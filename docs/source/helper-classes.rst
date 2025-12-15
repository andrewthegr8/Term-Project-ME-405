Helper Classes
------------------

To keep main.py from becoming overcrowded,
some functionality was bundled into object types.
This also allows initialization steps to easily happen
before the scheduler is run; an object of each type is initialized
beofre it is passed to the appropriate task.

.. tip::
    The ``@micropython.native`` emitter can be used to help code run
    more quickly. However, this emitter cannot be used on generator
    functions, which is what each task is. So, bundling task preformance into
    the method of an object means that the emitter can be used on that
    method to optimize the code's preformance. 

The following classes are initialized and passed to tasks, 
except, of course, :mod:`cotask` which schedules and runs the tasks.

* :class:`SSModel.SSModel` –
  Continuous-time state-space model and observer with RK4 integration for
  estimating pose, heading, and wheel states.

* :class:`PIController.PIController` –
  Closed-loop PI controller for regulating wheel velocity using encoder
  feedback.

* :class:`ThePursuer.ThePursuer` –
  Point seeking navigation controller that selects waypoints and computes
  steering and speed commands for high-level path following.

* :mod:`cotask` –
  Cooperative task scheduler providing Task objects, profiling support,
  and a priority-based dispatcher for multitasking under MicroPython.

* :mod:`task_share` –
  Shared variable and FIFO queue system used to safely exchange data
  between tasks.

PI Speed Controller
~~~~~~~~~~~~~~~~~~~

.. automodule:: PIController
   :members:
   :undoc-members:
   :show-inheritance:

State-Space Model
~~~~~~~~~~~~~~~~~

See the :doc:`ssmodel` page for more detailed information about
the model. This section focuses primarily on program functionality.

.. automodule:: SSModel
   :members:
   :undoc-members:
   :show-inheritance:

Point Targeting Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~

See the :doc:`drivingalgorithm` for more detailed infomation
about the course navigation design. This section focuses primarily
on program functionality.

.. automodule:: ThePursuer
   :members:
   :undoc-members:
   :show-inheritance:

Task Scheduler
~~~~~~~~~~~~~~~~~~~

.. automodule:: cotask
   :members:
   :undoc-members:
   :show-inheritance:

Shared Data Structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: task_share
   :members:
   :undoc-members:
   :show-inheritance:
