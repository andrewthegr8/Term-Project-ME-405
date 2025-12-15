"""Bluetooth serial communication helper.

This module provides the :class:`BTComm` class, a small wrapper around a
MicroPython ``UART`` object used to faciliate communication with the
robot over Bluetooth.

The class:

* Collects incoming characters into a line-oriented command string.
* Provides a non-blocking :meth:`check` method suitable for use in a
  cooperative multitasking.
* Sends pre-built binary packets using :meth:`ship`.
"""

import micropython


class BTComm:
    """Bluetooth serial communications wrapper.

    This class encapsulates a serial device (such as a MicroPython
    :class:`pyb.UART`) and provides simple methods for non-blocking command
    reception and packet transmission.

    Args:
            serial_device: A :class:`pyb.UART` object
    """

    def __init__(self, serial_device):
        """Initialize the Bluetooth communications helper.

        Args:
            serial_device: An object implementing a UART-like interface with
                methods such as ``any()``, ``read()``, and ``write()``. On the
                robot, this is typically a :class:`pyb.UART` instance.
        """
        # Serial port used for communication
        self.serial_device = serial_device
        # Most recently decoded command string
        self.command = str()
        # Fixed-size byte buffer for assembling a line
        self._buf = bytearray(24)
        # Current index into the buffer
        self._idx = 0

    @micropython.native
    def check(self):
        """Check for new serial data and assemble complete commands.

        This method is intended to be called regularly from a cooperative
        task. It reads at most one character from the underlying serial
        device, updates an internal line buffer, and detects when a complete
        command line (terminated by carriage return) has been received.

        Line handling rules:

        * ``\\r`` (carriage return, ASCII 13) → terminate the current line,
          decode and store the buffer, reset the
          buffer, and return ``True``.
        * ``\\n`` (line feed, ASCII 10) → ignored.
        * Backspace (ASCII 8) → remove the last character from the buffer.
        * Any other character → appended to the buffer until ``\r`` is recieved.

        Returns:
            bool: ``True`` if a complete line has just been received,
            ``False`` otherwise.
        """
        if self.serial_device.any():
            b = self.serial_device.read(1)[0]
            if b == 13:      # Carriage return -> end of command
                self.command = self._buf[:self._idx].decode("utf-8")
                self._idx = 0
                return True
            elif b == 10:    # Line feed -> ignore
                pass
            elif b == 8 and self._idx:  # Backspace
                self._idx -= 1
            elif self._idx < len(self._buf):
                self._buf[self._idx] = b
                self._idx += 1
        return False

    @micropython.native
    def get_command(self):
        """Return the most recent command string.

        Returns:
            str: The last complete command received over the serial link. If no
            complete command has been received yet, this is an empty string.
        """
        return self.command

    @micropython.native
    def ship(self, packet):
        """Send a pre-built packet over the serial link.

        Args:
            packet: A :class:`bytearray` object
            containing the already-packed packet to transmit.
        """
        self.serial_device.write(memoryview(packet))
