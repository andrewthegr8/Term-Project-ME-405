"""Main control file for Romi

    This file is comprised of several tasks that are scheduled to run at 
    desired intervals
"""

import gc
from pyb import Pin, Timer, UART, I2C
import time
from time import ticks_ms, ticks_diff, sleep
import cotask
import task_share
import ustruct
from array import array
from math import copysign
from micropython import const
#Import custom object (drivers, etc)
from Encoder import Encoder
from Motor import Motor
from LineSensor import LineSensor
from BTComm import BTComm
from IMU import IMU
from SSModel import SSModel
from PIController import PIController
from ThePursuer import ThePursuer

#Tunable Parameters
MAXDELTA = const(25) #Maximum amount by which the duty cycle will be increased or decreased per tick
ARRIVED = const(2.5)     #Once we're this close to the point, start targeting the next


###WARNING: If you continually send commands to Romi, it currently prioritizes recieving over sending so it will never stream data
def Talker_fun(shares):
    '''
    This task is responsible for sending and recieivng data over bluetooth
    '''

    #Unpack chares and queues
    packet, packet_fmt, btcomm, velo_set, kp_lf, ki_lf, time_L, pos_L, velo_L, time_R, pos_R, velo_R, cmd_L, cmd_R, offset, Eul_head, yaw_rate, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw, p_pos_L, p_pos_R = shares
    state = 0
    sendit = True

    while True:
        if state == 0: #State zero: init (Setup serial port)
            #State zero: Listening mode - See if we have input. If we do, retrieve it.
            if btcomm.check(): #Recieve and process 1 character, and see if we have a complete command
                state = 1 #If command got to state 2 to intrepret
            else: #If nothing to read, then we write!
                #Check to make sure there's something in every single one of our queues
                #Use .many() for these queues to make sure we don't empty it and upset the controller/estimator
                #Note we only check a few queues but pull from many. This is becuase several of the queues are filled 
                # from the smae taks so checking both is redundant
                if (time_L.many() and
                    time_R.many() and
                    cmd_L.many() and
                    Eul_head.many() and
                    p_pos_L.many()): 
                    ustruct.pack_into((packet_fmt), packet, 3, #Format, buffer, offset
                                            time_L.get(),
                                            time_R.get(),
                                            pos_L.get(),
                                            velo_L.get(),
                                            velo_R.get(),
                                            pos_R.get(),
                                            cmd_L.get(),
                                            cmd_R.get(),
                                            Eul_head.get(),
                                            yaw_rate.get(),
                                            offset.get(),
                                            X_pos.get(),
                                            Y_pos.get(),
                                            p_v_R.get(),
                                            p_v_L.get(),
                                            p_head.get(),
                                            velo_set.get(),
                                            p_pos_L.get(),
                                            p_pos_R.get())
                    #Sneaky... only send every other packet...
                    if sendit:
                        btcomm.ship(packet)
                        sendit = False
                    else: 
                        sendit = True
        elif state == 1:  #Interpret input
            rawcmd = btcomm.get_command() #We only end up here when there's a command waiting
            if not rawcmd:
                pass
            elif rawcmd[0] == '$': #See if we were given a command
                if rawcmd[1:4] == 'SPD': #Set Motor Speed (in/s)
                    try:
                        velo_set.put(float(rawcmd[4:]))
                    except:
                        pass
            state = 0 #Go back to interfacing
        yield state

def IMU_Interface_fun(shares):
    imu, Eul_head, yaw_rate, SENS_LED = shares
    while True:
        Eul_head.put(imu.get_heading()) #Convert rads to degs
        yaw_rate.put(0) #Not currently using yaw_rate so no reason to read it from IMU
        yield

