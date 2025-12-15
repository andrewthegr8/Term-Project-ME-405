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
To fix this, a pull-down resitor was added to the left motor controller enable
pin to ensure it stays low until the code configures it as an output.

PIC OF PULL DOWN Resistor

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

PIC OF LEDS

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
 **Higher Nominal Voltage**: NiMH rechargable batteries (used by many groups in
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

:class:`task_share` Improvments
----------------------------------

* View get many methods to task_share class addition
Known Issues
--------------------------

* Motor controllers tuned better
* IMU sometimes jump on init