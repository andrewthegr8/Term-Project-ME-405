STM32 Pin Configuration
=======================

This page documents the pin configuration used for the STM32L476RG
Nucleo-64 in this project.

:note::
    The **CPU pin** naming convention is used here, rather than the **Board Pin**
    convention.

====================================
Romi Sensor and Pinout Documentation
====================================

Color legend (used in tables and diagram)
-----------------------------------------

.. |LINE| raw:: html

   <span style="background-color:#C6EFCE; padding:1px 4px; border-radius:3px;">Line&nbsp;Sensor</span>

.. |ENC| raw:: html

   <span style="background-color:#FFD966; padding:1px 4px; border-radius:3px;">Encoder</span>

.. |IMU| raw:: html

   <span style="background-color:#9DC3E6; padding:1px 4px; border-radius:3px;">IMU</span>

.. |OBS| raw:: html

   <span style="background-color:#F4B183; padding:1px 4px; border-radius:3px;">Obstacle</span>

.. |BT| raw:: html

   <span style="background-color:#C9C9FF; padding:1px 4px; border-radius:3px;">Bluetooth</span>

.. |MOT| raw:: html

   <span style="background-color:#A9D18E; padding:1px 4px; border-radius:3px;">Motor</span>

.. |UI| raw:: html

   <span style="background-color:#D9D9D9; padding:1px 4px; border-radius:3px;">UI&nbsp;/&nbsp;Status</span>


Per-sensor pin tables
=====================

Line sensor array (QTR-style reflectance sensors)
-------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 18 22 48

   * - Pin
     - Channel
     - Mode / peripheral
     - Notes
   * - ``C5`` |LINE|
     - Line Sensor 14
     - Analog input (via ``LineSensor`` driver)
     - Right header; shared row with IMU SDA in the pinout sheet.
   * - ``B1`` |LINE|
     - Line Sensor 13
     - Analog input
     - Right header; same pad can be used as *Left Encoder Ch A* in hardware, but is used as line sensor in this firmware.
   * - ``C4`` |LINE|
     - Line Sensor 12
     - Analog input
     - Right header.
   * - ``A7`` |LINE|
     - Line Sensor 11
     - Analog input
     - Right header.
   * - ``A6`` |LINE|
     - Line Sensor 10
     - Analog input
     - Right header.
   * - ``A0`` |LINE|
     - Line Sensor 9
     - Analog input
     - Left header.
   * - ``A1`` |LINE|
     - Line Sensor 8
     - Analog input
     - Left header.
   * - ``A4`` |LINE|
     - Line Sensor 7
     - Analog input
     - Left header.
   * - ``B0`` |LINE|
     - Line Sensor 6
     - Analog input
     - Left header.
   * - ``C1`` |LINE|
     - Line Sensor 5
     - Analog input
     - Left header; pairs with ADC channel on ``A2`` in the hardware sheet.
   * - ``C0`` |LINE|
     - Line Sensor 4
     - Analog input
     - Left header; pairs with ADC channel on ``A3`` in the hardware sheet.
   * - ``C3`` |LINE|
     - Line Sensor 3
     - Analog input
     - Left header.
   * - ``C2`` |LINE|
     - Line Sensor 2
     - Analog input
     - Left header.

Line sensor drivers and reference lines
---------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 25 22 41

   * - Pin
     - Signal
     - Mode / peripheral
     - Notes
   * - ``H0`` |LINE|
     - Line Sensor Even Control
     - ``Pin.OUT_PP`` (push-pull output, pull-down)
     - ``evenctrl`` line for multiplexing or powering even-indexed sensors.
   * - ``H1`` |LINE|
     - Line Sensor Odd Control
     - ``Pin.OUT_PP`` (push-pull output, pull-down)
     - ``oddctrl`` line for multiplexing or powering odd-indexed sensors.
   * - ``A2`` |LINE|
     - Line Sensor ADC A
     - ADC input (to on-board ST-Link MCU)
     - Labeled *ADC (UART2 to ST-link MCU)* in the sheet, used with Line Sensor 5.
   * - ``A3`` |LINE|
     - Line Sensor ADC B
     - ADC input (to on-board ST-Link MCU)
     - Labeled *ADC (UART2 to ST-link MCU)*, used with Line Sensor 4.