def SS_Simulator_fun(shares):
    #Run a glorious state-space simulation of Romi
    #State equations and RK4 solver are contained in SSModel object
    RUN_LED, imu_off, ssmodel, mainperiod, y, u, Eul_head, velo_L, velo_R, pos_L, pos_R, cmd_L, cmd_R, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw, p_pos_L, p_pos_R = shares

    while True:
        #If we have hit the wall, disable feedback from the IMU
        if RUN_LED.value():
            RUN_LED.value(0)
        else:
            RUN_LED.value(1)
        if imu_off.get() == 1:
            ssmodel.L_Psi = 0
        #Run our RK4 solver using the latest motor voltages
        #Assumes constant 9 volts supplied to motors
        u[0] = 0.09*cmd_L.view()
        u[1] = 0.09*cmd_R.view()
        #time_now = ticks_us()
        #delta_t = ticks_diff(time_now,time_last)/1000000
        #time_last = time_now
        #Build y-matrix of true values
        y[0] = Eul_head.view()
        y[1] = velo_L.view()
        y[2] = velo_R.view()
        y[3] = pos_L.view()
        y[4] = pos_R.view()
        ssmodel.RK4_step(u, y, mainperiod)
        #Get outputs and send to shares
        yhat = ssmodel.y_hat_fcn()
        p_v_L.put(yhat[0])
        p_v_R.put(yhat[1])
        p_head.put(yhat[2])
        p_pos_L.put(yhat[3])
        p_pos_R.put(yhat[4])
        X_pos.put(yhat[5])
        Y_pos.put(-yhat[6]) #This might screw me over later... we'll see
        p_yaw.put(0)
        yield



def LineFollow_fun(shares):
    """!
        Line Follower Task
        Implements PI controller for setpoint offset for left an right motors
        based on line sensor readings.
        Passes command signal offset to the controller
        Inputs:
            Shares: offset (float) - speed offset to be added to right motor/subtracted from left
            Queues: IRread (int)   - returns the individual IR sensor readings normalized and multiplied by 1000
            
            Line_sensor: Line Sensor object. Should already be initialized and calibrated.
    """
    SENS_LED, length, Aixi_sum, Ai_sum, p_X, velo_set, lf_stop, kp_lf, ki_lf, offset, Line_sensor = shares

    state = 0
    #Initialize controller variables
    esum = 0
    time_last = 0

    while True:
        if state == 0: 
            if lf_stop.get() == 1:
                SENS_LED.value(0)
                state = 1
                yield state
            #Make sure time_last is initialized
            if time_last == 0: time_last = ticks_ms()
            #Read line sensor
            readings = Line_sensor.read()
            Aixi_sum = 0
            Ai_sum = 0
            #Calculate centroid (x_bar)
            #Assumes all sensors have width 1.
            for idx,val in enumerate(readings):
                Aixi_sum += val*(idx-length)
                Ai_sum += val
            if Aixi_sum == 0: #Happens when all sensors read 0, ie, just white, ie, line lost
                error = 0
            else:
                error = Aixi_sum/sum(readings)
            #Do P control
            p_ctrl = kp_lf*error
            time = ticks_ms()
            dt = ticks_diff(time,time_last)/1000 #convert ms to s
            time_last = time
            #Only do I ctrl if we have a speed command to prevent integral windup
            if int(velo_set.get()) == 0:
                esum = 0
            else:
                esum += error*dt
            i_ctrl = ki_lf*esum
            #d_ctrl = kd_lf.get()*(error-last_error)/dt
            ctrl_sig = p_ctrl+i_ctrl
            if X_pos.view() > 25:
                ctrl_sig += 8.5
            offset.put(ctrl_sig)
            SENS_LED.value(1)
        elif state == 1:
            SENS_LED.value(0)
            pass #Do nothing
        yield state

