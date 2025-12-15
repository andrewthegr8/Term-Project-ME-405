STM32 Pin Configuration
=======================

This page documents the pin configuration used for the STM32L476RG
Nucleo-64 in this project.

.. note::
    The **CPU pin** naming convention is used here, rather than the **Board Pin**
    convention.


.. Color legend

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


Line sensor array (QTR-style reflectance sensors)
-------------------------------------------------

.. note::
  If only the Even LED control line is used and the odd line is left
  floating, all LEDs will be controlled.

.. list-table::
   :header-rows: 1
   :widths: 12 18 13 40

   * - Pin
     - Channel
     - Mode / peripheral
     - Notes
   * - ``C5`` |LINE|
     - Line Sensor 14
     - Analog input
     - Right header
   * - ``B1`` |LINE|
     - Line Sensor 13
     - Analog input
     - Right header
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
     - Left header
   * - ``C0`` |LINE|
     - Line Sensor 4
     - Analog input
     - Left header
   * - ``C3`` |LINE|
     - Line Sensor 3
     - Analog input
     - Left header.
   * - ``C2`` |LINE|
     - Line Sensor 2
     - Analog input
     - Left header.
   * - ``H0`` |LINE|
     - Line Sensor Even Control
     - ``Pin.OUT_PP``
     - Line for toggling even-indexed sensor LEDs.
   * - ``H1`` |LINE|
     - Line Sensor Odd Control
     - ``Pin.OUT_PP``
     - Line for toggling odd-indexed sensor LEDs.

.. note::
  If only the Even LED control line is used and the odd line is left
  floating, all LEDs will be controlled. This is how the sensor was used
  in this project.



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
     - Timer encoder input (TIM1_CH1)
     - Configured by :class:`Encoder` using ``Timer(1, freq=10000)``.
   * - ``A9`` |ENC|
     - Left Encoder Ch B
     - Timer encoder input (TIM1_CH2)
     - Connected to the left wheel encoder.
   * - ``A15`` |ENC|
     - Right Encoder Ch A
     - Timer encoder input (TIM2_CH1, remapped)
     - Pin is put in alternate (AF) mode before encoder setup to remap TIM2.
   * - ``B3`` |ENC|
     - Right Encoder Ch B
     - Timer encoder input (TIM2_CH2, remapped)
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
     - Shared I²C bus for IMU; configured via ``I2C(1, I2C.CONTROLLER)``.
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
     - Digital wall / obstacle detector read via ``obst_sens.value()``.


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
     - GPIO output
     - Direction / drive input to left motor driver.
   * - ``B10`` |MOT|
     - Left Motor IN2 / DIR
     - GPIO output
     - Second direction input for left motor driver.
   * - ``C8`` |MOT|
     - Left Motor PWM
     - Timer PWM output (TIM3_CH1)
     - Speed control for left motor (``Timer(3, freq=10000)``).
   * - ``B6`` |MOT|
     - Right Motor IN1 / PWM
     - GPIO / timer output
     - Direction and/or PWM drive input to right motor driver, paired with ``B11``.
   * - ``B11`` |MOT|
     - Right Motor DIR
     - GPIO output
     - Second direction input for right motor driver.
   * - ``C7`` |MOT|
     - Right Motor PWM
     - Timer PWM output (TIM4_CH1)
     - Speed control for right motor (``Timer(4, freq=10000)``).


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
     - Toggled in the state-space simulator to show that it is running.
   * - ``C11`` |UI|
     - WALL_LED
     - ``Pin.OUT_PP``
     - Turned on when a wall or obstacle is detected.


Physical pinout diagrams
---------------------------------------------------

Top-view of the Nucleo Morpho headers as used by this project.

Each row corresponds to one “step down” the headers, starting at the
top (nearest the USB connector).

Left header
^^^^^^^^^^^

Outer row is closest to the board edge, inner row is the row closer
to the MCU.

