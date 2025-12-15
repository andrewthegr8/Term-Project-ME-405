import serial
from serial.threaded import LineReader,ReaderThread
from time import sleep
import time
import subprocess
from matplotlib import pyplot as plt
import numpy as np
import csv
from queue import Queue, Empty
import threading
import os
import signal
import struct
from RomiDisplay import RomiDisplay
from tkinter import *
from GoatedPlotter import GoatedPlotter


#Class definition for threaded serial reader.
#This should alwasy be recieving serial input even while the script is doing other stuff

class StupidError(Exception):
    def __init__(self, message="I couldn't be bothered to be more specific."):
        self.message = message
        super().__init__(self.message)

class CommError(Exception):
    def __init__(self, message="Serial communication error"):
        self.message = message
        super().__init__(self.message)

def SerialReader(ser, record_data, recorded_data, time_L, time_R, pos_L, velo_L, velo_R, pos_R, cmd_L, cmd_R, Eul_head, yaw_rate, offset, X_pos, Y_pos, p_v_R, p_v_L, p_head, velo_set, p_pos_L, p_pos_R):
#Serial Reader Thread! 
#Constantly recieves and decodes serial data
    sync = b'\xAA\x55'
    format = '<IIfffffffffffffffff'
    packet_length = struct.calcsize(format) + 3
    buffer = bytearray()
    while True:
        if read_stop.is_set():
            sleep(0.05)
            continue
        with serial_lock:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting) #Get everything from the serial buffer
            else:
                data = False

        if data:
            buffer.extend(data) #Add data to the end of the buffer
            while True: #Run until all data is interpreted
                # Find sync byte
                idx = buffer.find(sync)
                #If we can't find sync byte delete all the buffer except the last byte in case it's first half of sync
                if idx < 0:
                    if len(buffer) > 1:
                        del buffer[:-1]
                    break

                #If we did find sync, Do we have enough for full frame?
                #If not, delete whatever's before the sync
                if not len(buffer[idx:]) >= packet_length:
                    del buffer[:idx]   # drop justuff before sync
                    break

                #If we're here, we have a full packet! Yay!
                #See if we have a handshake or not
                if buffer[idx+2] == 0x00: #normal pack of data
                    packet = buffer[idx+3:idx+packet_length] #Grab useful data (ignoring sync and type bits)
                    data = struct.unpack(format, packet)
                    time_L.put(data[0])
                    time_R.put(data[1])
                    pos_L.put(data[2])
                    velo_L.put(data[3])
                    velo_R.put(data[4])
                    pos_R.put(data[5])
                    cmd_L.put(data[6])
                    cmd_R.put(data[7])
                    Eul_head.put(data[8])
                    yaw_rate.put(data[9])
                    offset.put(data[10])
                    X_pos.put(data[11])
                    Y_pos.put(data[12])
                    p_v_R.put(data[13])
                    p_v_L.put(data[14])
                    p_head.put(data[15])
                    velo_set.put(data[16])
                    p_pos_L.put(data[17])
                    p_pos_R.put(data[18])
                    if record_data.is_set():
                        recorded_data["time_L"].append(data[0])
                        recorded_data["time_R"].append(data[1])
                        recorded_data["pos_L"].append(data[2])
                        recorded_data["velo_L"].append(data[3])
                        recorded_data["velo_R"].append(data[4])
                        recorded_data["pos_R"].append(data[5])
                        recorded_data["cmd_L"].append(data[6])
                        recorded_data["cmd_R"].append(data[7])
                        recorded_data["Eul_head"].append(data[8])
                        recorded_data["yaw_rate"].append(data[9])
                        recorded_data["offset"].append(data[10])
                        recorded_data["X_pos"].append(data[11])
                        recorded_data["Y_pos"].append(data[12])
                        recorded_data["p_v_R"].append(data[13])
                        recorded_data["p_v_L"].append(data[14])
                        recorded_data["p_head"].append(data[15])
                        recorded_data["velo_set"].append(data[16])
                        recorded_data["p_pos_L"].append(data[17])
                        recorded_data["p_pos_R"].append(data[18])

                elif buffer[idx+2] == 0xFF: #Handshake data
                    packet = buffer[idx+3:idx+packet_length].rstrip(b'\x00') #Grab useful data (ignoring sync and type bits and stripping padding)
   
                del buffer[:idx + packet_length]   
        sleep(0.01)
    

def SerialWriter(ser,Ser_cmds):
    #Serial writer thread
    #Send command when needed
    while True:
        if write_stop.is_set():
            sleep(0.05)
            continue
        try:
            command = Ser_cmds.get(timeout=0.05)
        except Empty:
            continue
        print(f"Sending {command}")
        with serial_lock: #Get lock and write command
            ser.write((command + '\r\n').encode('utf-8'))
            ser.flush()       

def PlotMeSomeData():
    pass

#Setup dictionary for recorded data
recorded_data = {
    "time_L": [],
    "time_R": [],
    "pos_L": [],
    "velo_L": [],
    "velo_R": [],
    "pos_R": [],
    "cmd_L": [],
    "cmd_R": [],
    "Eul_head": [],
    "yaw_rate": [],
    "offset": [],
    "X_pos": [],
    "Y_pos": [],
    "p_v_R": [],
    "p_v_L": [],
    "p_head": [],
    "velo_set": [],
    "p_pos_L": [],
    "p_pos_R": []
}

#Setup queues for multi-threading
time_L = Queue()
time_R = Queue()
pos_L = Queue()
velo_L = Queue()
velo_R = Queue()
pos_R = Queue()
cmd_L = Queue()
cmd_R = Queue()
Eul_head = Queue()
yaw_rate = Queue()
offset = Queue()
X_pos = Queue()
Y_pos = Queue()
p_v_R = Queue()
p_v_L = Queue()
p_head = Queue()
velo_set = Queue()
p_pos_L = Queue()
p_pos_R = Queue()
Ser_cmds = Queue()


#Thread coordination flags
record_data = threading.Event()
record_data.clear()
read_stop = threading.Event()
read_stop.clear()
write_stop = threading.Event()
write_stop.clear()
go_plot = threading.Event()
go_plot.clear()
serial_lock = threading.Lock()

#Open Bluetooth COM Port
try:
        ser = serial.Serial('COM13', 460800, timeout=1)
        print(f"Connected to {ser.name}")
except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        exit()

#Setup tkinter live display
root = Tk()
disp = RomiDisplay(ser, serial_lock, go_plot, read_stop, write_stop, record_data, recorded_data, Ser_cmds, time_L, time_R, pos_L, velo_L, velo_R, pos_R, cmd_L, cmd_R, Eul_head, yaw_rate, offset, X_pos, Y_pos, p_v_R, p_v_L, p_head, velo_set, p_pos_L, p_pos_R, root)


#Setup multithreading and start reading from serial port
SerRead = threading.Thread(target=SerialReader, args=(ser, record_data, recorded_data, time_L, time_R, pos_L, velo_L, velo_R, pos_R, cmd_L, cmd_R, Eul_head, yaw_rate, offset, X_pos, Y_pos, p_v_R, p_v_L, p_head, velo_set, p_pos_L, p_pos_R), daemon=True)
SerRead.start()
SerWrite = threading.Thread(target=SerialWriter, args=(ser,Ser_cmds), daemon=True)
SerWrite.start()
GoatPlot = threading.Thread(target=GoatedPlotter, args=(recorded_data,go_plot), daemon=True)
GoatPlot.start()




#Loop endlessly in tkinter loop
print("Romi Whisperer V0")
root.mainloop()