def Pursuer_fun(shares): #Task which implements pure pursuit
    WALL_LED, imu_off, obst_sens, velo_set, lf_stop, thepursuer, p_X, p_Y, p_head, offset = shares
    
    state = 0
    wall = False
    wall_hit = False

    while True:
        if state == 0:
            #thepursuer.ctrller.time_last = ticks_ms() #Init offset controller for I ctrl
            if p_X.view() >= 31.25: # and p_Y.view() >= 3: #If we're past the magic point
                lf_stop.put(1) #Tell line follower to stop
                state = 1
        elif state == 1: 
            X = X_pos.view()
            Y = Y_pos.view()
            if X < 3 and Y < 10 and wall_hit is False: #if close to wall and wall not hit yet
                if obst_sens.value() == 0: #if obstacle detected
                    wall = True
                    wall_hit = True
                    WALL_LED.value(1)
                    #imu_off.put(1)
            else:
                wall = False
            off, speed = thepursuer.get_offset(p_X.view(),p_Y.view(),p_head.view(),wall)
            if not velo_set.get() == 0: #Unless we have a 0 speed command
                velo_set.put(speed)
                offset.put(off)
            else: #stop and stay in place
                velo_set.put(0)
                offset.put(0)
        yield state
    
    
    
        



def Controller_fun(shares): #Goated PI controller
    """!
    Motor Controller Task
    Implements PI control for both motors
    Also has the ability to set both motors to zero speed and signal
    the motor controllers to reset the encoders.
    """

    #Unpack shares and queues
    offset, leftencoder, leftmotor, pos_L ,rightencoder, rightmotor, pos_R, t_L, v_L, t_R, v_R, r_ctrl, l_ctrl, velo_L, velo_R, time_L, time_R, velo_set, cmd_L, cmd_R = shares
    state = 0
    lastsig_L = 0.0
    lastsig_R = 0.0
    delta = 0.0

    while True:
        #Always update encoders and grab data to use
        leftencoder.update()
        t_L = time.ticks_ms()
        rightencoder.update()
        t_R = time.ticks_ms()
        v_L = leftencoder.get_velocity()
        v_R = rightencoder.get_velocity()
        if state == 0: #State 0: set last time varibales after the motor controllers have initalized and put something in the queues
            l_ctrl.last_time = t_L
            r_ctrl.last_time = t_R
            state = 1
        elif state == 1: #State 1: Run the controller
            cmd = velo_set.get()
            if cmd == 0.0: #If command is zero, reset and go to state 2
                cmd_L.put(0)     
                leftmotor.set_effort(0)
                cmd_R.put(0)
                rightmotor.set_effort(0)
                state = 2
            else:   #Run the controller
                off = offset.get()
                #Left motor stuff
                l_sig = l_ctrl.get_ctrl_sig((cmd+off),v_L,t_L)
                delta = l_sig - lastsig_L
                if delta > MAXDELTA:
                    l_sig = lastsig_L + MAXDELTA
                elif delta < -MAXDELTA:
                    l_sig = lastsig_L - MAXDELTA
                lastsig_L = l_sig
                leftmotor.set_effort(l_sig)
                cmd_L.put(l_sig)
                
                #Right motor stuff
                r_sig = r_ctrl.get_ctrl_sig((cmd-off),v_R,t_R)
                delta = r_sig - lastsig_R
                if delta > MAXDELTA:
                    r_sig = lastsig_R + MAXDELTA
                elif delta < -MAXDELTA:
                    r_sig = lastsig_R - MAXDELTA
                lastsig_R = r_sig
                rightmotor.set_effort(r_sig)
                cmd_R.put(r_sig)
        
        elif state == 2: #State 2 do other things and reinitialize on rentry to state 2
            cmd = velo_set.get()
            cmd_L.put(0) #Update these every tick for accurate monitoring
            cmd_R.put(0)
            if not cmd == 0.0: #If command is not zero, go back to state 1
                #Reinit and go back to state 1
                #Reset Encoders (to zero position and velocity (esp since velocity is moving average))
                leftencoder.zero()
                rightencoder.zero()
                #Reset PI controllers
                l_ctrl.reset(t_L)
                r_ctrl.reset(t_R)
                state = 1
        #Always send data for collection
        pos_L.put(leftencoder.get_position())
        velo_L.put(v_L)
        time_L.put(t_L)
        pos_R.put(rightencoder.get_position())
        velo_R.put(v_R)
        time_R.put(t_R)
        yield state

