"""BNO055 IMU driver for MicroPython.

This module implements a minimal driver for a BNO055 IMU connected over
I²C. It configures sensor units and axis mapping, provides utilities to
store and restore calibration data, and exposes methods to read heading
and yaw rate.

All register addresses and bit masks are specific to the BNO055.
"""

from pyb import I2C
from micropython import const
from math import pi
import micropython

# I2C address of the IMU
IMU_ADDR = const(0x28)

# Register addresses
OPR_MODE = const(0x3D)
CALIB_STAT = const(0x35)
CALIB_LSB = const(0x55)
AXIS_MAP_SIGN = const(0x42)
UNIT_SEL = const(0x3B)
EUL_HEADING = const(0x1A)
ANG_VELO_Z = const(0x18)

# Bit masks and configuration values
MODE_MSK = const(0b11110000)
SIGN_REMAP_MSK = const(0b11111000)
UNIT_SEL_MSK = const(0b11111000)
FUSION_MODE = const(0b00001100)
CONFIG_MODE = const(0b00000000)
Z_SIGN_NEG = const(0b00000001)
Y_SIGN_NEG = const(0b00000010)
X_SIGN_NEG = const(0b00000100)
UNITS = const(0b00000111)


class IMU:
    """Driver for a BNO055 IMU in NDOF (fusion) or config mode.

    The driver assumes the IMU is connected on a bus that is already
    initialized as an :class:`pyb.I2C` controller. It:

    * Configures units (m/s², radians, rad/s) and axis sign mapping.
    * Provides helpers for switching between configuration and fusion modes.
    * Supports storing and restoring the 22-byte calibration block.
    * Computes a continuous heading estimate that unwraps at ±π.

    Radians / heading notes:

    * Raw heading data is in 1/16th of a degree; values are converted to
      radians.
    * :meth:`get_heading` uses a wrap/un-wrap scheme to provide a
      continuous heading (`psi_continuous`) across multiple revolutions.

    """

    def __init__(self, i2c_controller: I2C):
        """Initialize the IMU and configure units and axis mapping.

        Args:
            i2c_controller: Pre-configured :class:`pyb.I2C` instance on the
                appropriate bus for the BNO055.
        """
        self.i2c = i2c_controller
        # Configure units to m/s^2, radians, and rad/s
        buff = self.i2c.mem_read(1, IMU_ADDR, UNIT_SEL)
        write = buff[0] & UNIT_SEL_MSK
        write |= UNITS
        self.i2c.mem_write(write, IMU_ADDR, UNIT_SEL)

        # Remap axis signs to match the robot's coordinate system
        buff = self.i2c.mem_read(1, IMU_ADDR, AXIS_MAP_SIGN)
        write = buff[0] & SIGN_REMAP_MSK
        write |= Z_SIGN_NEG
        write |= Y_SIGN_NEG
        write |= X_SIGN_NEG
        self.i2c.mem_write(write, IMU_ADDR, AXIS_MAP_SIGN)

        # Heading offset and continuous heading variables
        self.head_offset = 0.0
        self.last_heading = 0.0
        self._b2 = bytearray(2)
        self.pi = pi
        self.pi_2 = 2 * pi
        self.psi_continuous = 0.0

    def set_fusion(self):
        """Put the IMU into 9DOF fusion mode.

        The sensor must already be powered and responding on the I²C bus.
        """
        buff = self.i2c.mem_read(1, IMU_ADDR, CALIB_STAT)
        write = buff[0] & MODE_MSK
        write |= FUSION_MODE
        self.i2c.mem_write(write, IMU_ADDR, OPR_MODE)

    def set_config(self):
        """Put the IMU into configuration mode.

        In config mode, the IMU stops running sensor fusion but allows
        certain configuration operations such as reading & writing calibration data.
        """
        buff = self.i2c.mem_read(1, IMU_ADDR, OPR_MODE)
        write = buff[0] & MODE_MSK
        write |= CONFIG_MODE
        self.i2c.mem_write(write, IMU_ADDR, OPR_MODE)

    def cal_status(self) -> bool:
        """Check whether the IMU is fully calibrated.

        .. warning::
            The calibration status check is only vaid when the IMU
            is in Fusion mode. Make sure to call :meth:`set_fusion` at some point
            before using this method.

        Returns:
            bool: ``True`` if all calibration subsystems (accelerometer,
            gyroscope, magnetometer, system) are fully calibrated as
            indicated by the BNO055's status register, otherwise ``False``.
        """
        buff = self.i2c.mem_read(1, IMU_ADDR, CALIB_STAT)
        return True if buff[0] == 0xFF else False

    def read_cal_data(self, cali_file: str):
        """Read calibration data from the IMU and store it to a file.
        
        .. warning::
            The calibration coeffiecients are only valid when the IMU is
            in CONFIG mode. Do not attempt to read or write the calibration
            coefficients when the IMU is in FUSION mode. Make sure to call
            :meth:`set_config` at some point before using this method.


        Args:
            cali_file: Path to a file on the MicroPython filesystem where
                the 22-byte calibration block will be written.
        """
        cali_data = bytearray(22)
        self.i2c.mem_read(cali_data, IMU_ADDR, CALIB_LSB)
        with open(cali_file, "wb") as f:
            f.write(cali_data)

    def write_cal_data(self, cali_file: str):
        """Write calibration data from a file back into the IMU.

        .. warning::
            The calibration coeffiecients are only valid when the IMU is
            in CONFIG mode. Do not attempt to read or write the calibration
            coefficients when the IMU is in FUSION mode. Make sure to call
            :meth:`set_config` at some point before using this method.

        Args:
            cali_file: Path to a file containing a previously stored 22-byte
                calibration block.
        """
        with open(cali_file, "rb") as f:
            cali_data = f.read()
        self.i2c.mem_write(cali_data, IMU_ADDR, CALIB_LSB)

    def init_heading(self):
        """Initialize heading offset from the current IMU reading.

        The raw heading is read once and stored as an offset so that future
        heading values are reported relative to this initial orientation.
        """
        data = self.i2c.mem_read(2, IMU_ADDR, EUL_HEADING)
        data = (data[1] << 8) | data[0]
        self.head_offset = -data / 900  # radians

    @micropython.native
    def get_heading(self) -> float:
        """Return the continuous heading estimate in radians.

        The heading is read from the IMU, converted to radians, adjusted by
        :attr:`head_offset`, mapped into the range [-π, π], and then
        unwrapped to form a continuous signal over multiple revolutions.

        Returns:
            float: Continuous heading angle (radians).
        """
        data = self._b2
        try:
            self.i2c.mem_read(data, IMU_ADDR, EUL_HEADING)
        except OSError:
            return self.last_heading

        raw = (data[1] << 8) | data[0]
        head = -raw / 900 - self.head_offset

        w = ((head + self.pi) % self.pi_2) - self.pi
        d = (w - self.last_heading + self.pi) % self.pi_2 - self.pi
        self.psi_continuous += d
        self.last_heading = w
        return self.psi_continuous

    @micropython.native
    def get_yaw_rate(self) -> float:
        """Return the yaw rate about the Z-axis in rad/s.

        Returns:
            float: Yaw rate (radians per second) computed from the Z-axis
            angular velocity output of the IMU.
        """
        data = self._b2
        self.i2c.mem_read(data, IMU_ADDR, ANG_VELO_Z)
        yawrate = (data[1] << 8) | data[0]
        if yawrate & 0x8000:  # negative
            yawrate -= 0x10000
        return yawrate / 900
