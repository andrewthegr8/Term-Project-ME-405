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


Line Sensor Array
-------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 18 13 40

   * - Pin
     - Channel
     - Mode
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



Wheel Encoders (quadrature)
---------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 20 26 42

   * - Pin
     - Channel
     - Mode
     - Notes
   * - ``A8`` |ENC|
     - Left Encoder Ch A
     - TIM1_CH1
     - 
   * - ``A9`` |ENC|
     - Left Encoder Ch B
     - TIM1_CH2
     - 
   * - ``A15`` |ENC|
     - Right Encoder Ch A
     - TIM2_CH1
     - Alternate function mode ``AF1``.
   * - ``B3`` |ENC|
     - Right Encoder Ch B
     - TIM2_CH2
     - Alternate function mode ``AF1``.


IMU (I²C)
---------------------

.. list-table::
   :header-rows: 1
   :widths: 12 20 26 42

   * - Pin
     - Channel
     - Mode
     - Notes
   * - ``B8`` |IMU|
     - I2C clock
     -  ``I2C1 SCL``
     - Alternate function mode ``AF4``
   * - ``B9`` |IMU|
     - I2C data 
     - ``I2C1 SDA``
     - Alternate function mode ``AF4``
   * - ``C9`` |IMU|
     - IMU Reset
     - ``Pin.OUT_PP``
     - Optional hardware reset for the IMU; available on the header but not actively driven in the current firmware.

Obstacle Sensor
---------------

.. list-table::
   :header-rows: 1
   :widths: 12 22 26 40

   * - Pin
     - Signal
     - Mode
     - Notes
   * - ``B7`` |OBS|
     - Obstacle Sensor
     - ``Pin.IN`` with ``Pin.PULL_DOWN``
     - Simple limit switch. GND when pressed, pulled high otherwise.


Bluetooth (UART)
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 20 26 42

   * - Pin
     - Channel
     - Mode
     - Notes
   * - ``C12`` |BT|
     - UART TX
     - ``UART5_TX``
     - Alternate function mode ``AF8``
   * - ``D2`` |BT|
     - UART RX
     - ``UART5_RX``
     - Alternate function mode ``AF8``

.. Note::
  Ensure that the TX/RX lines are connected correctly between the
  STM32 and the Bluetooth module (TX to RX, RX to TX).


Drive Motors
---------------------------------

.. list-table::
   :header-rows: 1
   :widths: 12 20 26 42

   * - Pin
     - Channel
     - Mode
     - Notes
   * - ``B4`` |MOT|
     - Left motor effort (PWM)
     - ``TIM3_CH1``
     - 
   * - ``B10`` |MOT|
     - Left motor direction
     - ``Pin.OUT_PP``
     - 
   * - ``C8`` |MOT|
     - Left motor enable (nSLP)
     - ``Pin.OUT_PP``
     - 
   * - ``B6`` |MOT|
     - Right motor effort (PWM)
     - ``TIM4_CH1``
     - 
   * - ``B11`` |MOT|
     - Right motor direction
     - ``Pin.OUT_PP``
     - 
   * - ``C7`` |MOT|
     - Right motor enable (nSLP)
     - ``Pin.OUT_PP``
     - 



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
     - SENS_LED
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
-----------

Outer row is closest to the board edge, inner row is the row closer to the MCU.

.. list-table:: Left header (outer / inner rows)
   :header-rows: 1
   :widths: 18 12 12 18

   * - Left function label
     - Outer pin
     - Inner pin
     - Right function label

   * - RUN_LED
     - ``C10`` |UI|
     - ``C11`` |UI|
     - WALL_LED

   * - UART5–TX
     - ``C12`` |BT|
     - ``D2`` |BT|
     - UART5–RX

   * - VDD
     - ``VDD``
     - ``E5V``
     - 5V Rail

   * - BOOT0
     - ``BOOT0``
     - ``GND``
     - Ground

   * - NC
     - ``NC``
     - ``NC``
     - NC

   * - NC
     - ``NC``
     - ``IOREF``
     - IOREF

   * - SWD
     - ``A13``
     - ``RESET``
     - RESET

   * - SWD
     - ``A14``
     - ``3V3``
     - 3V3

   * - Right Encoder – Ch A
     - ``A15`` |ENC|
     - ``5V``
     - 5V

   * - GND
     - ``GND``
     - ``GND``
     - GND

   * - Obstacle Sensor
     - ``B7`` |OBS|
     - ``GND``
     - Ground

   * - Blue Button
     - ``C13`` |UI|
     - ``VIN``
     - VIN

   * - RTC
     - ``C14``
     - ``NC``
     - NC

   * - RTC
     - ``C15``
     - ``A0`` |LINE|
     - Line Sensor 9

   * - Line Sensor – Even
     - ``H0`` |LINE|
     - ``A1`` |LINE|
     - Line Sensor 8

   * - Line Sensor – Odd
     - ``H1`` |LINE|
     - ``A4`` |LINE|
     - Line Sensor 7

   * - VBAT
     - ``VBAT``
     - ``B0`` |LINE|
     - Line Sensor 6

   * - Line Sensors 2 / 5
     - ``C2`` |LINE|
     - ``C1`` |LINE|
     - Line Sensor 5

   * - Line Sensors 3 / 4
     - ``C3`` |LINE|
     - ``C0`` |LINE|
     - Line Sensor 4


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
