"""Infrared line sensor array driver.

This module implements a simple driver for a line sensor array composed
of multiple analog IR reflectance sensors connected to ADC pins.

Each sensor reading is calibrated so that:

* **0** corresponds to pure white.
* **1000** corresponds to pure black.

All scaling is done with integer arithmetic for efficiency on
MicroPython.
"""

import micropython
from pyb import ADC
from array import array


class LineSensor:
    """Array of calibrated infrared line sensors."""

    class IRSensor:
        """Single calibrated IR reflectance sensor.

        Each :class:`IRSensor` wraps one ADC channel and stores its own
        calibration values for "black" and "white", which are used to
        normalize raw readings into the 0–1000 range.
        """

        def __init__(self, Pin):
            """Initialize an IR sensor on the given ADC pin.

            Args:
                Pin: Pin object that will be passed to :class:`pyb.ADC`.
            """
            self.Sensor = ADC(Pin)
            # Default calibration values, overridden by cal_black/cal_white
            self.black = 4095
            self.white = 500

        def cal_black(self):
            """Calibrate this sensor for a black surface.

            Reads one ADC value and stores it as the 'black' reference.

            Returns:
                int: The raw ADC value stored as the black calibration value.
            """
            self.black = self.Sensor.read()
            return self.black

        def cal_white(self):
            """Calibrate this sensor for a white surface.

            Reads one ADC value and stores it as the 'white' reference.

            Returns:
                int: The raw ADC value stored as the white calibration value.
            """
            self.white = self.Sensor.read()
            return self.white

        def get_cal_val(self) -> int:
            """Return the calibrated reading in the range [0, 1000].

            The raw ADC reading is mapped linearly between the stored
            ``white`` and ``black`` values. The result is clamped to be at
            least 10 to avoid zeros that can break downstream math.

            Returns:
                int: Calibrated reflectance value between 0 and 1000.
            """
            raw = self.Sensor.read()
            return max(
                10,
                ((raw - self.white) * 1000 // (self.black - self.white)),
            )

    def __init__(self, Sensor_pins, Even_pin, Odd_pin):
        """Create a line sensor array driver.

        Args:
            Sensor_pins: Iterable of pin objects, one for each sensor.
            Even_pin: Pin used to control even-numbered sensor LEDs.
            Odd_pin: Pin used to control odd-numbered sensor LEDs.

        Notes:
            * Each element of ``Sensor_pins`` is used to construct an
              :class:`IRSensor`.
            * The even/odd control pins are currently kept high; they can be
              toggled if you wish to strobe the emitters.
        """
        self.Sensors_range = range(len(Sensor_pins))
        self.SensorArray = []
        self.SensorReadings = array("H", (0 for _ in range(len(Sensor_pins))))
        for pin in Sensor_pins:
            self.SensorArray.append(self.IRSensor(pin))
            self.Even_pin = Even_pin
            self.Odd_pin = Odd_pin
        self.Even_pin.high()
        self.Odd_pin.high()

    @micropython.native
    def read(self):
        """Read all sensors and return their calibrated values.

        The current implementation reads each sensor once and returns the
        calibrated value as stored in :class:`IRSensor`.

        Returns:
            array('H'): An array of unsigned 16-bit integers containing the
            calibrated values for each sensor.
        """
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].get_cal_val()
        return self.SensorReadings

    def cal_black(self):
        """Calibrate all sensors on a black surface.

        Returns:
            array('H'): An array of raw ADC values used as black references
            for each sensor.
        """
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].cal_black()
        return self.SensorReadings

    def cal_white(self):
        """Calibrate all sensors on a white surface.

        Returns:
            array('H'): An array of raw ADC values used as white references
            for each sensor.
        """
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].cal_white()
        return self.SensorReadings
