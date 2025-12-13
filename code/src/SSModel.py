from math import sin,cos,pi
from micropython import const
from array import array
import micropython

numstatevars = const(7) #Use in for loops to make thing easier
#Define some constants so I can actually tell what the heck is going on

#Maybe don't feedback on velocity...

#State variables in order (in the order that they're put in the x matrix)
v_L   = const(0) #Left wheel velocity
v_R   = const(1) #Rigth wheel velocity
Psi   = const(2) #Heading
s_L   = const(3) #Left wheel linear displacement
s_R   = const(4) #Right wheel linear displacement
X_r   = const(5) #X position
Y_r   = const(6) #Y position

#Output variables in order (Some are duplicates of x matrix)
V     = const(0) #Overall linear velocity
S     = const(1) #Overall displacement
#Psi
#s_L
#s_R
#X_r
#Y_r

class SSModel():
    #This class impleemnts a State-Space model for Romi
    def __init__(self):
        # Given Electromechanical properties
        K_l       = 3.5     # Left Motor Gain [rad/(V*s)]
        K_r       = 3.35    # Right Motor Gain
        tau       = 0.1                 # Inverse of Motor Time Constant [1/s]
        w         = 5.5425              # Romi wheel base [in]
        r         = 1.375               # Romi wheel radius [in]]

        #Forms of properties used in calcs
        self.tau_inv  = 1/tau
        self.rkm_l    = r*K_l
        self.rkm_r    = r*K_r
        self.w_inv    = 1/w
        self.sixth    = 1/6
        

        #Feedback gains
        # self.L_Psi = 0
        self.L_Psi = 12
        self.L_v   = 40
        self.L_pos = 10

        #setup temporary variables to be persistent buffers
        self.k1 = array('f', [0.0]*numstatevars)
        self.k2 = array('f', [0.0]*numstatevars)
        self.k3 = array('f', [0.0]*numstatevars)
        self.k4 = array('f', [0.0]*numstatevars)



        self.xd     = array('f', [0.0]*numstatevars)
        self.x_last = array('f', [0.0]*numstatevars)
        self.x_tmp  = array('f', [0.0]*numstatevars)
        self.x_out  = array('f', [0.0]*numstatevars)
        self.y_hat  = array('f', [0.0]*numstatevars)

###NOTE:
    #The format of y (the True y) shall be as follows
    #y = [Psi   from IMU in rad
    #     v_L    Left wheel velo from encoder (in/s)
    #     v_R    Right wheel velo from ecoder (in/s)
    #     pos_L  Left wheel encoder based position (in)
    #     pos_R  Right wheel enoder based position (in)]



    @micropython.native
    def x_dot_fcn(self,u,x,y):
        #Calculate derivative of each state variable based on state values and inputs
        #Return list of state variable derivatives at this time.
        #This implements state feedback, to make this observer more accurate, but only 4 states have feedback
        xd = self.xd
        
        xd[v_L] = self.tau_inv * (self.rkm_l * u[0] - x[v_L])   + self.L_v * (y[1] - x[v_L])
        xd[v_R] = self.tau_inv * (self.rkm_r * u[1] - x[v_R])   + self.L_v * (y[2] - x[v_R])
        xd[Psi] = (self.w_inv) * (x[v_R] - x[v_L])              + self.L_Psi * (y[0] - x[Psi])
        xd[s_L] = x[v_L]                                        + self.L_pos * (y[3] - x[s_L])
        xd[s_R] = x[v_R]                                        + self.L_pos * (y[4] - x[s_R])
        xd[X_r] = 0.5*(x[v_L] + x[v_R]) * cos(x[Psi])  
        xd[Y_r] = 0.5*(x[v_L] + x[v_R]) * sin(x[Psi]) 
    
    @micropython.native
    def y_hat_fcn(self):
        #Calculates and returns the output vector based on the last computed state values
        
        #Create local references for faster lookup
        #x_last = self.x_last
        #y_hat  = self.y_hat
        
        #y_hat[V]  = 0.5 * (x_last[v_L] + x_last[v_R])
        #y_hat[S]  = 0.5 * (x_last[s_L] + x_last[s_R])
        #y_hat[Psi]  = x_last[Psi]
        #y_hat[s_L]  = x_last[s_L]
        #y_hat[s_R]  = x_last[s_R]
        #y_hat[X_r]  = x_last[X_r]
        #y_hat[Y_r]  = x_last[Y_r]
        return self.x_last

    @micropython.native
    def RK4_step(self, u, y, delta_t):
       #Find k1-k4:
            #1. Update preallocated xd values at appropriate x interval to get k
            #2. Copy these to preallocated k array
            #3. Update x_tmp variable with previous k values to find next k
        x_dot_fcn = self.x_dot_fcn
        x_last    = self.x_last
        xd        = self.xd
        x_tmp     = self.x_tmp
        x_out     = self.x_out
        k1        = self.k1
        k2        = self.k2
        k3        = self.k3
        k4        = self.k4
        
        #Find and save k1
        x_dot_fcn(u,x_last, y)
        k1[:] = xd
        
        #Find and save k2
        for i in range(numstatevars):
            x_tmp[i] = x_last[i]+0.5*k1[i]*delta_t
        x_dot_fcn(u, x_tmp, y)
        k2[:] = xd

        for i in range(numstatevars):
            x_tmp[i] = x_last[i]+0.5*k2[i]*delta_t
        x_dot_fcn(u, x_tmp, y)
        k3[:] = xd

        for i in range(numstatevars):
            x_tmp[i] = x_last[i]+k3[i]*delta_t
        x_dot_fcn(u, x_tmp, y)
        k4[:] = xd

        #Now that we have k's find and save x_n+1
        sixth = self.sixth
        for i in range(numstatevars):
            x_out[i] = x_last[i] + sixth*(k1[i]+2*k2[i]+2*k3[i]+k4[i])*delta_t

        #Save this for the next step
        x_last[:] = x_out

