from pyb import Pin, Timer
import micropython

class Motor:
    '''A motor driver interface encapsulated in a Python class. Works with
       motor drivers using separate PWM and direction inputs such as the DRV8838
       drivers present on the Romi chassis from Pololu.'''
    
    '''
    -Need to setup timer with appropraite frequency and input timer object.
        Will initalize timer channel for PWM, just specify PWM pin and which timer channel
    
    '''
    
    def __init__(self, PWM: pyb.Pin, DIR: pyb.Pin, nSLP: pyb.Pin, Timer: pyb.Timer, NumChannel): #Need to update NumTimer and TimerChannel to be Timer and TimerChannel objects so we init timer outside of motor drivers 
        '''Initializes a Motor object'''
        self.nSLP_pin = Pin(nSLP, mode=Pin.OUT_PP, value=0)
        self.DIR_pin = Pin(DIR, mode=Pin.OUT_PP, value=0)
        #Setup specified timer and create PWM signal on specified channel
        self.tim = Timer
        self.timch = self.tim.channel(NumChannel, pin=PWM, mode=Timer.PWM, pulse_width_percent=0)

    @micropython.native
    def set_effort(self, effort: float):
        '''Sets the present effort requested from the motor based on an input value
           between -100 and 100'''
        if effort < 0:
            self.DIR_pin.high()
        else:
            self.DIR_pin.low()

        self.timch.pulse_width_percent(abs(effort))
            
    def enable(self):
        '''Enables the motor driver by taking it out of sleep mode into brake mode'''
        self.nSLP_pin.high()
        self.timch.pulse_width_percent(0)
            
    def disable(self):
        '''Disables the motor driver by taking it into sleep mode'''
        self.timch.pulse_width_percent(0)
        self.nSLP_pin.low()
