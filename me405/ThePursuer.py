"""Pure-pursuit path following for the Romi robot.

This module implements a specialized pure-pursuit controller that drives
the Romi through a fixed sequence of waypoints at varying speeds.

Inputs:

* Current X and Y position.
* Current heading.
* A flag indicating whether the controller should advance to the next
  waypoint immediately (for example when a wall is hit).

Output:

* Differential wheel speed offset (left vs. right).
* Desired forward speed.
"""

from PIController import PIController  # noqa: F401  (may be used in extensions)
import micropython
from micropython import const
from array import array
from math import sin, cos, sqrt, atan2, asin, pi, acos
from time import ticks_ms

head_weight = const(30)
FULLTHROTTLE = const(3)
SLOWDOWN_ON_APPROACH = const(8)
SLOWDOWN_DIST = const(7)
KP_FRACT = const(0.6)


class ThePursuer:
    """Pure-pursuit waypoint follower.

    This controller uses a list of predefined waypoints (X, Y) along the
    course, with associated base speeds and heading gains. At each call to
    :meth:`get_offset`, it:

    * Computes the error vector from the current position to the current
      waypoint.
    * Checks whether the waypoint has been reached (or if ``NextPoint``
      is set) and advances to the next waypoint if so.
    * Computes a heading error ``alpha`` between the robot's current
      heading and the direction to the waypoint.
    * Chooses a linear speed based on distance and headings, with
      slowdown near each waypoint.
    * Returns a proportional steering offset and the chosen speed.
    """

    def __init__(self, base_speed, success_dist, kp, ki):
        """Initialize pure-pursuit controller and waypoint list.

        Args:
            base_speed: Default linear speed (unused directly; per-segment
                base speeds are encoded in :attr:`base_speed` array).
            success_dist: Distance threshold (inches) below which the next
                waypoint will be targeted.
            kp: Heading proportional gain (kept for compatibility; per-
                segment gains are stored in :attr:`kp_head`).
            ki: Integral gain (currently unused but retained for possible
                PI control extensions).
        """
        # Predefined waypoint coordinates (inches)
        self.x_coords = array(
            "f",
            [
                33.46456692913386,
                51.181102362204726,
                55.118110236220474,
                49.21259842519685,
                27.559055118110237,
                13.779527559055119,
                2.952755905511811,
                0.0,
                15.748031496062993,
                15.748031496062993,
                -1.968503937007874,
            ],
        )
        self.y_coords = array(
            "f",
            [
                14.763779527559056,
                0.0,
                11.811023622047244,
                27.559055118110237,
                24.606299212598426,
                24.606299212598426,
                24.606299212598426,
                1.968503937007874,
                11.811023622047244,
                0.0,
                -1.968503937007874,
            ],
        )

        # Per-segment base speeds
        self.base_speed = array(
            "f",
            [
                18,
                16,
                25,
                14,
                16.5,
                16,
                16,
                10,
                14,
                18,
                18,
            ],
        )
        # Distance from the waypoint at which we stop boosting speed
        self.brake_dist = array(
            "f",
            [
                7,
                7,
                0,
                6,
                7,
                7,
                7,
                6,
                7,
                7,
                7,
            ],
        )
        # Heading gains per segment
        self.kp_head = array(
            "f",
            [
                9,
                9,
                10,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
                9,
            ],
        )

        self.num_wp = len(self.x_coords) - 1
        self.idx = 0
        self.success_dist = success_dist
        self.current_speed = base_speed
        self.countdown = 0
        # A PI controller could be used here for heading, but currently only P is used
        # self.ctrller = PIController(kp, ki)

    @micropython.native
    def get_offset(self, C_x, C_y, Psi, NextPoint):
        """Compute wheel speed offset and forward speed.

        Args:
            C_x: Current X position (inches).
            C_y: Current Y position (inches).
            Psi: Current heading angle (radians).
            NextPoint: If ``True``, force advancing to the next waypoint
                (for example, when a wall is detected).

        Returns:
            tuple[float, float]: ``(offset, speed)`` where

            * ``offset`` is a differential speed term added/subtracted from
              the base speed on each wheel to create a turn.
            * ``speed`` is the desired linear speed (same sign and units
              as your velocity setpoint).
        """
        Psi = -Psi  # Coordinate system adjustment

        # Current target waypoint
        P_x = self.x_coords[self.idx]
        P_y = self.y_coords[self.idx]

        # Error vector and distance to waypoint
        E_x = P_x - C_x
        E_y = P_y - C_y
        E = sqrt(E_x ** 2 + E_y ** 2)

        # Check if waypoint reached or forced to advance
        if E < self.success_dist or NextPoint:
            self.idx += 1
            if self.idx > self.num_wp:
                # No more waypoints; signal “done” via KeyboardInterrupt
                raise KeyboardInterrupt
            P_x = self.x_coords[self.idx]
            P_y = self.y_coords[self.idx]
            E_x = P_x - C_x
            E_y = P_y - C_y
            E = sqrt(E_x ** 2 + E_y ** 2)

        # Heading error alpha between robot heading and error vector
        cpsi = cos(Psi)
        spsi = sin(Psi)
        alpha = atan2(cpsi * E_y - spsi * E_x, E_x * cpsi + E_y * spsi)

        # Desired speed: base segment speed plus a distance-dependent boost
        # which decreases near the waypoint and with increasing heading error.
        speed = self.base_speed[self.idx] + max(
            FULLTHROTTLE
            + (SLOWDOWN_ON_APPROACH * (E - self.brake_dist[self.idx])),
            0,
        ) / (1 + head_weight * abs(alpha))

        # Proportional steering offset on heading error
        offset = self.kp_head[self.idx] * alpha

        # Slow down briefly when NextPoint is asserted
        if NextPoint:
            self.countdown = 10
            speed = 0.1
        if self.countdown:
            self.countdown -= 1
            speed = 0.1

        return offset, speed
