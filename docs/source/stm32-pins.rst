STM32 Pin Configuration
=======================

This page documents the pin configuration used for the STM32L476RG
Nucleo-64 in this project.

..note::
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

.. list-table::
   :header-rows: 1
   :widths: 12 18 22 48

   * - Pin
     - Channel
     - Mode / peripheral
     - Notes
   * - ``C5`` |LINE|
     - Line Sensor 14
     - Analog input
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
     - ``Pin.OUT_PP``
     - ``evenctrl`` line for multiplexing or powering even-indexed sensors.
   * - ``H1`` |LINE|
     - Line Sensor Odd Control
     - ``Pin.OUT_PP``
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


Physical pinout diagram (modeled after spreadsheet)
---------------------------------------------------

Top-view of the Nucleo Morpho headers as used by this project.

Each row corresponds to one “step down” the headers, starting at the
top (nearest the USB connector).  The table shows both rows for the left
header and both rows for the right header, along with the primary
function / sensor on each pin.

.. list-table:: Romi Nucleo Morpho headers (top view)
   :header-rows: 1
   :widths: 8 14 14 14 14 36

   * - Row
     - Left header (outer)
     - Left header (inner)
     - Right header (inner)
     - Right header (outer)
     - Functions / sensors (per pin)

   * - 1
     - ``C10`` |UI|
     - ``C11`` |UI|
     - ``C9`` |IMU|
     - ``C8`` |MOT|
     - ``C10`` RUN_LED (UI); ``C11`` WALL_LED (UI); ``C9`` IMU-RST; ``C8`` Left motor PWM / nSLP (used as PWM in code).

   * - 2
     - ``C12`` |BT|
     - ``D2`` |BT|
     - ``B8`` |IMU|
     - ``C6`` |UI| |LINE|
     - ``C12`` UART5-TX (Bluetooth); ``D2`` UART5-RX (Bluetooth); ``B8`` IMU-SCL; ``C6`` SENS_LED (calibration / line-sensor LED).

   * - 3
     - ``VDD``
     - ``E5V``
     - ``B9`` |IMU|
     - ``C5`` |LINE|
     - Power pins (``VDD``, ``E5V``); ``B9`` IMU-SDA; ``C5`` Line Sensor 14.

   * - 4
     - ``BOOT0``
     - ``GND``
     - ``AVDD``
     - ``U5V``
     - Boot and supply pins (no direct sensor use in this firmware).

   * - 5
     - ``NC``
     - ``NC``
     - ``GND``
     - ``NC``
     - Unused / ground pins.

   * - 6
     - ``NC``
     - ``IOREF``
     - ``A5``
     - ``A12``
     - On-board ADC / USB-communication pads (not used by the provided MicroPython code).

   * - 7
     - ``A13``
     - ``RESET``
     - ``A6`` |LINE|
     - ``A11``
     - ``A13`` SWD programming; ``RESET`` line; ``A6`` Line Sensor 10; ``A11`` USB communication through shoe (unused in code).

   * - 8
     - ``A14``
     - ``3V3``
     - ``A7`` |LINE|
     - ``B12``
     - ``A14`` SWD programming; ``3V3`` supply; ``A7`` Line Sensor 11; ``B12`` spare.

   * - 9
     - ``A15`` |ENC|
     - ``5V``
     - ``B6`` |MOT|
     - ``B11`` |MOT|
     - ``A15`` Right Encoder Ch A (TIM2_CH1); ``5V`` supply; ``B6`` Right Motor PWM; ``B11`` Right Motor DIR.

   * - 10
     - ``GND``
     - ``GND``
     - ``C7`` |MOT|
     - ``GND``
     - Ground pins; ``C7`` Right Motor nSLP / enable.

   * - 11
     - ``B7`` |OBS|
     - ``GND``
     - ``A9`` |ENC|
     - ``B2``
     - ``B7`` Obstacle sensor (digital input); ``A9`` Left Encoder Ch B (TIM1_CH2); ``B2`` spare.

   * - 12
     - ``C13`` |UI|
     - ``VIN``
     - ``A8`` |ENC|
     - ``B1`` |LINE|
     - ``C13`` Blue user button; ``VIN`` power in; ``A8`` Left Encoder Ch A (TIM1_CH1); ``B1`` Line Sensor 13.

   * - 13
     - ``C14``
     - ``NC``
     - ``B10`` |MOT|
     - ``B15``
     - ``C14`` 32 kHz RTC crystal; ``B10`` Left Motor DIR; ``B15`` spare.

   * - 14
     - ``C15``
     - ``A0`` |LINE|
     - ``B4`` |MOT|
     - ``B14``
     - ``C15`` 32 kHz RTC crystal; ``A0`` Line Sensor 9; ``B4`` Left Motor PWM (TIM3_CH1); ``B14`` spare.

   * - 15
     - ``H0`` |LINE|
     - ``A1`` |LINE|
     - ``B5``
     - ``B13``
     - ``H0`` Line Sensor Even control; ``A1`` Line Sensor 8; ``B5`` spare; ``B13`` spare.

   * - 16
     - ``H1`` |LINE|
     - ``A4`` |LINE|
     - ``B3`` |ENC|
     - ``AGND``
     - ``H1`` Line Sensor Odd control; ``A4`` Line Sensor 7; ``B3`` Right Encoder Ch B (TIM2_CH2); ``AGND`` analog ground.

   * - 17
     - ``VBAT``
     - ``B0`` |LINE|
     - ``A10``
     - ``C4`` |LINE|
     - ``VBAT`` battery input; ``B0`` Line Sensor 6; ``A10`` general I/O (not used in code); ``C4`` Line Sensor 12.

   * - 18
     - ``C2`` |LINE|
     - ``C1`` |LINE|
     - ``A2`` |LINE|
     - ``NC``
     - ``C2`` Line Sensor 2; ``C1`` Line Sensor 5; ``A2`` ADC (UART2 to ST-Link MCU, used with the line array); other pin NC.

   * - 19
     - ``C3`` |LINE|
     - ``C0`` |LINE|
     - ``A3`` |LINE|
     - ``NC``
     - ``C3`` Line Sensor 3; ``C0`` Line Sensor 4; ``A3`` ADC (UART2 to ST-Link MCU, used with the line array); other pin NC.