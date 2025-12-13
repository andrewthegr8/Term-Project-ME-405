from pyb import I2C
from micropython import const
from math import pi
import micropython

'''
IMU I2C communication Driver
Note that this driver has hard coded values for memory register locations
for a BNO055 IMU
'''

#Constants
IMU_ADDR   = const(0x28) #I2C location of IMU peripherial


#Memory Addresses
OPR_MODE      = const(0x3D)
CALIB_STAT    = const(0x35)
CALIB_LSB     = const(0x55)
AXIS_MAP_SIGN = const(0x42)
UNIT_SEL      = const(0x3B)
EUL_HEADING   = const(0x1A)
ANG_VELO_Z    = const(0x18)


#Useful masks

MODE_MSK       = const(0b11110000)
SIGN_REMAP_MSK = const(0b11111000)
UNIT_SEL_MSK   = const(0b11111000)
FUSION_MODE    = const(0b00001100)
CONFIG_MODE    = const(0b00000000)
Z_SIGN_NEG     = const(0b00000001)
Y_SIGN_NEG     = const(0b00000010)
X_SIGN_NEG     = const(0b00000100)
UNITS          = const(0b00000111)





class IMU:
    
    def __init__(self,i2c_controller):
        self.i2c = i2c_controller #Pre-configured i2c controller on the appropriate bus
        #Configure the orientation of the IMU
        ##Set the units to m/s^2, radians, and rad/s
        buff = self.i2c.mem_read(1,IMU_ADDR, UNIT_SEL)
        write = buff[0] & UNIT_SEL_MSK
        write = write | UNITS
        self.i2c.mem_write(write, IMU_ADDR, UNIT_SEL)
        ##Change z-axis sign
        buff = self.i2c.mem_read(1,IMU_ADDR, AXIS_MAP_SIGN)
        write = buff[0] & SIGN_REMAP_MSK
        write |= Z_SIGN_NEG
        write |= Y_SIGN_NEG
        write |= X_SIGN_NEG
        self.i2c.mem_write(write, IMU_ADDR, AXIS_MAP_SIGN)
        self.head_offset = 0.0
        self.last_heading = 0.0
        self._b2 = bytearray(2) #Preallocate array for memread to read into
        self.pi = pi
        self.pi_2 = 2*pi
        self.psi_continuous = 0.0



    def set_fusion(self): #Set the IMU to 9DOF Fusion mode with fast magnometer calibration
        #We read the register, clear target bits with a mask, and then write 
        buff = self.i2c.mem_read(1,IMU_ADDR,CALIB_STAT) #Read Operation mode register
        write = buff[0] & MODE_MSK
        write |= FUSION_MODE
        self.i2c.mem_write(write, IMU_ADDR, OPR_MODE)

    def set_config(self): #Set the IMU to config mode
        #We read the register, clear target bits with a mask, and then write 
        buff = self.i2c.mem_read(1,IMU_ADDR,OPR_MODE) #Read Operation mode register
        write = buff[0] & MODE_MSK
        write |= CONFIG_MODE
        self.i2c.mem_write(write, IMU_ADDR, OPR_MODE)

    def cal_status(self): #Check IMU calibration status
        buff = self.i2c.mem_read(1,IMU_ADDR,CALIB_STAT)
        return True if buff[0] == 0xFF else False #Return true is completely calibrated, else False
    
    def read_cal_data(self,cali_file): #Get and return the calibration data from the IMU
        cali_data = bytearray(22)
        self.i2c.mem_read(cali_data, IMU_ADDR, CALIB_LSB) #Read all 22 bytes of calibration data
        with open(cali_file, 'wb') as f:
            f.write(cali_data)
    
    def write_cal_data(self,cali_file): #Write calibration data from a file to the IMU
        with open(cali_file, "rb") as f:
           cali_data = f.read()
        self.i2c.mem_write(cali_data, IMU_ADDR, CALIB_LSB)

    def init_heading(self): #Get the current heading and use it as an offset
        data = self.i2c.mem_read(2, IMU_ADDR, EUL_HEADING)
        data = (data[1] << 8) | data[0] #Convert to 1 16-bit binary number
        self.head_offset = -data/900 #Heading offset in radians

    @micropython.native
    def get_heading(self): #Read and convert heading euler angle. Return as radian float
        data = self._b2
        try:
            self.i2c.mem_read(data, IMU_ADDR, EUL_HEADING)
        except OSError:
            return self.last_heading
        #We have to manually intrepret signed number because micropython is too dumb to do it for us I guess
        data = (data[1] << 8) | data[0] #Convert to 1 16-bit binary number
        #Apply heading offset
        head = -data/900-self.head_offset #Convert to radians and subtract offset and change sign convention
        #Go from 0,2pi convnetion to -pi,pi convention
        w = ((head + self.pi) % self.pi_2) - self.pi
        # compute shortest signed delta and accumulate
        d = (w - self.last_heading + self.pi) % self.pi_2 - self.pi
        self.psi_continuous += d
        self.last_heading = w
        return self.psi_continuous         
    
    @micropython.native
    def get_yaw_rate(self): #Read and convert yaw rate. Return as radian/s float
        data = self._b2
        self.i2c.mem_read(data, IMU_ADDR, ANG_VELO_Z)
        #We have to manually intrepret signed number because micropython is too dumb to do it for us I guess
        yawrate = (data[1] << 8) | data[0] #Convert to 1 16-bit binary number
        if yawrate & 0x8000: #Is negative?
            yawrate -= 0x10000 #If so, subtract the largest unsigned number + 1 from it
        return yawrate/900 #Convert to radians
        








    

