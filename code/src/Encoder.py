from pyb import Pin, Timer
from time import ticks_us, ticks_diff   # Use to get dt value in update()
from ucollections import deque
from math import pi
import micropython

'''
Encoder Class Overview:
-Assumes timer is already configured with appropriate frequency
-Using mode ENC_AB from timer module requires encoder to be connected to channels 1 and 2 of timer
    So, just input the timer channel pins for appropriate timer's channel 1 and 2.
-The Timer module kindly handles quadrature sign decoding for use :)

Inputs(Timer Object, Timer Channel 1 Pin (Encoder Channel A), Timer Channel 2 Pin (Encoder Channel B))

Methods:
    Update(): Should be run automatically at a set period.
        Reads timer counter
        Checks for overflow and adjusts if necessary
        Calculates current position and velocity

'''

class Encoder:
    '''A quadrature encoder decoding interface encapsulated in a Python class'''

    def __init__(self, Time: pyb.Timer, chA_pin: pyb.Pin, chB_pin: pyb.Pin):
        '''Initializes an Encoder object'''
        self.tim = Time
        self.chA = self.tim.channel(1, pin=chA_pin, mode=Timer.ENC_AB)
        self.chB = self.tim.channel(2, pin=chB_pin, mode=Timer.ENC_AB)  
        self.AR = self.tim.period() #Get the auto-reload value for the timer. This is used in overflow handling
        self.AR_2 = self.AR//2      #For maximum speed                        

        #Not totally sure if this next block is necessary, but I figure it can't hurt.
        try:
            int(self.AR)
        except:
            raise ValueError("Timer Auto-reload value (period) must be an integer.")
        self.position         = int(0)                    # Total accumulated position of the encoder
        self.last_position    = int(0)                    # Position from last update (to calculate velocity)
        self.prev_count       = int(0)                        # Counter value from the most recent update
        self.last_time        = ticks_us()
        self.delta            = int(0)                        # Change in count between last two updates
        self.dt               = int(0)                        # Amount of time between last two updates
        self.velocity_queue = deque((), 5)                    #To keep track of recent velocity measurements for averaging
        for _ in range(5):
            self.velocity_queue.append(0.0)      
        self.velocity_run_sum = 0.0                          #To make moving average more memory efficient
        self.tick_to_in       = (pi*1.375*2)/(12*119.76)      #(pi*d)/(PPR*gear ratio*)
        self.velo_conv        = self.tick_to_in*(1_000_000/5) #Convert ticks to in, us to s, and take average (5)
        self.tim.counter(0)                                   # Reset timer counter to zero

    @micropython.native
    def update(self):
        '''Runs one update step on the encoder's timer counter to keep
           track of the change in count and check for counter reload'''
        #Get new count and calculate delta
        count = self.tim.counter()
        time = ticks_us()
        sdelta = self.delta
        self.dt = ticks_diff(time, self.last_time)
        sdelta = count - self.prev_count
        
        #Check for underflow/overflow
        if sdelta < -self.AR_2: #Overflow
            sdelta += self.AR
        elif sdelta > self.AR_2: #Underflow
            sdelta += -self.AR

        #Update position (leave in ticks!)
        self.position += sdelta

        #Update velocity
        self.velocity_run_sum -= self.velocity_queue.popleft() #Remove oldest velocity value from running total
        velocity = sdelta/(self.dt) #calculate current velocity (ticks/us) (Probably close to zero!!!)
        self.velocity_queue.append(velocity) #Add newest velocity to queue
        self.velocity_run_sum += velocity #Add latest velocity to running sum

        #Update variables
        self.last_time = time
        self.prev_count = count
        self.last_position = self.position


    @micropython.native                
    def get_position(self):
        '''Returns the most recently updated value of position as determined
           within the update() method'''
        #So... Our timers count down when the motors are moving forward.
        #Fix this by returning the additive invers of our position vector
        return -self.position*self.tick_to_in
            
    @micropython.native
    def get_velocity(self):
        '''Returns a measure of velocity using the the most recently updated
           value of delta as determined within the update() method'''
        #Same deal with negative velocity :)
        #Return average of up to 5 most recent values.
        return -self.velocity_run_sum*self.velo_conv

    
    def zero(self):
        '''Sets the present encoder position to zero and causes future updates
           to measure with respect to the new zero position'''
        self.update()
        self.position = 0
        self.last_position = 0
        #Reset velocity queue
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0.0)
        self.velocity_queue.append(0)
        self.velocity_run_sum = 0.0
