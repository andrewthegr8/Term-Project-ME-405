Heading and Speed Control Logic
===============================

Overview
---------------

The point seking control algorithm is designed to orient and drive the Romi smoothly
and accurately along a predefined sequence of waypoints. At any given moment,
the controller uses three key pieces of information:

1. Romi’s current position :math:`\mathbf{C}`
2. The next target waypoint :math:`\mathbf{P}`
3. Romi’s absolute heading (yaw angle) :math:`\Psi`

Using these, the algorithm computes the *error vector* pointing from Romi
toward the next waypoint and then determines the angular misalignment between
Romi’s heading and this vector. This angle, called the *heading error*
:math:`\alpha`, is the primary quantity used for rotational control.

Vector Definitions
==================

The waypoint and current-position vectors are defined as:

.. math::

   \mathbf{P} =
   \begin{bmatrix}
       P_x \\[4pt]
       P_y
   \end{bmatrix},
   \qquad
   \mathbf{C} =
   \begin{bmatrix}
       C_x \\[4pt]
       C_y
   \end{bmatrix}

The error vector is simply:

.. math::

   \mathbf{E} =
   \begin{bmatrix}
       E_x \\[4pt]
       E_y
   \end{bmatrix}
   = \mathbf{P} - \mathbf{C}

Heading Error Computation
=========================

To determine how far Romi must rotate to point toward the waypoint, the
algorithm computes the angle between Romi’s heading direction vector and the
error vector.

The heading direction (a unit vector) is given by:

.. math::

   \hat{\mathbf{h}} =
   \begin{bmatrix}
       \cos\Psi \\[4pt]
       \sin\Psi
   \end{bmatrix}

Using dot and cross products, the cosine and sine of the heading error
:math:`\alpha` are:

.. math::

   \cos\alpha = \frac{\hat{\mathbf{h}} \cdot \mathbf{E}}{\lVert \mathbf{E} \rVert}
   \qquad
   \sin\alpha = \frac{\hat{\mathbf{h}} \times \mathbf{E}}{\lVert \mathbf{E} \rVert}

The cross and dot products expand to:

.. math::

   \hat{\mathbf{h}} \times \mathbf{E}
   = \cos\Psi\,E_y \;-\; \sin\Psi\,E_x

.. math::

   \hat{\mathbf{h}} \cdot \mathbf{E}
   = (\cos\Psi)E_x \;+\; (\sin\Psi)E_y

Finally, the correctly signed heading error is computed with:

.. math::

   \boxed{
   \alpha = \operatorname{atan2}\!\left(\hat{\mathbf{h}} \times \mathbf{E},
                                       \hat{\mathbf{h}} \cdot \mathbf{E}\right)
   }

We use :math:`\operatorname{atan2}` instead of :math:`\arccos` or
:math:`\arcsin` because those functions cannot distinguish among all four
quadrants; `atan2` preserves both magnitude and sign of the angular offset.

Conceptual Description
======================

The algorithm continually works to minimize the heading error :math:`\alpha`.
When :math:`\alpha = 0`, Romi is perfectly aligned with the direction to the
next waypoint. When :math:`\alpha` is nonzero, the controller commands an
angular velocity that steers Romi back toward alignment.

The field diagrams illustrate:

* Romi’s current position :math:`\mathbf{C}`
* The waypoint :math:`\mathbf{P}`
* The error vector :math:`\mathbf{E} = \mathbf{P} - \mathbf{C}`
* Romi’s heading vector :math:`\hat{\mathbf{h}}`
* The geometric angle :math:`\alpha` between the two vectors

By iteratively updating the waypoint index once Romi gets within a
specified distance, the robot smoothly transitions from target to target along
its path. This method is particularly effective in constrained environments,
such as navigating between narrow columns or aligning precisely with objects
to manipulate.

Speed Control Logic
===================

In addition to controlling heading, the algorithm modulates Romi’s linear
speed. Early testing showed that constant-speed operation produced undesirable
behavior: Romi would overshoot waypoints, especially during tight turns or when
approaching closely spaced points. To address this, the controller adjusts
speed based on two primary factors:

1. **Heading Accuracy**  
   When :math:`\alpha` is large (i.e., Romi is not well aligned), forward speed
   is reduced so Romi turns rather than drifting off course. As alignment
   improves, speed increases.

2. **Distance to the Target**  
   As Romi approaches a waypoint, speed is gradually reduced. This prevents
   overshooting and allows smoother transitions when the next waypoint becomes
   active.

The final commanded speed is computed as:

.. math::

   \text{speed}
   = \text{base\_speed}_i + 
     \frac{
         \max\!\left(
             \text{FULLTHROTTLE}
             +
             (\text{SLOWDOWN\_ON\_APPROACH} \cdot (E - \text{brake\_dist}_i)),
             0
         \right)
     }
     {1 + \text{head\_weight}\,|\alpha|}

Here:

* ``FULLTHROTTLE``, ``SLOWDOWN_ON_APPROACH`` and ``head_weight``  
  are global tuning constants.
* ``base_speed_i`` and ``brake_dist_i``  
  vary by waypoint. Waypoints near walls use smaller base speeds, while
  waypoints prone to overshoot use larger brake distances.

This structure ensures Romi accelerates when appropriately aligned and far
from the target, yet decelerates for high heading error or when approaching a
waypoint. The ``max(…, 0)`` term guarantees speed is never penalized for being
too close to a target.

Performance Notes
=================

Although the speed and heading controllers could be refined further, this
implementation performed robustly in competition conditions. The tuning values
were selected empirically due to time constraints, but the combined strategy
enabled Romi to navigate the track accurately, handle complex obstacle regions,
and maintain stable behavior across all required path segments.