.. list-table:: Left header (outer / inner rows)
   :header-rows: 1
   :widths: 40 15 15

   * - Function / sensor (left of header)
     - Outer pin
     - Inner pin

   * - Status LEDs (RUN_LED, WALL_LED)
     - ``C10`` |UI|
     - ``C11`` |UI|

   * - UART5 – Bluetooth link (TX/RX)
     - ``C12`` |BT|
     - ``D2`` |BT|

   * - Board power rails
     - ``VDD``
     - ``E5V``

   * - Boot configuration and ground
     - ``BOOT0``
     - ``GND``

   * - Not connected
     - ``NC``
     - ``NC``

   * - IO reference (unused by code)
     - ``NC``
     - ``IOREF``

   * - SWD programming and reset
     - ``A13``
     - ``RESET``

   * - SWD programming / 3.3 V supply
     - ``A14``
     - ``3V3``

   * - Right Encoder Ch A (TIM2_CH1) + 5 V
     - ``A15`` |ENC|
     - ``5V``

   * - Ground row
     - ``GND``
     - ``GND``

   * - Obstacle sensor and ground
     - ``B7`` |OBS|
     - ``GND``

   * - User button and VIN power in
     - ``C13`` |UI|
     - ``VIN``

   * - RTC 32 kHz crystal (hardware only)
     - ``C14``
     - ``NC``

   * - RTC 32 kHz crystal and Line Sensor 9
     - ``C15``
     - ``A0`` |LINE|

   * - Line Sensor Even control / Line Sensor 8
     - ``H0`` |LINE|
     - ``A1`` |LINE|

   * - Line Sensor Odd control / Line Sensor 7
     - ``H1`` |LINE|
     - ``A4`` |LINE|

   * - VBAT and Line Sensor 6
     - ``VBAT``
     - ``B0`` |LINE|

   * - Line Sensors 2 and 5
     - ``C2`` |LINE|
     - ``C1`` |LINE|

   * - Line Sensors 3 and 4
     - ``C3`` |LINE|
     - ``C0`` |LINE|


Right header
^^^^^^^^^^^^

Top view; inner row is the one nearer the MCU, outer row is nearer the board
edge.

.. list-table:: Right header (inner / outer rows)
   :header-rows: 1
   :widths: 15 15 40

   * - Inner pin
     - Outer pin
     - Function / sensor (right of header)

   * - ``C9`` |IMU|
     - ``C8`` |MOT|
     - ``C9`` IMU-RST; ``C8`` Left motor enable / PWM (nSLP / PWM, used as motor control).

   * - ``B8`` |IMU|
     - ``C6`` |UI| |LINE|
     - ``B8`` IMU-SCL; ``C6`` SENS_LED (line-sensor / calibration LED).

   * - ``B9`` |IMU|
     - ``C5`` |LINE|
     - ``B9`` IMU-SDA; ``C5`` Line Sensor 14.

   * - ``AVDD``
     - ``U5V``
     - Analog VDD and USB 5 V (no direct sensor in this firmware).

   * - ``GND``
     - ``NC``
     - Ground / not connected.

   * - ``A5``
     - ``A12``
     - On-board ADC / USB communication through shoe (unused in the MicroPython code).

   * - ``A6`` |LINE|
     - ``A11``
     - ``A6`` Line Sensor 10; ``A11`` USB communication through shoe (unused by code).

   * - ``A7`` |LINE|
     - ``B12``
     - ``A7`` Line Sensor 11; ``B12`` spare.

   * - ``B6`` |MOT|
     - ``B11`` |MOT|
     - Right motor drive: ``B6`` PWM / IN1; ``B11`` DIR / IN2.

   * - ``C7`` |MOT|
     - ``GND``
     - ``C7`` Right Motor nSLP / enable; outer pin ground.

   * - ``A9`` |ENC|
     - ``B2``
     - ``A9`` Left Encoder Ch B (TIM1_CH2); ``B2`` spare.

   * - ``A8`` |ENC|
     - ``B1`` |LINE|
     - ``A8`` Left Encoder Ch A (TIM1_CH1); ``B1`` Line Sensor 13.

   * - ``B10`` |MOT|
     - ``B15``
     - ``B10`` Left Motor DIR; ``B15`` spare.

   * - ``B4`` |MOT|
     - ``B14``
     - ``B4`` Left Motor PWM (TIM3_CH1); ``B14`` spare.

   * - ``B5``
     - ``B13``
     - Both pins currently spare in the code.

   * - ``B3`` |ENC|
     - ``AGND``
     - ``B3`` Right Encoder Ch B (TIM2_CH2); ``AGND`` analog ground.

   * - ``A10``
     - ``C4`` |LINE|
     - ``A10`` general I/O (unused in code); ``C4`` Line Sensor 12.

   * - ``A2`` |LINE|
     - ``NC``
     - ``A2`` ADC (UART2 to ST-Link MCU, used with line-sensor group); outer pin NC.

   * - ``A3`` |LINE|
     - ``NC``
     - ``A3`` ADC (UART2 to ST-Link MCU, used with line-sensor group); outer pin NC.
