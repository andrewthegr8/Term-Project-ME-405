Hardware Drivers
----------------------------------

The following classes are used for interfacing with hardware.
Their methods preform other useful functions as well.

* :class:`Motor.Motor` –
  DRV8838-compatible motor driver providing PWM effort control and
  direction/sleep pin management.

* :class:`Encoder.Encoder` –
  Quadrature encoder interface -  uses timer encoder mode to compute wheel
  position and velocity with overflow handling and moving-average smoothing
  for velocity.

* :class:`IMU.IMU` –
  I²C-based driver for the BNO055 9-DOF IMU, providing fused orientation and
  angular rate measurements.

* :class:`LineSensor.LineSensor` –
  Complete reflectance sensor array driver built from multiple
  :class:`IRSensor <LineSensor.LineSensor.IRSensor>` elements.

* :class:`LineSensor.LineSensor.IRSensor` –
  Internal class representing a single calibrated IR reflectance element,
  mapping ADC readings to normalized reflectance values.

* :class:`BTComm.BTComm` –
  UART-based Bluetooth communication driver used as a sensor/telemetry
  interface.

Bluetooth Communication Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: BTComm
   :members:
   :undoc-members:
   :show-inheritance:

IMU (BNO055) Driver
~~~~~~~~~~~~~~~~~~~~

.. automodule:: IMU
   :members:
   :undoc-members:
   :show-inheritance:

Line Sensor Array Driver
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: LineSensor
   :members:
   :undoc-members:
   :show-inheritance:


Motor Driver
~~~~~~~~~~~~~~~~~

.. automodule:: Motor
   :members:
   :undoc-members:
   :show-inheritance:

Encoder Driver
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: Encoder
   :members:
   :undoc-members:
   :show-inheritance: