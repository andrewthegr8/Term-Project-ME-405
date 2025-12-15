Romi Control Architecture 
======================================

.. warning::

   This documentation is a work in progress. Some sections are incomplete,
   others are missing entirely.

   Charlie, if you are reading this, please grade this later. :)

This website contains hardware and software documentation for a project revolving around
a small differential drive robot (Romi). It was completed as part of a course (ME 405) at
Cal Poly SLO.

The primary project objective was for the robot to quickly and reliably
complete an obstacle course.

Robot features include

* Realtime State Estimation via a State Space Observer with Feedback
* Line Following Capabilities via Analog IR Sesnors
* Path Planning with Velocity and Heading Control
* Realtime Transmission of Telemetry Data to a PC via Bluetooth
* Obstacle Detection and Avoidance

Access the full code repository on GitHub `here <https://github.com/andrewthegr8/Term-Project-ME-405/tree/main>`_.


Demo
-----------------
The goal of the project was to program the robot to autonomously 
navigate an obstacle sourse using a variety of sensors. The video below shows
the robot successfully completing the course.

In the video, the robot uses an IR line sensor to follow the line until the "Y"
at which point it targets checkpoints and solo cups while avoiding obstacles.
It also utilizes its bump sensor to detect and avoid the "wall" near the start.


.. raw:: html

   <style>
     .video-container-vertical {
       position: relative;
       padding-bottom: 100%; /* 9:16 aspect ratio */
       height: 0;
       overflow: hidden;
       margin: 20px auto;
       background: #000;
     }
     .video-container-vertical iframe {
       position: absolute;
       top: 0;
       left: 0;
       width: 100%;
       height: 100%;
     }
   </style>

   <div class="video-container-vertical">
     <iframe
       src="https://www.youtube.com/embed/yyV9BpyjOOg"
       frameborder="0"
       allowfullscreen>
     </iframe>
   </div>


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   background
   hardware
   software
   pcui
   ssmodel
   drivingalgorithm
   importantnotes