Wheel encoders (quadrature)
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 20 26 42

   * - Pin
     - Channel
     - Mode / peripheral
     - Notes
   * - ``A8`` |ENC|
     - Left Encoder Ch A
     - ``Timer(1)`` encoder input (CH1)
     - Configured by :class:`Encoder` using ``tim1 = Timer(1, freq=10000)``.
   * - ``A9`` |ENC|
     - Left Encoder Ch B
     - ``Timer(1)`` encoder input (CH2)
     - Connected to the left wheel encoder.
   * - ``A15`` |ENC|
     - Right Encoder Ch A
     - ``Timer(2)`` encoder input (CH1, remapped)
     - Pin is placed in ``Pin.ALT`` mode before encoder setup to remap TIM2.
   * - ``B3`` |ENC|
     - Right Encoder Ch B
     - ``Timer(2)`` encoder input (CH2, remapped)
     - Works with ``A15`` for the right wheel encoder.


IMU (BNO055 over I²C)
---------------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Pin
     - Signal
     - Mode / peripheral
     - Notes
   * - ``B8`` |IMU|
     - IMU-SCL
     - ``I2C(1)`` SCL (alternate function)
     - Shared I²C bus for IMU; configured via ``i2c = I2C(1, I2C.CONTROLLER)``.
   * - ``B9`` |IMU|
     - IMU-SDA
     - ``I2C(1)`` SDA (alternate function)
     - Data line for the IMU.
   * - ``C9`` |IMU|
     - IMU-RST
     - ``Pin.OUT_PP`` (assumed)
     - Labeled in the pinout sheet as IMU reset; controlled in hardware, not toggled explicitly in ``main.py``.


Obstacle sensor
---------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Pin
     - Signal
     - Mode / peripheral
     - Notes
   * - ``B7`` |OBS|
     - Obstacle Sensor
     - ``Pin.IN`` with ``Pin.PULL_DOWN``
     - Digital wall / obstacle detector read in :func:`Pursuer_fun` (``obst_sens.value()``).


Bluetooth UART (HC-05 style link)
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Pin
     - Signal
     - Mode / peripheral
     - Notes
   * - ``C12`` |BT|
     - UART5-TX (Bluetooth)
     - ``UART(5)`` TX (alternate function)
     - Transmit line from Nucleo to Bluetooth module.
   * - ``D2`` |BT|
     - UART5-RX (Bluetooth)
     - ``UART(5)`` RX (alternate function)
     - Receive line from Bluetooth module to Nucleo.


Drive motors (H-bridge interface)
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 24 26 38

   * - Pin
     - Role
     - Mode / peripheral
     - Notes
   * - ``B4`` |MOT|
     - Left Motor IN1
     - GPIO output (set in :class:`Motor`)
     - Direction / drive input to left motor driver.
   * - ``B10`` |MOT|
     - Left Motor IN2 / DIR
     - GPIO output
     - Second direction input for left motor driver.
   * - ``C8`` |MOT|
     - Left Motor PWM
     - ``Timer(3)`` PWM output (CH1)
     - Speed control for left motor (``tim3 = Timer(3, freq=10000)``).
   * - ``B6`` |MOT|
     - Right Motor IN1
     - GPIO output
     - Direction / drive input to right motor driver.
   * - ``B11`` |MOT|
     - Right Motor IN2 / DIR
     - GPIO output
     - Second direction input for right motor driver.
   * - ``C7`` |MOT|
     - Right Motor PWM
     - ``Timer(4)`` PWM output (CH1)
     - Speed control for right motor (``tim4 = Timer(4, freq=10000)``).


User interface: button and LEDs
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Pin
     - Signal
     - Mode / peripheral
     - Notes
   * - ``C13`` |UI|
     - Blue button
     - ``Pin.IN`` with ``Pin.PULL_UP``
     - Used both for general interaction and line-sensor calibration.
   * - ``C6`` |UI| |LINE|
     - SENS_LED (Calibration / Line follower)
     - ``Pin.OUT_PP``
     - Status LED for line sensor activity and calibration.
   * - ``C10`` |UI|
     - RUN_LED
     - ``Pin.OUT_PP``
     - Toggled in :func:`SS_Simulator_fun` to show that the state-space simulator is running.
   * - ``C11`` |UI|
     - WALL_LED
     - ``Pin.OUT_PP``
     - Turned on in :func:`Pursuer_fun` when a wall is detected.


Physical pinout diagram (modeled after spreadsheet)
===================================================

Top-view of the Nucleo headers as used by this project.  
Each cell is annotated with the MCU pin and a colored tag for the sensor /
subsystem that primarily uses it.

