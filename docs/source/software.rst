Software
==========

The program design for this project consists of several tasks which 
are run by a prioritized scheduler. Each task is a generator function,
and many are configured as finite state machines. Tasks communicate using
``share`` and ``queue`` objects. 

All tasks are stored in 



.. note::

   TODO: Explain the structure of the MicroPython code (main loop,
   modules, how motion commands work, etc.).

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