#Line Sensor class to manage a variable number of IR line sensors
import micropython
from pyb import ADC
from array import array

####IMPORTANT!!!
'''
The individual sensors are setup up to consider completely white as 0 and completely black as 1000
This is in acordance with a high voltage reading correpsonding to black and low to white
0 and 1000 were chosen so that all math done in the following methods could be integer operations
Sensor values will be return as an unsigned integer between 0 and 1000
'''

class LineSensor:

    class IRSensor:
    #Class for each an individual IR sensor of the line sensor array
        def __init__(self, Pin):
            '''Initializer Function
            Setup ADC on the pin for this sensor
            Initialize calibration variables
            '''
            self.Sensor = ADC(Pin) 
            self.black = 4095
            self.white = 500

        def cal_black(self):
            #Compute and store average from an array of black calibration values
            self.black = self.Sensor.read()
            return self.black

        def cal_white(self):
            #Compute and store average from an array of white calibration values
            self.white = self.Sensor.read()
            return self.white

        def get_cal_val(self):
            raw = self.Sensor.read()
            return max(10,((raw - self.white)*1000//(self.black-self.white))) #return average of normalized values or 10, whichever is greater
        
    def __init__(self, Sensor_pins, Even_pin, Odd_pin):
        '''
        Initializer Function
        Sensorpins = List or Tuple of pin object for each ir sensor
        Even_pin = pin object for even control pin
        Odd_pin = same but for odd
        Tim = timer object with appropriate frequency for polling pins set
        Buff_size = number of samples to take from each pin for each reading
        '''
        self.Sensors_range = range(len(Sensor_pins))
        self.SensorArray = []
        self.SensorReadings = array('H', (0 for i in range(len(Sensor_pins))))
        for pin in Sensor_pins:
            self.SensorArray.append(self.IRSensor(pin)) #Create list which contains an IR object for each sensor
            self.Even_pin = Even_pin
            self.Odd_pin = Odd_pin
        self.Even_pin.high()
        self.Odd_pin.high()

    @micropython.native
    def read(self):
        #Turn on even and then odd LEDS, get calibrated value for each sensors and put in buffer
        #self.Even_pin.high()
        #self.Odd_pin.high()
        #sleep(0.001)
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].get_cal_val()
        #self.Even_pin.low()
        #self.Odd_pin.low()
        return self.SensorReadings
    
    def cal_black(self):
        #Run to calibrate sensors to a pure black value. Return calibration value for each sensor
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].cal_black()
        return self.SensorReadings
    
    def cal_white(self):
    #Run to calibrate sensors to a pure black value. Return calibration value for each sensor
        for idx in self.Sensors_range:
            self.SensorReadings[idx] = self.SensorArray[idx].cal_white()
        return self.SensorReadings
    