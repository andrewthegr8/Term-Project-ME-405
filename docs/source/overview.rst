Overview
===============


ME 405 Mechatronics
----------------------
This class is offered as part of Cal Poly Mechanical Engineering program.
Here's the description from the Cal Poly catalog.

Microprocessor applications in machine control and product design. Applied electronics.
Drive technology; transducers and electromechanical systems. Real-time programming.
Mechatronic design methodology. 

The Fall 2025 Mechatronics class offering focused on programming in 
MicroPython on a STM32 MCU to operate a small differential drive robot.

Term project
-----------------
The term project for the class was to program the robot to autonomously 
navigate an obstacle sourse using a variety of sensors. The video below shows
the robot successfully completing the course.

In the video, the robot uses an IR line sensor to follow the line until the "Y"
at which point it targets checkpoints and solo cups while avoiding obstacles.
It also utilizes its bump sensor to detect and avoid the "wall" near the start.

Access the full code repository on GitHub `here <https://github.com/andrewthegr8/Term-Project-ME-405/tree/main>`.

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










