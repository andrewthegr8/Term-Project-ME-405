STM32 Pin Configuration
=======================

This page documents the pin configuration used for the STM32L476RG
Nucleo-64 in this project.

.. note::
    The **CPU Pin** naming convention is used here, rather than the **Board Pin**
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


Physical Pinout Diagrams
---------------------------------------------------

Top-view of the Nucleo Morpho headers as used by this project.

Each row corresponds to one “step down” the headers, starting at the
top (nearest the USB connector).

.. note::
    The USB port and the ST-link MCU are pointed away from the user in
    this left/right orientation.

Left Header
~~~~~~~~~~~~~~~~~~~~

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

   * - UART5 - TX (Bluetooth)
     - ``C12`` |BT|
     - ``D2`` |BT|
     - UART5 - RX (Bluetooth)

   * - 
     - ``VDD``
     - ``E5V``
     - 

   * - 
     - ``BOOT0``
     - ``GND``
     - 

   * - 
     - ``NC``
     - ``NC``
     - 

   * - 
     - ``NC``
     - ``IOREF``
     - 

   * - SWD programming
     - ``A13``
     - ``RESET``
     - 

   * - SWD programming
     - ``A14``
     - ``3V3``
     - 

   * - Right Encoder – Ch A
     - ``A15`` |ENC|
     - ``5V``
     - 

   * - 
     - ``GND``
     - ``GND``
     - 

   * - Obstacle Sensor
     - ``B7`` |OBS|
     - ``GND``
     - 

   * - Blue button
     - ``C13`` |UI|
     - ``VIN``
     - 

   * - 
     - ``C14``
     - ``NC``
     - 

   * -
     - ``C15``
     - ``A0`` |LINE|
     - Line Sensor – 9

   * - Line Sensor – Even
     - ``H0`` |LINE|
     - ``A1`` |LINE|
     - Line Sensor – 8

   * - Line Sensor – Odd
     - ``H1`` |LINE|
     - ``A4`` |LINE|
     - Line Sensor – 7

   * - 
     - ``VBAT``
     - ``B0`` |LINE|
     - Line Sensor – 6

   * - Line Sensor – 2
     - ``C2`` |LINE|
     - ``C1`` |LINE|
     - Line Sensor – 5

   * - Line Sensor – 3
     - ``C3`` |LINE|
     - ``C0`` |LINE|
     - Line Sensor – 4


Right Reader
~~~~~~~~~~~~~

Inner row is closer to the MCU, outer row is closer to the board edge.

.. list-table:: Right header (inner / outer rows)
   :header-rows: 1
   :widths: 18 12 12 18

   * - Left function label
     - Inner pin
     - Outer pin
     - Right function label

   * - IMU-RST
     - ``C9`` |IMU|
     - ``C8`` |MOT|
     - Left Motor - nSLP

   * - IMU-SCL
     - ``B8`` |IMU|
     - ``C6`` |UI|
     - Calibration LED / SENS_LED

   * - IMU-SDA
     - ``B9`` |IMU|
     - ``C5`` |LINE|
     - Line Sensor - 14

   * - 
     - ``AVDD``
     - ``U5V``
     - 

   * - Calibration LED
     - ``GND``
     - ``NC``
     - 

   * - ADC (on-board LED)
     - ``A5``
     - ``A12``
     - USB communication through Shoe of Brian

   * - Line Sensor - 10
     - ``A6`` |LINE|
     - ``A11``
     - USB communication through Shoe of Brian

   * - Line Sensor - 11
     - ``A7`` |LINE|
     - ``B12``
     - 

   * - Right Motor - PWM
     - ``B6`` |MOT|
     - ``B11`` |MOT|
     - Right Motor - DIR

   * - Right Motor - nSLP
     - ``C7`` |MOT|
     - ``GND``
     - 

   * - Left Encoder - Ch B
     - ``A9`` |ENC|
     - ``B2``
     - 

   * - Left Encoder - Ch A
     - ``A8`` |ENC|
     - ``B1`` |LINE|
     - Line Sensor - 13

   * - Left Motor - DIR
     - ``B10`` |MOT|
     - ``B15``
     - 

   * - Left Motor - PWM
     - ``B4`` |MOT|
     - ``B14``
     - 

   * - Right Encoder - Ch B
     - ``B3`` |ENC|
     - ``B13``
     - 

   * - 
     - ``A10``
     - ``C4`` |LINE|
     - Line Sensor - 12

   * - ADC (UART2 to ST-link MCU)
     - ``A2`` |LINE|
     - ``NC``
     - 

   * - ADC (UART2 to ST-link MCU)
     - ``A3`` |LINE|
     - ``NC``
     - 