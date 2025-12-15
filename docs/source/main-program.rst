Main Program
--------------------
As previously mentioned, the software architecture consists of several cooperatively run tasks,
all contained in ``main.py``. This page has information about how the tasks communication,
as well as detailed documentation for ``main.py``.

.. note::
    For some of the tasks, much of the functionality is bundled into a helper class,
    and the task does little more than run a method of one of the helper classes.

Task List
~~~~~~~~~~~~~~~~~

The following cooperative tasks and helper function are defined in
:mod:`~me405.main`:

* :func:`~me405.main.Talker_fun` –
  Handles Bluetooth communication: receives text commands, updates shares, and
  streams telemetry packets over the serial link.

* :func:`~me405.main.IMU_Interface_fun` –
  Periodically reads the BNO055 IMU and pushes heading (and optionally yaw rate)
  measurements into shared queues.

* :func:`~me405.main.SS_Simulator_fun` –
  Runs the state-space model to estimate robot position, heading, and related
  states using feedback from encoder and IMU data, then logs them to queues.

* :func:`~me405.main.LineFollow_fun` –
  Uses the reflectance sensor array to follow a black line. Computes a
  lateral offset command for the controller.

* :func:`~me405.main.Pursuer_fun` –
  Implements point targeting path following, generating speed and turning
  commands based on the estimated pose.

* :func:`~me405.main.Controller_fun` –
  Performs PI wheel-speed control. Reading setpoints and encoder feedback to
  compute and set motor efforts. Logs wheel position and velocity data.

* :func:`~me405.main.GarbageCollector_fun` –
  Low-priority background task that periodically runs :func:`gc.collect` to
  manage heap usage on the microcontroller.

Task diagram
~~~~~~~~~~~~~~~~

The diagram below shows how the cooperative tasks interact
and pass data via shares and queues. Each tasks' period (T) in ms
and priority (P) is shown as well.

.. graphviz::
   :align: center
   :class: zoomable-graph

   digraph firmware_arch {
     rankdir=LR;

     // Overall font / spacing
     fontsize=16;
     nodesep="0.6";
     ranksep="1.0 equally";

     node [
       shape=box,
       style="rounded,filled",
       fillcolor="#f8f8f8",
       fontname="Helvetica",
       fontsize=16
     ];

     edge [
       fontname="Helvetica",
       fontsize=12
     ];

     // =========================
     // Task nodes (Garbage removed)
     // =========================
     subgraph cluster_tasks {
       label = "Tasks (priority P, period T)";
       style = "rounded";
       color = "#cccccc";

       Talker        [label="Talker\nP=1, T=10 ms"];
       IMU_Interface [label="IMU_Interface\nP=4, T=30 ms"];
       Controller    [label="Controller\nP=5, T=30 ms"];
       LineFollow    [label="LineFollow\nP=2, T=30 ms"];
       Pursuer       [label="Pursuer\nP=3, T=30 ms"];
       SS_Simulator  [label="SS_Simulator\nP=3, T=30 ms"];
     }

     // =========================
     // Column layout (reduces edge crossing)
     // =========================
     { rank = same; IMU_Interface; Talker; }
     { rank = same; SS_Simulator; Controller; }
     { rank = same; Pursuer; LineFollow; }

     // =========================
     // Shares / queues between tasks
     // =========================

     // Speed commands
     Talker      -> Controller    [label="velo_set (Share)\n$SPD commands"];
     Pursuer     -> Controller    [label="velo_set (Share)"];
     Controller  -> Talker        [label="cmd_L/R (Queues)\ntelemetry"];

     // Offsets
     LineFollow  -> Controller    [label="offset (Share)\nline follower"];
     Pursuer     -> Controller    [label="offset (Share)\npure pursuit"];

     // Line follower enable/disable
     Pursuer     -> LineFollow    [label="lf_stop (Share)"];

     // IMU to simulator & talker
     IMU_Interface -> SS_Simulator [label="Eul_head, yaw_rate\n(Queues)"];
     IMU_Interface -> Talker       [label="Eul_head,\nyaw_rate (Queues)"];

     // Controller → others
     Controller  -> Talker        [label="time_L/R, pos_L/R,\nvelo_L/R (Queues)"];
     Controller  -> SS_Simulator  [label="pos_L/R, velo_L/R,\ncmd_L/R (Queues)"];

     // State-space simulator outputs
     SS_Simulator -> Talker       [label="X_pos, Y_pos,\np_v_L/R, p_head,\np_yaw, p_pos_L/R (Queues)"];
     SS_Simulator -> LineFollow   [label="X_pos (Queue)"];
     SS_Simulator -> Pursuer      [label="X_pos, Y_pos,\np_head (Queues)"];

     // Pursuer adjusting behavior
     Pursuer     -> Talker        [label="indirect effect via\nvelo_set/offset"];
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
~~~~~~~~~~~~~~~~~~~~
All task generator functions are contained in ``main.py``. The
documentation for this script is shown below.

.. automodule:: me405.main
   :members:
   :undoc-members:
   :show-inheritance:

