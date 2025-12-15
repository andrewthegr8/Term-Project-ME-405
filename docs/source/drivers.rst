Hardware Drivers
----------------------------------

The following classes are used for interfacing with hardware.
Their methods preform other useful functions as well.

* :class:`~me405.Motor.Motor` –
  DRV8838-compatible motor driver providing PWM effort control and
  direction/sleep pin management.

* :class:`~me405.Encoder.Encoder` –
  Quadrature encoder interface -  uses timer encoder mode to compute wheel
  position and velocity with overflow handling and moving-average smoothing
  for velocity.

* :class:`~me405.IMU.IMU` –
  I²C-based driver for the BNO055 9-DOF IMU, providing fused orientation and
  angular rate measurements.

* :class:`~me405.LineSensor.LineSensor` –
  Complete reflectance sensor array driver built from multiple
  :class:`IRSensor <~me405.LineSensor.LineSensor.IRSensor>` elements.

* :class:`~me405.LineSensor.LineSensor.IRSensor` –
  Internal class representing a single calibrated IR reflectance element,
  mapping ADC readings to normalized reflectance values.

* :class:`~me405.BTComm.BTComm` –
  UART-based Bluetooth communication driver used as a sensor/telemetry
  interface.

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