def GarbageCollector_fun():
    while True:
        gc.collect()
        yield

def Cali_test(Line_sensor,button,SENS_LED):
        #Run blocking calibration sequence
        SENS_LED.high()
        print('Begin blocking calibration sequence')
        print('Press blue button to calibrate on black.')
        while button.value() == 1:
            pass
        print('Calibrating!')
        black = Line_sensor.cal_black()
        print('Black calibration array')
        print(black)
        sleep(1)
        print('Press blue button to calibrate on white.')
        while button.value() == 1:
            pass
        white = Line_sensor.cal_white()
        print('White calibration array')
        print(white)
        sleep(1)
        print('Press blue button to begin.')
        while button.value() == 1:
            pass
        SENS_LED.low()
        return Line_sensor

# This code creates all the needed shares and queues then starts the tasks.
# The tasks run until a keyboard interrupt, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    print("Here we go!\r\n"
          "Press Ctrl-C to stop and show diagnostics.")

    #MOTOR & ENCODER SETUP
    #Setup Timers
    tim1 = Timer(1, freq=10000) #For left motor encoder
    tim2 = Timer(2, freq=10000) #For right motor encoder
    tim3 = Timer(3, freq=10000) #For left motor PWM
    tim4 = Timer(4, freq=10000)   #For right motor PWM
    
    #Remap pins for Timer2
    Pin(Pin.cpu.A0,mode=Pin.ANALOG) # Set pin modes back to default
    Pin(Pin.cpu.A1,mode=Pin.ANALOG)
    Pin(Pin.cpu.A15, mode=Pin.ALT, alt=1)
    Pin(Pin.cpu.B3, mode=Pin.ALT, alt=1)

    #Setup motor and encoder objects
    leftmotor = Motor(Pin.cpu.B4,Pin.cpu.B10,Pin.cpu.C8,tim3,1)
    leftmotor.enable()
    rightmotor = Motor(Pin.cpu.B6,Pin.cpu.B11,Pin.cpu.C7,tim4,1)
    rightmotor.enable()
    rightencoder = Encoder(tim2,Pin.cpu.A15,Pin.cpu.B3)
    leftencoder = Encoder(tim1,Pin.cpu.A8,Pin.cpu.A9)

    gc.collect()

    #Init controller objects
    r_ctrl = PIController(0.6,15) #Set kp and ki for motors
    l_ctrl = PIController(0.6,15)

    #Init internal variables for controller generator
    t_L = 0
    v_L = 0.0
    t_R = 0
    v_R = 0.0


    #TALKER SETUP
    #Setup serial device for communicator and create BTComm object
    serial_device = UART(5,460800)
    btcomm = BTComm(serial_device)

    #Initalize a buffer for talker to store output data in    
    packet_fmt = "<II" + "f"*17
    packet = bytearray(3 + ustruct.calcsize(packet_fmt))          #Create a buffer that we can later pack numbers into
    #Set the sync and type bytes
    packet[0] = 0xAA 
    packet[1] = 0x55 
    packet[2] = 0x00
    
    gc.collect()

    #LINE SENSOR SETUP
    #Setup pins for Line Sensor
    #s15 = Pin.cpu.D2
    s14 = Pin.cpu.C5
    s13 = Pin.cpu.B1
    s12 = Pin.cpu.C4
    s11 = Pin.cpu.A7
    s10 = Pin.cpu.A6
    s9  = Pin.cpu.A0
    s8  = Pin.cpu.A1
    s7  = Pin.cpu.A4
    s6  = Pin.cpu.B0
    s5  = Pin.cpu.C1
    s4  = Pin.cpu.C0
    s3  = Pin.cpu.C3
    s2  = Pin.cpu.C2
    #s1  = Pin.cpu.A10
    #Setup control pins - outut, push-pull with pull down resistors, init to low
    evenctrl = Pin(Pin.cpu.H0, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)
    oddctrl = Pin(Pin.cpu.H1, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)

    gc.collect()
    #Create Line Sensor object
    sensors = [s2,s3,s4,s5,s6,s7,s8,s9,s10,s11,s12,s13,s14]
    num_sens = len(sensors)
    Line_sensor = LineSensor(sensors,evenctrl,oddctrl)
    button = Pin(Pin.cpu.C13, Pin.IN, Pin.PULL_UP) 
    SENS_LED = Pin(Pin.cpu.C6, Pin.OUT_PP, value=0) #To indicate if calibration is complete or not

    #Line_sensor = Cali_test(Line_sensor,button,LED)
    #Init vars
    Aixi_sum = 0
    Ai_sum = 0
    length = (num_sens - 1)/2
    gc.collect()


    #Setup IMU
    i2c = I2C(1, I2C.CONTROLLER)
    imu = IMU(i2c)
    #Put IMU in config mode and write calibration data
    imu.set_config()
    sleep(0.1)
    imu.write_cal_data('calibration.txt')
    sleep(0.1)
    #Put IMU in fusion mode and make sure it's calibrated
    imu.set_fusion()
    sleep(0.1)
    
    #Initialize out glorious state space model object
    ssmodel = SSModel()
    #Initalize y and u arrays
    u = array('f', [0.0, 0.0])
    y = array('f', [0.0, 0.0, 0.0, 0.0, 0.0])
    mainperiod = 30 #Period that the simulation (and pretty much all of our tasks) runs at

    #Initalize pure pursuit object
    thepursuer = ThePursuer(BASESPEED, ARRIVED, kp_head, ki_head)

    #Initalize obstacle sensor
    obst_sens = Pin(Pin.cpu.B7, Pin.IN, pull=Pin.PULL_DOWN)
    RUN_LED = Pin(Pin.cpu.C10, Pin.OUT_PP, value=0)
    WALL_LED = Pin(Pin.cpu.C11, Pin.OUT_PP, value=0)
    gc.collect()

    # Create shares and queues. See task definitions for descriptions
    
    #Shares
    velo_set = task_share.Share('f', thread_protect=False, name="Motor Speed Set Point")
    imu_off  = task_share.Share('I', thread_protect=False, name="IMU disable flag")
    offset     = task_share.Share('f', thread_protect=False, name="Motor setpoint adjustment from line follower")
    lf_stop    = task_share.Share('I', thread_protect=False, name="Line follow stop flag")
    gc.collect()




    #Queues
    cmd_L    = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Left Motor Command Signal")
    cmd_R    = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Right Motor Command Signal")
    time_L   = task_share.Queue('I', 20, thread_protect=False, overwrite=True, name="Left Motor Time")
    pos_L    = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name="Left Motor Position")
    velo_L   = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name="Left Motor Velocity")
    time_R   = task_share.Queue('I', 20, thread_protect=False, overwrite=True, name="Right Motor Time")
    pos_R    = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name="Right Motor Position")
    velo_R   = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name="Right Motor Velocity")
    Eul_head = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name='Euler heading (in radians) from the IMU')
    yaw_rate = task_share.Queue('f', 20, thread_protect=False, overwrite=True, name='Yaw rate (in radians/s) from the IMU')
    gc.collect()
    #Output variables of Glorious SS model
    X_pos    = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Absolute X Position")
    Y_pos    = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Absolte Y Position")
    p_v_R      = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Total Path Length")
    p_v_L      = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Total Velocity")
    p_head   = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Heading (rads)")
    p_yaw    = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Yaw Rate (rad/s)")
    p_pos_L  = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Path Length - Left Wheel")
    p_pos_R  = task_share.Queue('f', 10, thread_protect=False, overwrite=True, name="Path Length - Right Wheel")
    gc.collect()


    #Set a bunch of default values
    velo_set.put(0.0) #Motor requested speed 0

    imu_off.put(0)

    #Motor ctrl signal to zero
    cmd_L.put(0) 
    cmd_R.put(0)
   
    #Line Follower Stuff
    offset.put(0)
    kp_lf = 1.1
    ki_lf = 0
    lf_stop.put(0) #Startout following the line




    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    Controller    = cotask.Task(Controller_fun, name="Controller", priority=5, period=mainperiod,
                         profile=True, trace=False, shares=(offset, leftencoder, leftmotor, pos_L ,rightencoder, rightmotor, pos_R, t_L, v_L, t_R, v_R, r_ctrl, l_ctrl, velo_L, velo_R, time_L, time_R, velo_set, cmd_L, cmd_R))
    IMU_Interface = cotask.Task(IMU_Interface_fun, name="IMU Interface", priority=4, period=mainperiod,
                            profile=True, trace=False, shares=(imu, Eul_head, yaw_rate, SENS_LED))

    Talker        = cotask.Task(Talker_fun, name="Talker", priority=1, period=10,
                        profile=True, trace=False, shares=(packet, packet_fmt, btcomm, velo_set, kp_lf, ki_lf, time_L, pos_L, velo_L, time_R, pos_R, velo_R, cmd_L, cmd_R, offset, Eul_head, yaw_rate, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw, p_pos_L, p_pos_R))
    
    Pursuer       = cotask.Task(Pursuer_fun, name="Pursuer", priority=3, period=mainperiod,
                            profile=True, trace=False, shares=(WALL_LED, imu_off, obst_sens, velo_set, lf_stop, thepursuer, X_pos, Y_pos, p_head, offset))
    LineFollow    = cotask.Task(LineFollow_fun, name="Line Follower", priority=2, period=mainperiod,
                            profile=True, trace=False, shares=(SENS_LED, length, Aixi_sum, Ai_sum, X_pos, velo_set, lf_stop,kp_lf, ki_lf, offset,Line_sensor))
    
    SS_Simulator  = cotask.Task(SS_Simulator_fun, name="State Simulator", priority=3, period=mainperiod,
                            profile=True, trace=False, shares=(RUN_LED, imu_off, ssmodel, (mainperiod/1000), y, u, Eul_head, velo_L, velo_R, pos_L, pos_R, cmd_L, cmd_R, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw, p_pos_L, p_pos_R))
    #Wall_Detector = cotask.Task(Wall_detect_fun, name="Wall Detector", priority=3, period=mainperiod,
    #                        profile=True, trace=False, shares=(obst_sens, X_pos, Y_pos, velo_set))
    
    
    GarbageCollector = cotask.Task(GarbageCollector_fun, name="Garbage Collect", priority=0, period=mainperiod, profile=True, trace=False)
    gc.collect()
   
    cotask.task_list.append(Controller)
    cotask.task_list.append(IMU_Interface)
    cotask.task_list.append(Talker)
    cotask.task_list.append(SS_Simulator)
    cotask.task_list.append(Pursuer)
    cotask.task_list.append(LineFollow)
    #cotask.task_list.append(Wall_Detector)
    cotask.task_list.append(GarbageCollector)
    gc.collect()

    print('All tasks initialized.')
    print(gc.mem_alloc())
    print(gc.mem_free())

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    imu.init_heading() #Wait until the last possible second to init IMU heading b/c it keeps jumping a few ms after being setup


    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            leftmotor.set_effort(0)
            rightmotor.set_effort(0)
            #Save IMU calibration data
            imu.set_config()
            sleep(0.1)
            imu.read_cal_data('calibration.txt')
            break

    # Print a table of task data and a table of shared information data
    print('\n' + str (cotask.task_list))
    print(task_share.show_all())
    print(Controller.get_trace())
    print(Talker.get_trace())
    print(Pursuer.get_trace())
    #print(Wall_Detector.get_trace())
    print(LineFollow.get_trace())

    print('')
