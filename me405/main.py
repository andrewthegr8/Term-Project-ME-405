"""Main control script for the Romi differential-drive robot.

This module is the top-level firmware entry point for the ME 405 term
project. It wires together all of the hardware drivers (motors, encoders,
IMU, line sensor, Bluetooth, etc.), configures the cooperative task
scheduler (:mod:`cotask`), and starts a set of periodic tasks that
implement the robot's behavior.

Overview
--------

On startup, the script performs the following steps:

* Configure timers, pins, and peripherals for:
  - Motor drivers and encoders
  - Bluetooth UART link
  - Line sensor array
  - IMU (BNO055)
  - Obstacle sensor and status LEDs
* Create :class:`task_share.Share` and :class:`task_share.Queue` instances
  used to exchange data between tasks.
* Optionally runs :func:`Cali_test` to calibrate the line sensor array.
* Construct cooperative tasks for:
  - Bluetooth communication (:func:`Talker_fun`)
  - IMU interface (:func:`IMU_Interface_fun`)
  - Motor PI control (:func:`Controller_fun`)
  - Line following (:func:`LineFollow_fun`)
  - Pure pursuit path tracking (:func:`Pursuer_fun`)
  - State-space model simulation (:func:`SS_Simulator_fun`)
  - Periodic garbage collection (:func:`GarbageCollector_fun`)
* Register those tasks with :mod:`cotask` and run the priority scheduler
  in a loop until a *keyboard interrupt* is received.

When a keyboard interrupt occurs (typically from a user pressing Ctrl-C
via the REPL), the scheduler is halted, all motors are stopped, the IMU
calibration coefficents are saved to flash memory, and the program prints
debugging statistics from the scheduler as well as the final state of each
queue before exiting.

.. note::
    Many of the task implementations use finite state machines (FSMs) to
    manage their internal operation. Diagrams for each FSM are included.

.. note::
    Many of the tasks have persistent variables/buffers that are allocated
    outside of the task function on startup and passed in the ``share``
    tuple to minimize heap churn.

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

# Import custom drivers and controller classes
from Encoder import Encoder
from Motor import Motor
from LineSensor import LineSensor
from BTComm import BTComm
from IMU import IMU
from SSModel import SSModel
from PIController import PIController
from ThePursuer import ThePursuer

# Tunable parameters
MAXDELTA = const(25) #Maximum change in motor duty cycle per control tick.
ARRIVED = const(2.5) #Distance threshold (inches) used by the pure-pursuit path planner to
#decide when a waypoint has been "arrived" at.


def Talker_fun(shares):
    """Bluetooth communication task.

    This task is responsible for sending and receiving data over the
    Bluetooth link. It uses the :class:`BTComm` helper class to cooperatively parse
    incoming commands and to build and ship telemetry packets.

    .. note::
        Telemetry packets are sent in a structured binary format using
        :mod:`ustruct` to minimize bandwidth usage.

    The task operates as a small state machine:

    * **State 0** – Listen for incoming characters. If a complete command
      is available, transition to state 1. Otherwise, if enough samples
      are present in the various telemetry queues, pack them into a
      structured binary packet and send (every other iteration) over
      Bluetooth.
    * **State 1** – Interpret a fully received command. Currently
      supports a ``$SPDxx.x`` command to change the requested wheel
      speed. After processing, transitions back to state 0.

    .. tip::
        Only every other packet is sent to cut down on taks run time
        But, all available telemetry samples are still packed into a
        packet each time to avoid queue overflows.

    .. tip::
        This task only checks certain queues for available samples
        before trying to build a telemetry packet. This is because
        several groups of quues are filled by the same task, so checking
        every single queue is redundant.

    .. warning::
        Since the IMU yaw rate is currently not implemented, this task
        publishes the velocity setpoint (``velo_set``) in its place.
        The PC side code expects this, but this packet modification
        is not well documented.

    Args:
        shares: Tuple of share/queue objects and configuration values, in
            the following order:

            * ``packet`` (:class:`bytearray`): Outgoing telemetry buffer.
            * ``packet_fmt`` (:class:`str`): ``ustruct`` format string.
            * ``btcomm`` (:class:`BTComm`): Bluetooth communications object.
            * ``velo_set`` (:class:`task_share.Share`): Requested wheel speed.
            * ``kp_lf``, ``ki_lf`` (:class:`float`): Line-follow controller gains. **DEPRACTATED**
            * ``time_L``, ``pos_L``, ``velo_L`` (:class:`task_share.Queue`):
              Left wheel time, position, and velocity.
            * ``time_R``, ``pos_R``, ``velo_R`` (:class:`task_share.Queue`):
              Right wheel time, position, and velocity.
            * ``cmd_L``, ``cmd_R`` (:class:`task_share.Queue`):
              Commanded efforts for left and right motors.
            * ``offset`` (:class:`task_share.Share`): Line-follow/point tracking speed offset.
            * ``Eul_head`` (:class:`task_share.Queue`): Euler heading from IMU.
            * ``yaw_rate`` (:class:`task_share.Queue`): Yaw rate from IMU. **Currently always 0**
            * ``X_pos``, ``Y_pos`` (:class:`task_share.Queue`): Estimated X/Y position.
            * ``p_v_R``, ``p_v_L`` (:class:`task_share.Queue`):
              State-space path length and velocity.
            * ``p_head``, ``p_yaw`` (:class:`task_share.Queue`):
              State-space heading and yaw rate.
            * ``p_pos_L``, ``p_pos_R`` (:class:`task_share.Queue`):
              State-space - path length per wheel.

    """
    # Unpack shares and queues
    (packet, packet_fmt, btcomm, velo_set, kp_lf, ki_lf, time_L, pos_L,
     velo_L, time_R, pos_R, velo_R, cmd_L, cmd_R, offset, Eul_head,
     yaw_rate, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw, p_pos_L,
     p_pos_R) = shares

    state = 0
    sendit = True

    while True:
        if state == 0:
            # Listen for input; if a full command is ready, go interpret it
            if btcomm.check():
                state = 1
            else:
                # Only ship data if all critical queues have enough samples
                if (time_L.many() and
                    time_R.many() and
                    cmd_L.many() and
                    Eul_head.many() and
                        p_pos_L.many()):
                    ustruct.pack_into(
                        packet_fmt,
                        packet,
                        3,
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
                        p_pos_R.get(),
                    )
                    # Only send every other packet to throttle bandwidth
                    if sendit:
                        btcomm.ship(packet)
                        sendit = False
                    else:
                        sendit = True

        elif state == 1:
            # Interpret a fully received command string
            rawcmd = btcomm.get_command()
            if not rawcmd:
                pass
            elif rawcmd[0] == "$":
                # Example: "$SPD1.5" sets wheel speed to 1.5 in/s
                if rawcmd[1:4] == "SPD":
                    try:
                        velo_set.put(float(rawcmd[4:]))
                    except Exception:
                        pass
            state = 0

        yield state


def IMU_Interface_fun(shares):
    """IMU interface task.

    This task reads the current heading from the IMU and publishes it
    into the shared queue for telemetry and state estimation.

    .. note::
        The current implementation only reads the heading angle. The initial
        itertion also read the yaw rate, but to minimize exceuption time,
        this feature was removed. A zero value is currently published for yaw
        rate so an empty queue doesn't block data transmission.

    Args:
        shares: Tuple ``(imu, Eul_head, yaw_rate, SENS_LED)`` where:

            * ``imu`` (:class:`IMU`): IMU driver instance.
            * ``Eul_head`` (:class:`task_share.Queue`): Euler heading (rad).
            * ``yaw_rate`` (:class:`task_share.Queue`): Yaw rate (rad/s).
            * ``SENS_LED`` (:class:`pyb.Pin`): Status LED (currently unused).
    """
    imu, Eul_head, yaw_rate, SENS_LED = shares
    while True:
        Eul_head.put(imu.get_heading())
        # Yaw rate is currently unused, but left for future expansion
        yaw_rate.put(0)
        yield


def SS_Simulator_fun(shares):
    """State-space simulation task.

    This task runs a continous-time state-space model of the Romi robot
    in parallel with the real hardware. It uses the latest measured
    velocities, positions, and IMU heading to feed back into the model,
    uses the motor commands as inputs, and publishes the estimated state to a set of
    queues.

    .. note::
        The IMU feedback can be disabled by setting the ``imu_off``
        share to 1. This feature was added becuase the IMU readings
        were being corrupted when the robot was close to the "wall."

    .. tip::
        This task also toggles ``RUN_LED`` each iteration to show
        that the scheduler is active.

    Args:
        shares: Tuple of objects in the following order:

            * ``RUN_LED`` (:class:`pyb.Pin`): Toggles each run to show activity.
            * ``imu_off`` (:class:`task_share.Share`): Flag to disable IMU
              feedback
            * ``ssmodel`` (:class:`SSModel`): State-space model instance.
            * ``mainperiod`` (:class:`float`): Simulation step period (s).
            * ``y`` (:class:`array`): Measurement vector buffer.
            * ``u`` (:class:`array`): Input vector buffer (motor voltages).
            * ``Eul_head`` (:class:`task_share.Queue`): IMU heading.
            * ``velo_L``, ``velo_R`` (:class:`task_share.Queue`):
              Left/right wheel velocities.
            * ``pos_L``, ``pos_R`` (:class:`task_share.Queue`):
              Left/right wheel positions.
            * ``cmd_L``, ``cmd_R`` (:class:`task_share.Queue`):
              Commanded motor efforts.
            * ``X_pos``, ``Y_pos`` (:class:`task_share.Queue`):
              Estimated absolute position.
            * ``p_v_R``, ``p_v_L`` (:class:`task_share.Queue`):
              Estimated path length and velocity.
            * ``p_head``, ``p_yaw`` (:class:`task_share.Queue`):
              Estimated heading and yaw rate.
            * ``p_pos_L``, ``p_pos_R`` (:class:`task_share.Queue`):
              Estimated path length per wheel.
    """
    (RUN_LED, imu_off, ssmodel, mainperiod, y, u, Eul_head, velo_L, velo_R,
     pos_L, pos_R, cmd_L, cmd_R, X_pos, Y_pos, p_v_R, p_v_L, p_head, p_yaw,
     p_pos_L, p_pos_R) = shares

    while True:
        # Blink the run LED to show activity
        RUN_LED.value(0 if RUN_LED.value() else 1)

        # Optionally disable heading correction when IMU is considered unreliable
        if imu_off.get() == 1:
            ssmodel.L_Psi = 0

        # Build input vector from motor commands (assumes ~9V supply)
        u[0] = 0.09 * cmd_L.view()
        u[1] = 0.09 * cmd_R.view()

        # Build measurement vector from latest sensor data
        y[0] = Eul_head.view()
        y[1] = velo_L.view()
        y[2] = velo_R.view()
        y[3] = pos_L.view()
        y[4] = pos_R.view()

        # Advance the state-space model
        ssmodel.RK4_step(u, y, mainperiod)

        # Publish estimated outputs
        yhat = ssmodel.y_hat_fcn()
        p_v_L.put(yhat[0])
        p_v_R.put(yhat[1])
        p_head.put(yhat[2])
        p_pos_L.put(yhat[3])
        p_pos_R.put(yhat[4])
        X_pos.put(yhat[5])
        # Invert Y for convenience of the chosen coordinate frame
        Y_pos.put(-yhat[6])
        p_yaw.put(0)
        yield


def LineFollow_fun(shares):
    """Line follower task.

    This task implements a PI controller that adjusts the left/right motor
    speed setpoints based on the position of a line under the reflective
    sensor array. It computes the centroid of the sensor readings to form
    an error signal and writes a speed offset into the ``offset`` share.

    It also monitors the ``lf_stop`` share to enter a disabled state when
    :func:`Pursuer_fun` requests the line follower to stop.

    .. note::
       For this implementation, a small forward speed bias is added so that
       Romi starts to turn when it approaches the ``Y`` intersection.

    .. tip::
       The line follower implements anti-windup by resetting the integral
       error sum when the requested speed is zero.

    .. graphviz::
       :caption: LineFollow_fun finite state machine

       digraph LineFollowFSM {
         rankdir=LR;
         node [shape=circle];

         S0 [label="Active follow"];
         S1 [label="Follower stopped"];

         // Active -> Stopped
         S0 -> S1 [
           label="lf_stop.get() == 1\\n"
                 "SENS_LED.value(0)"
         ];

         // Active -> Active (normal line following)
         S0 -> S0 [
           label="Line_sensor.read()\\n"
                 "Aixi_sum,Ai_sum,error\\n"
                 "kp_lf,ki_lf,esum\\n"
                 "velo_set,offset\\n"
                 "X_pos.view() bias\\n"
                 "SENS_LED.value(1)"
         ];

         // Stopped -> Stopped (no exit in code)
         S1 -> S1 [
           label="lf_stop.get() == 1\\n"
                 "SENS_LED.value(0)"
         ];
       }

    :param shares: Tuple in the following order:

        * ``SENS_LED`` (:class:`pyb.Pin`): LED indicating line follower
          activity.
        * ``length`` (:class:`float`): Half-width of the sensor index
          range used in centroid computation.
        * ``Aixi_sum`` (:class:`float`): Working variable for centroid
          numerator (unused outside).
        * ``Ai_sum`` (:class:`float`): Working variable for centroid
          denominator (unused outside).
        * ``X_pos`` (:class:`task_share.Queue`): Estimated X position.
        * ``velo_set`` (:class:`task_share.Share`): Requested average speed.
        * ``lf_stop`` (:class:`task_share.Share`): Flag to disable the
          line follower.
        * ``kp_lf``, ``ki_lf`` (:class:`float`): PI gains for line following.
        * ``offset`` (:class:`task_share.Share`): Speed offset written
          to the motor controller task.
        * ``Line_sensor`` (:class:`LineSensor`): Calibrated line sensor
          driver instance.
    """
    (SENS_LED, length, Aixi_sum, Ai_sum, X_pos, velo_set, lf_stop, kp_lf,
     ki_lf, offset, Line_sensor) = shares

    state = 0
    esum = 0
    time_last = 0

    while True:
        if state == 0:
            if lf_stop.get() == 1:
                SENS_LED.value(0)
                state = 1
                yield state

            if time_last == 0:
                time_last = ticks_ms()

            readings = Line_sensor.read()
            Aixi_sum = 0
            Ai_sum = 0

            for idx, val in enumerate(readings):
                Aixi_sum += val * (idx - length)
                Ai_sum += val

            if Aixi_sum == 0:
                error = 0
            else:
                error = Aixi_sum / sum(readings)

            # P control
            p_ctrl = kp_lf * error

            time_now = ticks_ms()
            dt = ticks_diff(time_now, time_last) / 1000
            time_last = time_now

            # I control (with anti-windup when speed command is zero)
            if int(velo_set.get()) == 0:
                esum = 0
            else:
                esum += error * dt
            i_ctrl = ki_lf * esum

            ctrl_sig = p_ctrl + i_ctrl

            # Small bias after robot has moved a certain distance
            if X_pos.view() > 25:
                ctrl_sig += 8.5

            offset.put(ctrl_sig)
            SENS_LED.value(1)

        elif state == 1:
            SENS_LED.value(0)
            # Do nothing until lf_stop is cleared
            pass

        yield state


def Pursuer_fun(shares):
    """Point seeking autonomous driving task.

    This task uses a simple controller to guide the robot
    along a sequence of target points. It controls both the 
    rotational velocity (via ``offset``) and forward speed (via ``velo_set``).

    When the robot passes a certain X position, it disables
    the line follower and begins pursuing waypoints. It also monitors
    an obstacle sensor to detect walls; when a wall is detected, it
    immediately advances to the next waypoint.

    .. note::
        The task only monitors the obstacle sensor when the robot is
        near the "wall" obstacle to avoid having the sensor triggered
        on the solo cups. Once a wall is detected, it sets a flag
        to ignore further detections to prevent repeated triggering.

    Args:
        shares: Tuple in the following order:

            * ``WALL_LED`` (:class:`pyb.Pin`): LED indicating wall detection.
            * ``imu_off`` (:class:`task_share.Share`): Flag to disable IMU
              feedback once a wall is hit.
            * ``obst_sens`` (:class:`pyb.Pin`): Digital obstacle sensor.
            * ``velo_set`` (:class:`task_share.Share`): Requested wheel speed.
            * ``lf_stop`` (:class:`task_share.Share`): Flag to stop the line
              follower.
            * ``thepursuer`` (:class:`ThePursuer`): Pure pursuit controller.
            * ``p_X``, ``p_Y`` (:class:`task_share.Queue`): Estimated X/Y from
              state-space model.
            * ``p_head`` (:class:`task_share.Queue`): Estimated heading.
            * ``offset`` (:class:`task_share.Share`): Commanded speed offset
              for the motor controller.
    """
    (WALL_LED, imu_off, obst_sens, velo_set, lf_stop, thepursuer, p_X, p_Y,
     p_head, offset) = shares

    state = 0
    wall = False
    wall_hit = False

    while True:
        if state == 0:
            # When the robot passes a certain point, switch from line follower
            if p_X.view() >= 31.25:
                lf_stop.put(1)
                state = 1

        elif state == 1:
            X = X_pos.view()
            Y = Y_pos.view()
            if X < 3 and Y < 10 and not wall_hit:
                if obst_sens.value() == 0:
                    wall = True
                    wall_hit = True
                    WALL_LED.value(1)
                    # imu_off.put(1)
            else:
                wall = False

            off, speed = thepursuer.get_offset(
                p_X.view(),
                p_Y.view(),
                p_head.view(),
                wall,
            )

            if velo_set.get() != 0:
                velo_set.put(speed)
                offset.put(off)
            else:
                velo_set.put(0)
                offset.put(0)

        yield state


def Controller_fun(shares):
    """Motor controller task (PI control for both wheels).

    This task implements a closed-loop velocity PI controller for each motor
    using encoder feedback. It uses :class:`PIController` instances to compute
    the control signals based on the requested speed (from ``velo_set`` share).

    When ``velo_set`` is zero, the task enters a "stopped" state where both
    motors are held at zero effort. Upon receiving a non-zero speed command,
    the encoders and controllers are re-initialized before resuming normal  
    operation.

    .. note::
        It limits the rate of change of the control signal to ``MAXDELTA``
        (a customizable constant) per control period to prevent
        sudden jumps in motor effort and avoid wheel slippage.
    
    .. note::
        ``offset`` is used to adjust the left/right wheel velocities
        differentially to control rotational velocity. A positive offset
        increases the left wheel velocity and decreases the right wheel velocity.
    
    .. image:: controllerfsm.png
        :alt: Finite state machine diagram for the motor controller task.
        :width: 400px
        :align: center


    Args:
        shares: Tuple in the following order:

            * ``offset`` (:class:`task_share.Share`): Speed offset from line
              follower / pursuer.
            * ``leftencoder``, ``rightencoder`` (:class:`Encoder`):
              Encoder drivers.
            * ``leftmotor``, ``rightmotor`` (:class:`Motor`): Motor drivers.
            * ``pos_L``, ``pos_R`` (:class:`task_share.Queue`): Position
              queues for logging.
            * ``t_L``, ``t_R`` (:class:`int`): Scratch variables for timestamps.
            * ``v_L``, ``v_R`` (:class:`float`): Scratch variables for velocity.
            * ``r_ctrl``, ``l_ctrl`` (:class:`PIController`): Motor PI controllers.
            * ``velo_L``, ``velo_R`` (:class:`task_share.Queue`):
              Velocity logging queues.
            * ``time_L``, ``time_R`` (:class:`task_share.Queue`):
              Timestamp logging queues.
            * ``velo_set`` (:class:`task_share.Share`): Requested speed.
            * ``cmd_L``, ``cmd_R`` (:class:`task_share.Queue`):
              Commanded efforts written for logging/state space model.
    """
    (offset, leftencoder, leftmotor, pos_L, rightencoder, rightmotor, pos_R,
     t_L, v_L, t_R, v_R, r_ctrl, l_ctrl, velo_L, velo_R, time_L, time_R,
     velo_set, cmd_L, cmd_R) = shares

    state = 0
    lastsig_L = 0.0
    lastsig_R = 0.0
    delta = 0.0

    while True:
        # Always update encoder readings
        leftencoder.update()
        t_L = time.ticks_ms()
        rightencoder.update()
        t_R = time.ticks_ms()
        v_L = leftencoder.get_velocity()
        v_R = rightencoder.get_velocity()

        if state == 0:
            # Initialize controller timing once data is available
            l_ctrl.last_time = t_L
            r_ctrl.last_time = t_R
            state = 1

        elif state == 1:
            # Normal closed-loop speed control
            cmd = velo_set.get()
            if cmd == 0.0:
                cmd_L.put(0)
                leftmotor.set_effort(0)
                cmd_R.put(0)
                rightmotor.set_effort(0)
                state = 2
            else:
                off = offset.get()

                # Left motor PI with slew-rate limiting
                l_sig = l_ctrl.get_ctrl_sig((cmd + off), v_L, t_L)
                delta = l_sig - lastsig_L
                if delta > MAXDELTA:
                    l_sig = lastsig_L + MAXDELTA
                elif delta < -MAXDELTA:
                    l_sig = lastsig_L - MAXDELTA
                lastsig_L = l_sig
                leftmotor.set_effort(l_sig)
                cmd_L.put(l_sig)

                # Right motor PI with slew-rate limiting
                r_sig = r_ctrl.get_ctrl_sig((cmd - off), v_R, t_R)
                delta = r_sig - lastsig_R
                if delta > MAXDELTA:
                    r_sig = lastsig_R + MAXDELTA
                elif delta < -MAXDELTA:
                    r_sig = lastsig_R - MAXDELTA
                lastsig_R = r_sig
                rightmotor.set_effort(r_sig)
                cmd_R.put(r_sig)

        elif state == 2:
            # Stopped state: keep logging, wait for non-zero command
            cmd = velo_set.get()
            cmd_L.put(0)
            cmd_R.put(0)
            if cmd != 0.0:
                leftencoder.zero()
                rightencoder.zero()
                l_ctrl.reset(t_L)
                r_ctrl.reset(t_R)
                state = 1

        # Always log position, velocity, and time
        pos_L.put(leftencoder.get_position())
        velo_L.put(v_L)
        time_L.put(t_L)
        pos_R.put(rightencoder.get_position())
        velo_R.put(v_R)
        time_R.put(t_R)

        yield state


def GarbageCollector_fun():
    """Periodic garbage collection task.

    This very low-priority task runs :func:`gc.collect` periodically to
    help reduce memory fragmentation in the MicroPython heap.
    """
    while True:
        gc.collect()
        yield


def Cali_test(Line_sensor, button, SENS_LED):
    """Blocking calibration helper for the line sensor.

    This function runs an interactive calibration sequence for the line
    sensor array:

    1. Wait for the user to press the blue button over a black surface
       and record the black calibration values.
    2. Wait for the user to press the button over a white surface and
       record the white calibration values.
    3. Wait for a final button press to begin normal operation.

    Args:
        Line_sensor: :class:`LineSensor` instance to be calibrated.
        button: :class:`pyb.Pin` configured as a pushbutton input.
        SENS_LED: :class:`pyb.Pin` used as a status LED.

    Returns:
        LineSensor: The same sensor instance, after calibration.
    """
    SENS_LED.high()
    print("Begin blocking calibration sequence")
    print("Press blue button to calibrate on black.")
    while button.value() == 1:
        pass
    print("Calibrating!")
    black = Line_sensor.cal_black()
    print("Black calibration array")
    print(black)
    sleep(1)
    print("Press blue button to calibrate on white.")
    while button.value() == 1:
        pass
    white = Line_sensor.cal_white()
    print("White calibration array")
    print(white)
    sleep(1)
    print("Press blue button to begin.")
    while button.value() == 1:
        pass
    SENS_LED.low()
    return Line_sensor


# This code creates all the needed shares and queues then starts the tasks.
# The tasks run until a keyboard interrupt, at which time the scheduler stops
# and diagnostic information about tasks, shares, and queues is printed.
if __name__ == "__main__":
    print(
        "Here we go!\r\n"
        "Press Ctrl-C to stop and show diagnostics."
    )

    # MOTOR & ENCODER SETUP
    # Setup Timers
    tim1 = Timer(1, freq=10000)  # For left motor encoder
    tim2 = Timer(2, freq=10000)  # For right motor encoder
    tim3 = Timer(3, freq=10000)  # For left motor PWM
    tim4 = Timer(4, freq=10000)  # For right motor PWM

    # Remap pins for Timer2
    Pin(Pin.cpu.A0, mode=Pin.ANALOG)
    Pin(Pin.cpu.A1, mode=Pin.ANALOG)
    Pin(Pin.cpu.A15, mode=Pin.ALT, alt=1)
    Pin(Pin.cpu.B3, mode=Pin.ALT, alt=1)

    # Setup motor and encoder objects
    leftmotor = Motor(Pin.cpu.B4, Pin.cpu.B10, Pin.cpu.C8, tim3, 1)
    leftmotor.enable()
    rightmotor = Motor(Pin.cpu.B6, Pin.cpu.B11, Pin.cpu.C7, tim4, 1)
    rightmotor.enable()
    rightencoder = Encoder(tim2, Pin.cpu.A15, Pin.cpu.B3)
    leftencoder = Encoder(tim1, Pin.cpu.A8, Pin.cpu.A9)

    gc.collect()

    # Init controller objects
    r_ctrl = PIController(0.6, 15)
    l_ctrl = PIController(0.6, 15)

    # Init internal variables for controller generator
    t_L = 0
    v_L = 0.0
    t_R = 0
    v_R = 0.0

    # TALKER SETUP
    serial_device = UART(5, 460800)
    btcomm = BTComm(serial_device)

    packet_fmt = "<II" + "f" * 17
    packet = bytearray(3 + ustruct.calcsize(packet_fmt))
    packet[0] = 0xAA
    packet[1] = 0x55
    packet[2] = 0x00

    gc.collect()

    # LINE SENSOR SETUP
    s14 = Pin.cpu.C5
    s13 = Pin.cpu.B1
    s12 = Pin.cpu.C4
    s11 = Pin.cpu.A7
    s10 = Pin.cpu.A6
    s9 = Pin.cpu.A0
    s8 = Pin.cpu.A1
    s7 = Pin.cpu.A4
    s6 = Pin.cpu.B0
    s5 = Pin.cpu.C1
    s4 = Pin.cpu.C0
    s3 = Pin.cpu.C3
    s2 = Pin.cpu.C2

    evenctrl = Pin(Pin.cpu.H0, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)
    oddctrl = Pin(Pin.cpu.H1, mode=Pin.OUT_PP, pull=Pin.PULL_DOWN, value=0)

    gc.collect()
    sensors = [s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14]
    num_sens = len(sensors)
    Line_sensor = LineSensor(sensors, evenctrl, oddctrl)
    button = Pin(Pin.cpu.C13, Pin.IN, Pin.PULL_UP)
    SENS_LED = Pin(Pin.cpu.C6, Pin.OUT_PP, value=0)

    Aixi_sum = 0
    Ai_sum = 0
    length = (num_sens - 1) / 2
    gc.collect()

    # IMU SETUP
    i2c = I2C(1, I2C.CONTROLLER)
    imu = IMU(i2c)
    imu.set_config()
    sleep(0.1)
    imu.write_cal_data("calibration.txt")
    sleep(0.1)
    imu.set_fusion()
    sleep(0.1)

    # State-space model setup
    ssmodel = SSModel()
    u = array("f", [0.0, 0.0])
    y = array("f", [0.0, 0.0, 0.0, 0.0, 0.0])
    mainperiod = 30  # ms

    # Pure pursuit setup (assumes BASESPEED, kp_head, ki_head are defined elsewhere)
    thepursuer = ThePursuer(BASESPEED, ARRIVED, kp_head, ki_head)

    # Obstacle sensor and LEDs
    obst_sens = Pin(Pin.cpu.B7, Pin.IN, pull=Pin.PULL_DOWN)
    RUN_LED = Pin(Pin.cpu.C10, Pin.OUT_PP, value=0)
    WALL_LED = Pin(Pin.cpu.C11, Pin.OUT_PP, value=0)
    gc.collect()

    # SHARES
    velo_set = task_share.Share("f", thread_protect=False, name="Motor Speed Set Point")
    imu_off = task_share.Share("I", thread_protect=False, name="IMU disable flag")
    offset = task_share.Share(
        "f",
        thread_protect=False,
        name="Motor setpoint adjustment from line follower",
    )
    lf_stop = task_share.Share("I", thread_protect=False, name="Line follow stop flag")
    gc.collect()

    # QUEUES
    cmd_L = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Left Motor Command Signal"
    )
    cmd_R = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Right Motor Command Signal"
    )
    time_L = task_share.Queue(
        "I", 20, thread_protect=False, overwrite=True, name="Left Motor Time"
    )
    pos_L = task_share.Queue(
        "f", 20, thread_protect=False, overwrite=True, name="Left Motor Position"
    )
    velo_L = task_share.Queue(
        "f", 20, thread_protect=False, overwrite=True, name="Left Motor Velocity"
    )
    time_R = task_share.Queue(
        "I", 20, thread_protect=False, overwrite=True, name="Right Motor Time"
    )
    pos_R = task_share.Queue(
        "f", 20, thread_protect=False, overwrite=True, name="Right Motor Position"
    )
    velo_R = task_share.Queue(
        "f", 20, thread_protect=False, overwrite=True, name="Right Motor Velocity"
    )
    Eul_head = task_share.Queue(
        "f",
        20,
        thread_protect=False,
        overwrite=True,
        name="Euler heading (in radians) from the IMU",
    )
    yaw_rate = task_share.Queue(
        "f",
        20,
        thread_protect=False,
        overwrite=True,
        name="Yaw rate (in radians/s) from the IMU",
    )
    gc.collect()

    X_pos = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Absolute X Position"
    )
    Y_pos = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Absolte Y Position"
    )
    p_v_R = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Total Path Length"
    )
    p_v_L = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Total Velocity"
    )
    p_head = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Heading (rads)"
    )
    p_yaw = task_share.Queue(
        "f", 10, thread_protect=False, overwrite=True, name="Yaw Rate (rad/s)"
    )
    p_pos_L = task_share.Queue(
        "f",
        10,
        thread_protect=False,
        overwrite=True,
        name="Path Length - Left Wheel",
    )
    p_pos_R = task_share.Queue(
        "f",
        10,
        thread_protect=False,
        overwrite=True,
        name="Path Length - Right Wheel",
    )
    gc.collect()

    # Default values
    velo_set.put(0.0)
    imu_off.put(0)
    cmd_L.put(0)
    cmd_R.put(0)
    offset.put(0)
    kp_lf = 1.1
    ki_lf = 0
    lf_stop.put(0)

    # TASK CREATION
    Controller = cotask.Task(
        Controller_fun,
        name="Controller",
        priority=5,
        period=mainperiod,
        profile=True,
        trace=False,
        shares=(
            offset,
            leftencoder,
            leftmotor,
            pos_L,
            rightencoder,
            rightmotor,
            pos_R,
            t_L,
            v_L,
            t_R,
            v_R,
            r_ctrl,
            l_ctrl,
            velo_L,
            velo_R,
            time_L,
            time_R,
            velo_set,
            cmd_L,
            cmd_R,
        ),
    )
    IMU_Interface = cotask.Task(
        IMU_Interface_fun,
        name="IMU Interface",
        priority=4,
        period=mainperiod,
        profile=True,
        trace=False,
        shares=(imu, Eul_head, yaw_rate, SENS_LED),
    )
    Talker = cotask.Task(
        Talker_fun,
        name="Talker",
        priority=1,
        period=10,
        profile=True,
        trace=False,
        shares=(
            packet,
            packet_fmt,
            btcomm,
            velo_set,
            kp_lf,
            ki_lf,
            time_L,
            pos_L,
            velo_L,
            time_R,
            pos_R,
            velo_R,
            cmd_L,
            cmd_R,
            offset,
            Eul_head,
            yaw_rate,
            X_pos,
            Y_pos,
            p_v_R,
            p_v_L,
            p_head,
            p_yaw,
            p_pos_L,
            p_pos_R,
        ),
    )
    Pursuer = cotask.Task(
        Pursuer_fun,
        name="Pursuer",
        priority=3,
        period=mainperiod,
        profile=True,
        trace=False,
        shares=(WALL_LED, imu_off, obst_sens, velo_set, lf_stop, thepursuer,
                X_pos, Y_pos, p_head, offset),
    )
    LineFollow = cotask.Task(
        LineFollow_fun,
        name="Line Follower",
        priority=2,
        period=mainperiod,
        profile=True,
        trace=False,
        shares=(SENS_LED, length, Aixi_sum, Ai_sum, X_pos, velo_set, lf_stop,
                kp_lf, ki_lf, offset, Line_sensor),
    )
    SS_Simulator = cotask.Task(
        SS_Simulator_fun,
        name="State Simulator",
        priority=3,
        period=mainperiod,
        profile=True,
        trace=False,
        shares=(
            RUN_LED,
            imu_off,
            ssmodel,
            (mainperiod / 1000),
            y,
            u,
            Eul_head,
            velo_L,
            velo_R,
            pos_L,
            pos_R,
            cmd_L,
            cmd_R,
            X_pos,
            Y_pos,
            p_v_R,
            p_v_L,
            p_head,
            p_yaw,
            p_pos_L,
            p_pos_R,
        ),
    )
    GarbageCollector = cotask.Task(
        GarbageCollector_fun,
        name="Garbage Collect",
        priority=0,
        period=mainperiod,
        profile=True,
        trace=False,
    )
    gc.collect()

    cotask.task_list.append(Controller)
    cotask.task_list.append(IMU_Interface)
    cotask.task_list.append(Talker)
    cotask.task_list.append(SS_Simulator)
    cotask.task_list.append(Pursuer)
    cotask.task_list.append(LineFollow)
    cotask.task_list.append(GarbageCollector)
    gc.collect()

    print("All tasks initialized.")
    print(gc.mem_alloc())
    print(gc.mem_free())

    gc.collect()

    imu.init_heading()

    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            leftmotor.set_effort(0)
            rightmotor.set_effort(0)
            imu.set_config()
            sleep(0.1)
            imu.read_cal_data("calibration.txt")
            break

    print("\n" + str(cotask.task_list))
    print(task_share.show_all())
    print(Controller.get_trace())
    print(Talker.get_trace())
    print(Pursuer.get_trace())
    print(LineFollow.get_trace())
    print("")