"""Simple PI (proportional–integral) controller."""

import micropython


class PIController:
    """Discrete-time PI controller with output saturation.

    This controller is used for the robot's wheel speed control. It
    accumulates the integral of the error and returns a control signal
    clamped to the range [-100, 100], suitable for use as a motor PWM
    duty cycle command.
    """

    def __init__(self, kp: float, ki: float):
        """Initialize the PI controller.

        Args:
            kp -  Proportional gain constant.
            ki -  Integral gain constant.
        """
        self.esum = 0.0
        self.kp = kp
        self.ki = ki
        self.time_last = 0

    @micropython.native
    def get_ctrl_sig(self, cmd: float, velocity: float, time: int) -> float:
        """Compute the PI control signal at the given time.

        Args:
            cmd: Desired value (setpoint), e.g., target wheel speed.
            velocity: Measured value, e.g., current wheel speed.
            time: Current time in milliseconds (from ``ticks_ms()``).

        Returns:
            float: The saturated control output in the range [-100, 100].
        """
        error = cmd - velocity
        p_cmd = self.kp * error

        dt = (time - self.time_last) / 1000
        self.time_last = time
        self.esum += error * dt

        i_cmd = self.ki * self.esum
        return max(min(100, (i_cmd + p_cmd)), -100)

    @micropython.native
    def reset(self, time: int):
        """Reset the integrator and update the internal time reference.

        Args:
            time: Current time in milliseconds, typically from ``ticks_ms()``.
        """
        self.esum = 0.0
        self.time_last = time
