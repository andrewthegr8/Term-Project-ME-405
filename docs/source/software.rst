Software
==========

The program design for this project consists of several tasks which 
are run by a prioritized scheduler (:mod:`me405.cotask`). Each task is a generator function,
and many are configured as finite state machines. Tasks communicate using 
``share`` and ``queue`` objects from :mod:`me405.task_share`, which, along with the scheduler, are 
adapted from code developed by Dr. John Ridgley. The original code for the
scheduler and inter-task communication objects
can be found in the `ME405-Support <https://github.com/spluttflob/ME405-Support>`_ repository. 

This diagram shows all the tasks and their scheduled frequency, as well as
what shares and queues the tasks interface with. See :ref:`_main-program`
for the details of each task.

The diagram below shows how the cooperative tasks interact with drivers
and pass data via shares and queues.

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


The following table contains additional information about the 
inter-task communication variables shown in the diagram. Variables 
labeled (predicted) contian datat that came from the state space observer
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





.. _main-program:

Main Program
--------------
All task generator functions are contained in 'main.py'.
.. automodule:: me405.main
   :members:
   :undoc-members:
   :show-inheritance:


Helper Classes
---------------------
The following classes are initialized and passed to tasks, 
except, of course, :mod:`me405.cotask` which schedules and runs the tasks.

PI Speed Controller
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.PIController
   :members:
   :undoc-members:
   :show-inheritance:

State-Space Model
~~~~~~~~~~~~~~~~~

.. automodule:: me405.SSModel
   :members:
   :undoc-members:
   :show-inheritance:

Point Targeting Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.ThePursuer
   :members:
   :undoc-members:
   :show-inheritance:

Task Scheduler
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.cotask
   :members:
   :undoc-members:
   :show-inheritance:

Shared Data Structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.task_share
   :members:
   :undoc-members:
   :show-inheritance:

Hardware Drivers
----------------------------------
The following classes are used for interfacing with hardware.

Bluetooth Communication Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.BTComm
   :members:
   :undoc-members:
   :show-inheritance:

IMU (BNO055) Driver
~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.IMU
   :members:
   :undoc-members:
   :show-inheritance:

Line Sensor Array Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.LineSensor
   :members:
   :undoc-members:
   :show-inheritance:


Motor Driver
~~~~~~~~~~~~~~~~~

.. automodule:: me405.Motor
   :members:
   :undoc-members:
   :show-inheritance:

Encoder Driver
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.Encoder
   :members:
   :undoc-members:
   :show-inheritance: