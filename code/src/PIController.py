import micropython

class PIController():
    #This class implements a PI controller.

    def __init__(self, kp, ki):
        self.esum      = 0.0 #Init esum for I control
        self.kp        = kp
        self.ki        = ki
        self.time_last = 0

    @micropython.native
    def get_ctrl_sig(self,cmd,velocity,time):
        #Preform PI control based on given desired and actual velocities and current time (in ms)
        #Proportional Control
        error = (cmd-velocity)
        p_cmd = self.kp*error
        #Integral Control
        dt = (time-self.time_last)/1000 #Calculate time elapsed since last run
        self.time_last = time           #Update last time
        self.esum += error*dt           #
        i_cmd = self.ki*self.esum
        return max(min(100, (i_cmd+p_cmd)), -100) #Return saturate control signal
       
    @micropython.native
    def reset(self,time):
        #Reset the controller
        self.esum = 0.0
        self.time_last = time
