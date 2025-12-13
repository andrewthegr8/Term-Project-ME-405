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

NEED OVERALL DIAGRAM

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

PI speed controller
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.PIController
   :members:
   :undoc-members:
   :show-inheritance:

State-space model
~~~~~~~~~~~~~~~~~

.. automodule:: me405.SSModel
   :members:
   :undoc-members:
   :show-inheritance:

Pure-pursuit path tracker
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.ThePursuer
   :members:
   :undoc-members:
   :show-inheritance:

Task scheduler
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.cotask
   :members:
   :undoc-members:
   :show-inheritance:

Shared data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.task_share
   :members:
   :undoc-members:
   :show-inheritance:

Hardware Drivers
----------------------------------
The following classes are used for interfacing with hardware.

Bluetooth communication
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.BTComm
   :members:
   :undoc-members:
   :show-inheritance:

IMU (BNO055) driver
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.IMU
   :members:
   :undoc-members:
   :show-inheritance:

Line sensor array
~~~~~~~~~~~~~~~~~

.. automodule:: me405.LineSensor
   :members:
   :undoc-members:
   :show-inheritance:


Motor driver
~~~~~~~~~~~~~~~~~

.. automodule:: me405.Motor
   :members:
   :undoc-members:
   :show-inheritance:

Encoder
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.Encoder
   :members:
   :undoc-members:
   :show-inheritance: