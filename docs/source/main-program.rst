Main Program
--------------------
As previously mentioned, the software architecture consists of several cooperatively run tasks,
all contained in ``main.py``. This page has information about how the tasks communication,
as well as detailed documentation for ``main.py``.

.. note::
    For some of the tasks, the functionaility is bundled into a helper class,
    and the task does little more than run a method of one of the helper classes.

Task List
~~~~~~~~~~~~~~~~~

The following cooperative tasks and helper function are defined in
:mod:`me405.main`:

* :func:`me405.main.Talker_fun` –
  Handles Bluetooth communication: receives text commands, updates shares, and
  streams telemetry packets over the serial link.

* :func:`me405.main.IMU_Interface_fun` –
  Periodically reads the BNO055 IMU and pushes heading (and optional yaw rate)
  measurements into shared queues.

* :func:`me405.main.SS_Simulator_fun` –
  Runs the state-space model to estimate robot position, heading, and related
  states from encoder and IMU data, then logs them to queues.

* :func:`me405.main.LineFollow_fun` –
  Uses the reflectance sensor array to follow the black line and computes a
  lateral offset command for the controller.

* :func:`me405.main.Pursuer_fun` –
  Implements pure-pursuit path following, generating speed and turning
  commands based on the estimated pose and obstacle flags.

* :func:`me405.main.Controller_fun` –
  Performs PI wheel-speed control, reading setpoints and encoder feedback to
  compute motor efforts and log wheel data.

* :func:`me405.main.GarbageCollector_fun` –
  Low-priority background task that periodically runs :func:`gc.collect` to
  manage heap usage on the microcontroller.

* :func:`me405.main.Cali_test` –
  Blocking calibration routine that guides the user through black/white
  calibration of the line sensor using the pushbutton and status LED.


Task diagram
~~~~~~~~~~~~~~~~

The diagram below shows how the cooperative tasks interact with drivers
and pass data via shares and queues. Each tasks period (T) in ms and priority
(P) is shown as well

.. graphviz::
   :align: center

   digraph firmware_arch {
     rankdir=LR;
     fontsize=10;
     node [shape=box, style="rounded,filled", fillcolor="#f8f8f8", fontname="Helvetica"];

     // =========================
     // Task nodes (with P/T)
     // =========================
     subgraph cluster_tasks {
       label = "Tasks (priority P, period T)";
       style = "rounded";
       color = "#cccccc";

       Talker       [label="Talker\nP=1, T=10 ms"];
       IMU_Interface[label="IMU_Interface\nP=4, T=30 ms"];
       Controller   [label="Controller\nP=5, T=30 ms"];
       LineFollow   [label="LineFollow\nP=2, T=30 ms"];
       Pursuer      [label="Pursuer\nP=3, T=30 ms"];
       SS_Simulator [label="SS_Simulator\nP=3, T=30 ms"];
       Garbage      [label="GarbageCollector\nP=0, T=30 ms"];
     }

     // =========================
     // Drivers / hardware
     // =========================
     subgraph cluster_drivers {
       label = "Drivers / Hardware";
       style = "rounded";
       color = "#cccccc";

       MotorDrv   [label="Motors\n(Motor left/right)"];
       EncoderDrv [label="Encoders\n(Encoder left/right)"];
       IMUDrv     [label="IMU\n(BNO055)"];
       LineSens   [label="LineSensor\n(array)"];
       BTDrv      [label="BTComm\n(UART)"];
       ObstSens   [label="Obstacle sensor"];
     }

     // Common edge style
     edge [fontname="Helvetica", fontsize=9];

     // =========================
     // Task <-> Driver interactions
     // =========================

     // Talker <-> Bluetooth
     BTDrv   -> Talker      [label="rx bytes"];
     Talker  -> BTDrv       [label="telemetry packets"];

     // IMU interface
     IMUDrv      -> IMU_Interface [label="sensor data"];
     IMU_Interface -> SS_Simulator [label="Eul_head, yaw_rate\n(Queues)"];

     // Controller <-> motors/encoders
     EncoderDrv  -> Controller    [label="wheel pos/vel\n(Encoder APIs)"];
     Controller  -> MotorDrv      [label="set_effort()"];

     // Line sensor
     LineSens    -> LineFollow    [label="line readings"];

     // Obstacle sensor
     ObstSens    -> Pursuer       [label="wall hit?"];

     // =========================
     // Shares / queues as labeled data flows
     // =========================

     // Speed setpoint share
     Talker      -> Controller    [label="velo_set (Share)\n$SPD commands"];
     Pursuer     -> Controller    [label="velo_set (Share)"];
     Controller  -> Talker        [label="cmd_L/R (Queues)\nfor telemetry"];

     // Line-follow & pursuit offset
     LineFollow  -> Controller    [label="offset (Share)\nline follower"];
     Pursuer     -> Controller    [label="offset (Share)\npure pursuit"];

     // Line-follower enable flag
     Pursuer     -> LineFollow    [label="lf_stop (Share)\nstop line follow"];

     // IMU disable flag to SS model
     Pursuer     -> SS_Simulator  [label="imu_off (Share)\nIMU disable flag"];

     // Wheel logs from controller
     Controller  -> Talker        [label="time_L/R, pos_L/R,\nvelo_L/R (Queues)"];
     Controller  -> SS_Simulator  [label="pos_L/R, velo_L/R,\ncmd_L/R (Queues)"];

     // IMU heading / yaw to others
     IMU_Interface -> Talker      [label="Eul_head,\nyaw_rate (Queues)"];

     // State-space outputs
     SS_Simulator -> Talker       [label="X_pos, Y_pos,\np_v_L/R, p_head,\np_yaw, p_pos_L/R (Queues)"];
     SS_Simulator -> LineFollow   [label="X_pos (Queue)"];
     SS_Simulator -> Pursuer      [label="X_pos, Y_pos,\np_head (Queues)"];

     // Pursuer adjusts commands
     Pursuer     -> Talker        [label="indirectly affects\ntelemetry via\nvelo_set/offset"];

     // Garbage collector (background)
     Garbage     -> Garbage       [style=dotted, label="gc.collect()"];
   }


