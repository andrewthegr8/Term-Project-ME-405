"""Motor driver for Pololu Romi differential-drive robot.

    This module provides a :class:`Motor` class that drives a single DC motor
    through a DRV8838-based motor driver, such as the ones on the Pololu Romi
    chassis. The driver expects a separate PWM pin for speed control and a
    direction pin for direction control, plus a sleep pin to enable/disable
    the driver.

    The timer used to generate the PWM must be configured by the caller with
    an appropriate frequency before creating a :class:`Motor` instance.
"""

from pyb import Pin, Timer
import micropython
import pyb

class Motor:
    """Driver for a single DC motor using a DRV8838-style driver.

    The motor driver uses three control signals:

    * **PWM**: Timer channel output that sets motor speed via duty cycle.
    * **DIR**: Digital output that sets the rotation direction.
    * **nSLP**: Sleep pin that enables or disables the driver.

    Typical usage:

    .. code-block:: python

        # configure timer elsewhere
        tim = Timer(2, freq=20000)            # 20 kHz PWM, for example

        # create motor driver
        left_motor = Motor(
            PWM=Pin('X1'),
            DIR=Pin('X2'),
            nSLP=Pin('X3'),
            Timer=tim,
            NumChannel=1,
        )

        left_motor.enable()
        left_motor.set_effort(50)             # 50% forward
        left_motor.set_effort(-30)            # 30% reverse
        left_motor.disable()

    .. warning::
        Setting the effort to 0% does not disable the motor driver; it
        commands a 0% duty cycle which places the motor in brake mode. To
        fully disable the driver and put it into sleep mode, call :meth:`disable`.
        Note that this puts the motor into coast mode, so calling :meth:`disable`
        while the motor is running will cause Romi to coast to a stop.
    
    Args:
        PWM: Pin used for the timer PWM output.
        DIR: Pin used to control the direction of rotation.
        nSLP: Pin connected to the driver's nSLP (sleep) input.
        Timer: Configured ``pyb.Timer`` instance used to generate PWM.
        NumChannel: Timer channel number to use for PWM output.
    """

    
    def __init__(self, PWM: pyb.Pin, DIR: pyb.Pin, nSLP: pyb.Pin, Timer: pyb.Timer, NumChannel): #Need to update NumTimer and TimerChannel to be Timer and TimerChannel objects so we init timer outside of motor drivers 
        """Initialize a :class:`Motor` instance.

        This sets up the direction and sleep pins as push-pull outputs and
        configures the given timer channel for PWM on the provided PWM pin.
        The motor is initially disabled (sleep mode).

        """
        self.nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self.DIR_pin = Pin(DIR, mode=Pin.OUT_PP, value=0)

        #Setup specified timer and create PWM signal on specified channel
        self.tim = Timer
        self.timch = self.tim.channel(NumChannel, pin=PWM, mode=Timer.PWM, pulse_width_percent=0)

    @micropython.native
    def set_effort(self, effort: float) -> None:
        """Set the requested motor effort.

        The effort is a signed percentage in the range [-100.0, 100.0].
        The sign controls direction and the magnitude controls duty cycle.

        * Positive values drive the motor in the "forward" direction.
        * Negative values drive the motor in the "reverse" direction.
        * Zero commands 0% duty cycle (brake mode).

        Args:
            effort: Requested effort as a percentage of full drive,
                from -100.0 (full reverse) to 100.0 (full forward).
        """
        if effort < 0:
            self.DIR_pin.high()
        else:
            self.DIR_pin.low()

        self.timch.pulse_width_percent(abs(effort))
            
    def enable(self):
        """Enable the motor driver.

        Takes the driver out of sleep mode (nSLP high) and sets the PWM duty
        cycle to 0%, putting the motor in brake mode
        """
        self.nSLP_pin.high()
        self.timch.pulse_width_percent(0)
            
    def disable(self):
        """Disable the motor driver.

        Sets the PWM duty cycle to 0% and pulls nSLP low, putting the driver
        into sleep mode and the motor into coast mode.
        """
        self.timch.pulse_width_percent(0)
        self.nSLP_pin.low()
