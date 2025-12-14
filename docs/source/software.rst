Software (MicroPython)
=======================

The program design for this project consists of several tasks which 
are run by a prioritized scheduler (:mod:`me405.cotask`). Each task is a generator function,
and many are configured as finite state machines. Tasks communicate using 
``share`` and ``queue`` objects from :mod:`me405.task_share`, which, along with the scheduler, are 
adapted from code developed by Dr. John Ridgley. The original code for the
scheduler and inter-task communication objects
can be found in the `ME405-Support <https://github.com/spluttflob/ME405-Support>`_ repository. 

The software documentation is broken up into 3 sections:

* :doc:`main-program` - This contains information about the tasks that provide high level functionality
* :doc:`helper-classes` - This contains information about object types developed to preform specific functions in this project
* :doc:`drivers` - This contians infromation about driver classes developed to interface with hardware
