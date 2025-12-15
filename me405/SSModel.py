"""State-space model of the Romi differential-drive robot.

This module defines a simple continuous-time state-space model for the
Romi robot with 7 state variables, and uses a 4th-order Runge–Kutta
(RK4) integrator to propagate the state.

State vector (indices):

* ``v_L`` – Left wheel linear velocity.
* ``v_R`` – Right wheel linear velocity.
* ``Psi`` – Heading angle (radians).
* ``s_L`` – Left wheel path length.
* ``s_R`` – Right wheel path length.
* ``X_r`` – X position in the world frame (inches).
* ``Y_r`` – Y position in the world frame (inches).

Measurement vector ``y`` is expected to contain:

* Heading from IMU (rad).
* Left wheel velocity (in/s).
* Right wheel velocity (in/s).
* Left wheel position (in).
* Right wheel position (in).
"""

from math import sin, cos, pi
from micropython import const
from array import array
import micropython

numstatevars = const(7)

# State indices
v_L = const(0)
v_R = const(1)
Psi = const(2)
s_L = const(3)
s_R = const(4)
X_r = const(5)
Y_r = const(6)

# Output indices (only used conceptually)
V = const(0)
S = const(1)


class SSModel:
    """State-space model and observer for the Romi robot.

    The model uses a simple first-order motor model plus kinematic
    relations for a differential-drive robot. A basic observer gain is
    applied to some states so that encoder/IMU measurements are blended
    into the state estimate.
    """

    def __init__(self):
        """Initialize model parameters, gains, and state storage."""
        # Motor gains (rad/(V*s))
        K_l = 3.5
        K_r = 3.35
        tau = 0.1           # Motor time constant inverse [1/s]
        w = 5.5425          # Wheel base [in]
        r = 1.375           # Wheel radius [in]

        # Derived parameters
        self.tau_inv = 1 / tau
        self.rkm_l = r * K_l
        self.rkm_r = r * K_r
        self.w_inv = 1 / w
        self.sixth = 1 / 6

        # Observer feedback gains
        self.L_Psi = 12
        self.L_v = 40
        self.L_pos = 10

        # Pre-allocated temporary arrays for RK4
        self.k1 = array("f", [0.0] * numstatevars)
        self.k2 = array("f", [0.0] * numstatevars)
        self.k3 = array("f", [0.0] * numstatevars)
        self.k4 = array("f", [0.0] * numstatevars)

        self.xd = array("f", [0.0] * numstatevars)
        self.x_last = array("f", [0.0] * numstatevars)
        self.x_tmp = array("f", [0.0] * numstatevars)
        self.x_out = array("f", [0.0] * numstatevars)
        self.y_hat = array("f", [0.0] * numstatevars)

    @micropython.native
    def x_dot_fcn(self, u, x, y):
        '''Compute the time derivative of the state vector.
            Called internally by the RK4 integrator.

        Args:
            u: Input vector (e.g. motor voltages) of length 2.
            x: Current state vector of length 7.
            y: Measurement vector of length 5.

        Side Effects:
            Updates :attr:`xd` with the computed state derivatives.
        '''
        xd = self.xd

        xd[v_L] = (
            self.tau_inv * (self.rkm_l * u[0] - x[v_L])
            + self.L_v * (y[1] - x[v_L])
        )
        xd[v_R] = (
            self.tau_inv * (self.rkm_r * u[1] - x[v_R])
            + self.L_v * (y[2] - x[v_R])
        )
        xd[Psi] = self.w_inv * (x[v_R] - x[v_L]) + self.L_Psi * (y[0] - x[Psi])
        xd[s_L] = x[v_L] + self.L_pos * (y[3] - x[s_L])
        xd[s_R] = x[v_R] + self.L_pos * (y[4] - x[s_R])
        xd[X_r] = 0.5 * (x[v_L] + x[v_R]) * cos(x[Psi])
        xd[Y_r] = 0.5 * (x[v_L] + x[v_R]) * sin(x[Psi])

    @micropython.native
    def y_hat_fcn(self):
        """Return the current estimated output vector.

        .. tip::
            Since the model is configured so that the output vector
            matches the state vector, this method simply returns the last
            state vector.

        Returns:
            array('f'): Estimated state/output vector.
        """
        return self.x_last

    @micropython.native
    def RK4_step(self, u, y, delta_t: float):
        """Advance the state estimate by one time step using RK4.

        Args:
            u: Input vector (length 2) at the current time step.
            y: Measurement vector (length 5) at the current time step.
            delta_t: Time step in seconds.
        """
        x_dot_fcn = self.x_dot_fcn
        x_last = self.x_last
        xd = self.xd
        x_tmp = self.x_tmp
        x_out = self.x_out
        k1 = self.k1
        k2 = self.k2
        k3 = self.k3
        k4 = self.k4

        # k1
        x_dot_fcn(u, x_last, y)
        k1[:] = xd

        # k2
        for i in range(numstatevars):
            x_tmp[i] = x_last[i] + 0.5 * k1[i] * delta_t
        x_dot_fcn(u, x_tmp, y)
        k2[:] = xd

        # k3
        for i in range(numstatevars):
            x_tmp[i] = x_last[i] + 0.5 * k2[i] * delta_t
        x_dot_fcn(u, x_tmp, y)
        k3[:] = xd

        # k4
        for i in range(numstatevars):
            x_tmp[i] = x_last[i] + k3[i] * delta_t
        x_dot_fcn(u, x_tmp, y)
        k4[:] = xd

        # Combine increments
        sixth = self.sixth
        for i in range(numstatevars):
            x_out[i] = x_last[i] + sixth * (
                k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]
            ) * delta_t

        # Save for next step
        x_last[:] = x_out
