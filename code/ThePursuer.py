#Class to implement pure pursuit control on Romi
#Assume Romi is operating at a constant straightline velocity
#Inputs: Romi's current X and Y coordinates
#Returns: offset between left and right wheels (to cause rotation)

from PIController import PIController
import micropython
from micropython import const
from array import array
from math import sin, cos, sqrt, atan2, asin, pi, acos
from time import ticks_ms

head_weight   = const(30)
FULLTHROTTLE = const(3) #When perfectly aligned, go this speed
SLOWDOWN_ON_APPROACH = const(8) #Speed up when farther way, slowdown when close
SLOWDOWN_DIST = const(7) #When this close to the next point, start slowing down
KP_FRACT = const(0.6) #Kp_head as a function of linear speed
#kp_head = const(9) 

class ThePursuer():

    def __init__(self, base_speed, success_dist, kp, ki):
        #Hard code in waypoints
        self.x_coords = array('f', [33.46456692913386,
51.181102362204726,
55.118110236220474,
49.21259842519685,
27.559055118110237,
13.779527559055119,
2.952755905511811,
0.0,
15.748031496062993,
15.748031496062993,
-1.968503937007874
])
        self.y_coords = array('f', [14.763779527559056,
0.0,
11.811023622047244,
27.559055118110237,
24.606299212598426,
24.606299212598426,
24.606299212598426,
1.968503937007874,
11.811023622047244,
0.0,
-1.968503937007874])
        
        self.base_speed = array('f',
                                    [18, #Line to CP 1
                                    16,  #CP 1  to CP2
                                    25,  #CP2 to CUP
                                    14,  #Cup to CP 3
                                    16.5,  #CP 3 to Garage Ent
                                    16,  #Garage Ent to Garage Middle
                                    16,  #Garage Middle to Garage end
                                    10,  #Garage end to otherside of wall - Slowdown when approaching wall
                                    14,  #Wall to Cup
                                    18,  #Cup to line
                                    18]  #Line to home                       
                                )
        self.brake_dist = array('f',     #Distance from next wp when we stop boosting
                                    [7, #Line to CP 1
                                    7,  #CP 1  to CP2
                                    0,  #CP2 to CUP
                                    6,  #Cup to CP 3
                                    7,  #CP 3 to Garage Ent
                                    7,  #Garage Ent to Garage Middle
                                    7,  #Garage Middle to Garage end
                                    6,  #Garage end to otherside of wallSlowdown when approaching wall
                                    7,  #Wall to Cup
                                    7,  #Cup to line
                                    7]  #Line to home                       
                                )
        self.kp_head = array('f',     #heading error to rotational speed 
                                    [9, #Line to CP 1
                                    9,  #CP 1  to CP2
                                    10,  #CP2 to CUP
                                    9,  #Cup to CP 3
                                    9,  #CP 3 to Garage Ent
                                    9,  #Garage Ent to Garage Middle
                                    9,  #Garage Middle to Garage end
                                    9,  #Garage end to otherside of wallSlowdown when approaching wall
                                    9,  #Wall to Cup
                                    9,  #Cup to line
                                    9]  #Line to home
        )    
        self.num_wp = len(self.x_coords)-1 #Number of waypoints
        self.idx = 0 #Index for accessing waypoints
        self.success_dist = success_dist #When are we close enough to a waypoint to target the next one?
        #self.aligned_enough = aligned_enough #When are we aligned enough to the target to hammer down?
        #self.base_speed = base_speed #Min speed when changing alignment
        self.current_speed = base_speed #Init current speed variable
        #self.slowdown_dist = slowdown_dist
        self.countdown = 0
        #initalize controller for controlling the offset
        #self.ctrller = PIController(kp,ki)

    @micropython.native
    def get_offset(self,C_x,C_y,Psi,NextPoint):
        Psi = -Psi #This is due of my poor understanding of coordinate systems
        #Time to go to next point?
        #Calculate absolute distance between points
        #For maximum efficiency, bind globals to locals
        P_x = self.x_coords[self.idx]
        P_y = self.y_coords[self.idx]
        #Calculate error vector
        E_x = P_x - C_x
        E_y = P_y - C_y
        E = sqrt(E_x**2 + E_y**2) #Absolute distance to wp = magnitude of E vector
        if E < self.success_dist or NextPoint:
            self.idx +=1
            if self.idx > self.num_wp:
                raise KeyboardInterrupt #We arrived
            P_x = self.x_coords[self.idx] #Rebind at new idx
            P_y = self.y_coords[self.idx]
            #Recalc E vector
            #Calculate error vector
            E_x = P_x - C_x
            E_y = P_y - C_y
            E = sqrt(E_x**2 + E_y**2)
        #Find heading error (alpha)
        cpsi = cos(Psi)
        spsi = sin(Psi)
        alpha = atan2(cpsi*E_y - spsi*E_x, E_x*cpsi + E_y*spsi) #Heading misalignment in radians alpha = error
        #Compute desired linear speed as a function of the base speed, heading error, and distance error
        #speed = self.base_speed + (dist_weight*(E-(self.success_dist+2)))/(1+head_weight*abs(alpha)) #Speed is proportional to distance from point and inversely proportional to heading error
        speed = self.base_speed[self.idx] + max(FULLTHROTTLE+(SLOWDOWN_ON_APPROACH*(E-self.brake_dist[self.idx])),0)/(1+head_weight*abs(alpha))

        #if alpha < 0.1:
        #    if E > 10:
        #        speed = 40
        #    elif E > 5:
        #        speed = 20
        #    else:
        #        speed = self.base_speed
        #else:
        #    speed = self.base_speed
        #When we hit the wall, and for a couple ticks after, drive slow
        offset = self.kp_head[self.idx]*alpha #Proportional control on heading error. Kp is a fraction of linear velocity

        if NextPoint:
            self.countdown = 10
            speed = 0.1
        if self.countdown:
            self.countdown -= 1
            speed = 0.1
        #if abs(alpha) < self.aligned_enough and E > self.slowdown_dist: #If closely enough aligned to target and we're far enough away from the next point
        #    speed = self.base_speed+2*E #Basic proportional control on romi velocity based on distance from point
        #else:
        #    speed = self.base_speed
        return offset, speed #IDK why offset needs to be negative but apparently it does