Inter-task communication variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following table contains additional information about the 
inter-task communication variables shown in the diagram. Variables 
labeled (predicted) contain data that came from the state space observer
rather than hardware.

.. list-table::
   :header-rows: 1
   :widths: 20 10 15 10 50

   * - **Name**
     - **Kind**
     - **Data Type**
     - **Size**
     - **Description**

   * - velo_set
     - Share
     - f (float)
     - —
     - Motor speed setpoint

   * - imu_off
     - Share
     - I (uint16)
     - —
     - IMU disable flag

   * - offset
     - Share
     - f (float)
     - —
     - Motor setpoint adjustment (rotational velocity setpoint)

   * - lf_stop
     - Share
     - I (uint16)
     - —
     - Line-follow stop flag

   * - cmd_L
     - Queue
     - f (float)
     - 10
     - Left motor command signal

   * - cmd_R
     - Queue
     - f (float)
     - 10
     - Right motor command signal

   * - time_L
     - Queue
     - I (uint16)
     - 20
     - Left motor timestamp

   * - pos_L
     - Queue
     - f (float)
     - 20
     - Left wheel path length

   * - velo_L
     - Queue
     - f (float)
     - 20
     - Left wheel velocity

   * - time_R
     - Queue
     - I (uint16)
     - 20
     - Right wheel timestamp

   * - pos_R
     - Queue
     - f (float)
     - 20
     - Right wheel path length

   * - velo_R
     - Queue
     - f (float)
     - 20
     - Right wheel velocity

   * - Eul_head
     - Queue
     - f (float)
     - 20
     - Euler heading (radians) from IMU

   * - yaw_rate
     - Queue
     - f (float)
     - 20
     - Yaw rate (radians/s) from IMU

   * - X_pos
     - Queue
     - f (float)
     - 10
     - Absolute X position (predicted)

   * - Y_pos
     - Queue
     - f (float)
     - 10
     - Absolute Y position (predicted)

   * - p_v_R
     - Queue
     - f (float)
     - 10
     - Right wheel velocity (predicted)

   * - p_v_L
     - Queue
     - f (float)
     - 10
     - Left wheel velocity (predicted)

   * - p_head
     - Queue
     - f (float)
     - 10
     - Heading (radians) (predicted)

   * - p_yaw
     - Queue
     - f (float)
     - 10
     - Yaw rate (radians/s) (predicted)

   * - p_pos_L
     - Queue
     - f (float)
     - 10
     - Left wheel path length (predicted)

   * - p_pos_R
     - Queue
     - f (float)
     - 10
     - Right wheel path length (predicted)


Main Script
--------------
All task generator functions are contained in ``main.py``.

.. automodule:: me405.main
   :members:
   :undoc-members:
   :show-inheritance:

