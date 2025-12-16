Important Notes
==========================
This page contains important/interesting notes about the project
that didn't fit naturally into other sections of the documentation.

Pull Down Resistor for Motor Controller
------------------------------------------

When the STM32 initializes, for a brief moment before the code
configures the GPIO pins, the motor controller input and enable pins
can float. Combined with pull-up resistor on random lines courtesy
of the Shoe of Brian, this can cause motors to behave erratically on
startup. This was the case with the left motor, which would sometimes
spin up unexpectedly on boot.
To fix this, a pull-down resistor was added to the left motor controller enable
pin to ensure it stays low until the code configures it as an output.

LED Interpretation
--------------------------

This Romi had a few LEDs installed to provide information 
about sensor and code preformance. These are referenced elsewhere in this documentation,
but here is a summary of what each LED indicates:

* Red LED: Toggled by the :func:`ssmodel_fun` every time the state space model updates.
  This indicates that the main control loop is running.
* Green LED: Indicates when the robot is looking for the wall and
  has registered a hit on the bump sensor.
  It is controlled by the :func:`thepursuer_fun` task
* Blue LED: Indicates when the robot is in line following mode.
  It is controlled by the :func:`linefollow_fun` task.

.. figure:: /images/romiled.jpg
   :alt: Romi with LEDs on
   :align: center

   Romi with Blue (line follow) and Red (SS model running) LEDs on.

Lipo Batteries versus Alkaline Batteries
------------------------------------------  

The Romi chassis is designed to accept 6 AA batteries, which
are typically alkaline. However, for this project, LiPo batteries
in a AA form factor were used instead.

But, you might ask, don't LiPo cells have a nominal voltage of 3.7V,
while alkaline AA batteries have a nominal voltage of around 1.5V?

This is true, but the LiPo batteries used here have built-in voltage
regulators that step down the voltage to a nominal 1.5V, making them
compatible with the Romi chassis.

The presence of a 3.7V cell with a voltage regulator provided several advantages:

* **Consistent Voltage Output**: Alkaline batteries drop in voltage as they discharge,
  leading to inconsistent motor performance. The voltage regulator in the LiPo batteries
  ensured a stable voltage output until the battery was nearly depleted.
* **Higher Nominal Voltage**: NiMH rechargable batteries (used by many groups in
  the class) provide around a fairly steady 1.2V each, for a total of 7.2V with 6 cells.
  Using LiPo batteries allowed a nominal voltage of 9V (6 x 1.5V), allowing for faster motor speeds,
  while retaining rechagability and consistent voltage output.

.. figure:: /images/batterygraph.jpg
   :alt: 
   :align: center
   :width: 70%
   
   Source: `<https://ripitapart.com/wp-content/uploads/2013/11/705255222_102.jpg>`_

The above graph compares the voltage discharge curves of
alkaline, NiMH, and LiPo batteries and demonstrates the aforementioned
properites that make LiPo batteries advatageous for this project.

.. note::
    The State Space Observer takes motor input voltages as an input.
    Were batteries with inconsistent voltage outputs used, Additionally
    circuitry and programming would have been required to measure
    battery voltage in real-time to ensure accurate state estimation.

``Queue`` Improvments
----------------------------------
 
 The ``task_share`` class used for inter-task communication was
 modified from its original form to include a few new methods that
 improved usability:

1.  :meth:`~me405.task_share.Queue.view` allows a task to view the most recent
    value without removing it from the queue. This was incredibly useful as many values
    are streamed to the `Talker_fun`` task for telemetry, but still need to be
    available for other tasks to read. Enabling these tasks to view the value
    without removing it from the queue eliminates the need for duplicate queues
    for each value.
2.  :meth:`~me405.task_share.Queue.many` allows a task to see if there are
    *at least 2* items in a queue. This was implemented so that the ``Talker_fun``
    task didn't drain queues faster than other tasks could produce data. Otherwise,
    tasks that depend on reading from these queues would fail.
3.  ``ValueError`` exception added to handle cases where a task attempts to read
    from an empty queue. This was useful for debugging. Otherwise, the task would block
    indefinitely, making it hard to determine the source of the issue.

Known Issues
--------------------------

This project is still a work in progress, and there are a few known issues
that should be addressed to further improve performance:

1.  **Motor Controller Tuning** - Due to the fast paced nature of this project
    The PI controller gains for the motor controller were not fully optimized.
    Further tuning could improve speed regulation and responsiveness.
2.  **Path Planning Optimization** - The current path planning algorithm
    is functional but could be optimized for smoother trajectories and
    faster run times.
3.  **Code Optimization** - As previously mentioned, the State Space Observer
    depends on the code running fast enough to produce accurate estimates.
    Further optimizations to the code and the use of measures like pre-compiling
    could improve the preformance of the observer.
4.  **State Space Model Tuning** - The state space model motor parameters
    were derived from theoretical calculations and basic testing.
    More extensive system identification and tuning could enhance
    estimation accuracy.
5.  **Wheel Slip Detection** - The current implementation does not account for
    wheel slip, which leads to inaccuracies in state estimation. To avoi this issues
    The current code limits Romi's maximum acceleration and deceleration rate.
    Implementing slip detection and compensation could allow the Romi to traverse 
    the course more aggressively.