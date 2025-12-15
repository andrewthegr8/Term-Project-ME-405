"""Quadrature encoder driver.

This module provides an :class:`Encoder` class that uses a hardware timer
configured in ``ENC_AB`` mode to decode a quadrature encoder. It tracks
the cumulative position and an averaged velocity estimate, and converts
raw encoder ticks into linear distance (inches) at the wheel.

Usage overview
--------------

The timer used for the encoder must be configured *before* creating an
:class:`Encoder` instance. The encoder A/B signals must be connected to
channel 1 and channel 2 of that timer.

Example
-------

.. code-block:: python

    from pyb import Pin, Timer
    from encoder import Encoder

    # Configure timer 4 for quadrature decoder mode (frequency is not critical)
    tim4 = Timer(4, prescaler=0, period=65535)

    # Create encoder object using timer 4 channels 1 and 2
    left_encoder = Encoder(
        Time=tim4,
        chA_pin=Pin('X1'),
        chB_pin=Pin('X2'),
    )

    while True:
        left_encoder.update()
        pos_in = left_encoder.get_position()
        vel_in_s = left_encoder.get_velocity()
        # use position / velocity in your controller

"""

from pyb import Pin, Timer
from time import ticks_us, ticks_diff
from ucollections import deque
from math import pi
import micropython


class Encoder:
    """Quadrature encoder interface using a hardware timer in ENC_AB mode.

    This class wraps a ``pyb.Timer`` configured for quadrature decoding
    and maintains:

    * A cumulative position in encoder ticks (and converted to inches).
    * A moving-average estimate of velocity, based on the most recent
      few samples.

    The timer must be in ``Timer.ENC_AB`` mode, and the encoder channels
    must be connected to timer channels 1 and 2.

    Args:
        Time: Configured :class:`pyb.Timer` instance used in ``ENC_AB`` mode.
        chA_pin: Pin connected to encoder channel A (timer channel 1).
        chB_pin: Pin connected to encoder channel B (timer channel 2).
    """

    def __init__(self, Time: Timer, chA_pin: Pin, chB_pin: Pin):
        """Initialize an :class:`Encoder` object.

        This sets up the timer channels for quadrature decoding, initializes
        position and velocity history, and resets the timer counter to zero.

        Raises:
            ValueError: If the timer's auto-reload value (period) is not
                an integer.
        """
        # Save timer and configure channels in quadrature mode
        self.tim = Time
        self.chA = self.tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        self.chB = self.tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)

        # Auto-reload value of the timer, used to detect over/underflow
        self.AR = self.tim.period()
        self.AR_2 = self.AR // 2

        # Sanity-check that AR is an integer
        try:
            int(self.AR)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("Timer auto-reload value (period) must be an integer.") from exc

        # State variables for position and velocity estimation
        self.position = int(0)           # Total accumulated position (ticks)
        self.last_position = int(0)      # Position at last update
        self.prev_count = int(0)         # Raw timer count at last update
        self.last_time = ticks_us()      # Timestamp (us) at last update
        self.delta = int(0)              # Change in count since last update
        self.dt = int(0)                 # Time step between updates (us)

        # Queue and running-sum for velocity moving average (ticks/us)
        self.velocity_queue = deque((), 5)
        for _ in range(5):
            self.velocity_queue.append(0.0)
        self.velocity_run_sum = 0.0

        # Conversion from encoder ticks to linear distance (inches) at the wheel:
        # (pi * wheel_diameter) / (ticks_per_rev * gear_ratio)
        # Specific numbers (1.375" wheel, 12*9.98*? etc.) are tuned for this robot.
        self.tick_to_in = (pi * 1.375 * 2) / (12 * 119.76)

        # Conversion factor from (ticks/us) to (in/s), with averaging over 5 samples
        self.velo_conv = self.tick_to_in * (1_000_000 / 5)

        # Start with a zeroed counter
        self.tim.counter(0)

    @micropython.native
    def update(self) -> None:
        """Run one update step to refresh position and velocity estimates.

        This method should be called periodically (e.g. from a timer
        callback or in the main control loop). It:

        * Reads the current timer counter.
        * Computes the difference from the previous count.
        * Corrects for counter overflows/underflows using the timer period.
        * Updates the cumulative position.
        * Updates the moving-average estimate of velocity.

        The updated values are then available via :meth:`get_position`
        and :meth:`get_velocity`.
        """
        # Read current count and time
        count = self.tim.counter()
        time = ticks_us()

        # Compute time delta in microseconds
        self.dt = ticks_diff(time, self.last_time)

        # Raw count delta
        sdelta = count - self.prev_count

        # Correct for underflow/overflow based on half the auto-reload value
        if sdelta < -self.AR_2:      # Overflow
            sdelta += self.AR
        elif sdelta > self.AR_2:     # Underflow
            sdelta -= self.AR

        # Update position (in ticks)
        self.delta = sdelta
        self.position += sdelta

        # Update velocity moving average (in ticks/us)
        self.velocity_run_sum -= self.velocity_queue.popleft()
        velocity = sdelta / self.dt if self.dt != 0 else 0.0
        self.velocity_queue.append(velocity)
        self.velocity_run_sum += velocity

        # Store state for next update
        self.last_time = time
        self.prev_count = count
        self.last_position = self.position

    @micropython.native
    def get_position(self) -> float:
        """Return the most recent position estimate in inches.

        The underlying timer counts down when the motors move forward
        with this configuration, so the internal tick count is
        negated before conversion.

        Returns:
            float: Wheel position in inches, relative to the last time
            :meth:`zero` was called (or object initialization).
        """
        # Timer counts down for forward motion; flip sign and convert to inches
        return -self.position * self.tick_to_in

    @micropython.native
    def get_velocity(self) -> float:
        """Return the most recent velocity estimate in inches per second.

        The returned value is the moving average of the last few
        velocity samples computed in :meth:`update`. The sign
        convention matches :meth:`get_position` (positive for forward
        motion).

        Returns:
            float: Wheel velocity in inches per second.
        """
        return -self.velocity_run_sum * self.velo_conv

    def zero(self) -> None:
        """Reset the encoder position and velocity history to zero.

        This method forces one :meth:`update` step, then:

        * Sets the accumulated position to zero.
        * Resets the last-position reference.
        * Clears the velocity queue and running sum.

        Subsequent calls to :meth:`get_position` will be measured
        relative to the position at the time :meth:`zero` was called.
        """
        self.update()
        self.position = 0
        self.last_position = 0

        # Reset velocity queue and running sum
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0)
        self.velocity_run_sum = 0.0