.. table:: Romi Nucleo Header Pinout (simplified)
   :widths: 22 36 22

   +----------------------+--------------------------------------+----------------------+
   | Left header pin      | Function / Notes                     | Right header pin     |
   +======================+======================================+======================+
   | ``C10`` |UI|         | RUN_LED (state-sim activity LED)     | ``C9`` |IMU| IMU-RST  |
   +----------------------+--------------------------------------+----------------------+
   | ``C11`` |UI|         | WALL_LED (wall detected)             | ``C8`` |MOT| Left     |
   |                      |                                      | motor nSLP           |
   +----------------------+--------------------------------------+----------------------+
   | ``C12`` |BT|         | UART5-TX → Bluetooth module          | ``B8`` |IMU| IMU-SCL  |
   +----------------------+--------------------------------------+----------------------+
   | ``D2``  |BT|         | UART5-RX ← Bluetooth module          | ``B9`` |IMU| IMU-SDA  |
   +----------------------+--------------------------------------+----------------------+
   | ``C13`` |UI|         | Blue pushbutton (active low)         | ``C6`` |UI| SENS_LED  |
   +----------------------+--------------------------------------+----------------------+
   | ``B7``  |OBS|        | Obstacle sensor input                | ``C5`` |LINE| Line    |
   |                      |                                      | Sensor 14            |
   +----------------------+--------------------------------------+----------------------+
   | ``A15`` |ENC|        | Right Encoder Ch A (TIM2_CH1)        | ``A12`` (USB path,   |
   |                      |                                      | not used in code)    |
   +----------------------+--------------------------------------+----------------------+
   | ``B3``  |ENC|        | Right Encoder Ch B (TIM2_CH2)        | ``A11`` (USB path /  |
   |                      |                                      | alt Line 10)         |
   +----------------------+--------------------------------------+----------------------+
   | ``A8``  |ENC|        | Left Encoder Ch A (TIM1_CH1)         | ``B1`` |LINE| Line   |
   |                      |                                      | Sensor 13            |
   +----------------------+--------------------------------------+----------------------+
   | ``A9``  |ENC|        | Left Encoder Ch B (TIM1_CH2)         | ``B2`` (spare)       |
   +----------------------+--------------------------------------+----------------------+
   | ``B10`` |MOT|        | Left Motor DIR                       | ``B15`` (spare)      |
   +----------------------+--------------------------------------+----------------------+
   | ``B4``  |MOT|        | Left Motor PWM (TIM3_CH1)            | ``B14`` (spare)      |
   +----------------------+--------------------------------------+----------------------+
   | ``B6``  |MOT|        | Right Motor PWM / DIR                | ``B13`` (spare)      |
   +----------------------+--------------------------------------+----------------------+
   | ``H0``  |LINE|       | Line Sensor Even control             | ``A10`` (AGND row)   |
   +----------------------+--------------------------------------+----------------------+
   | ``H1``  |LINE|       | Line Sensor Odd control              | ``C4`` |LINE| Line   |
   |                      |                                      | Sensor 12            |
   +----------------------+--------------------------------------+----------------------+
   | ``C2``  |LINE|       | Line Sensor 2                        | ``A2`` |LINE| ADC A  |
   +----------------------+--------------------------------------+----------------------+
   | ``C3``  |LINE|       | Line Sensor 3                        | ``A3`` |LINE| ADC B  |
   +----------------------+--------------------------------------+----------------------+
   | ``C0``  |LINE|       | Line Sensor 4                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``C1``  |LINE|       | Line Sensor 5                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``B0``  |LINE|       | Line Sensor 6                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``A4``  |LINE|       | Line Sensor 7                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``A1``  |LINE|       | Line Sensor 8                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``A0``  |LINE|       | Line Sensor 9                        | (no paired header)   |
   +----------------------+--------------------------------------+----------------------+
   | ``A6``  |LINE|       | Line Sensor 10                       | (shares row with     |
   |                      |                                      | USB on ``A11``)      |
   +----------------------+--------------------------------------+----------------------+
   | ``A7``  |LINE|       | Line Sensor 11                       | (shares row with     |
   |                      |                                      | ``B12``)             |
   +----------------------+--------------------------------------+----------------------+

This table is intentionally simplified to highlight only the pins touched
by the firmware and the sensors; power pins, grounds, SWD, and the RTC
oscillator pins are omitted for clarity.
