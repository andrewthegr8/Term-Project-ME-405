Software
==========

The program design for this project consists of several tasks which 
are run by a prioritized scheduler (:mod:`me405.cotask`). Each task is a generator function,
and many are configured as finite state machines. Tasks communicate using 
``share`` and ``queue`` objects from :mod:`me405.task_share`, which, along with the scheduler, are 
adapted from code developed by Dr. John Ridgley. The original code for the
scheduler and inter-task communication objects
can be found in the `ME405-Support
<https://github.com/spluttflob/ME405-Support>` repository. 









Tasks
--------------



Helper Classes
---------------------
The following classes are initialized and passed to tasks, 
except, of course, :mod:`me405.cotask` which schedules and runs the tasks.

Task scheduler
~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.cotask
   :members:
   :undoc-members:
   :show-inheritance:

Shared data structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: me405.task_share
   :members:
   :undoc-members:
   :show-inheritance:

Hardware Drivers
----------------------------------
The following classes are used for interfacing with hardware.

Motor driver
----------------

.. automodule:: me405.Motor
   :members:
   :undoc-members:
   :show-inheritance:

Encoder
-----------------

.. automodule:: me405.Encoder
   :members:
   :undoc-members:
   :show-inheritance: