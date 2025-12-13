from tkinter import *
from tkinter import ttk
import os
import signal
from time import sleep
import subprocess

class RomiDisplay():
    #Tkinter display so we cna see what Romi's doing in real time
    def __init__(self, ser, serial_lock, go_plot, read_stop, write_stop, record_data, recorded_data, Ser_cmds, time_L, time_R, pos_L, velo_L, velo_R, pos_R, cmd_L, cmd_R, Eul_head, yaw_rate, offset, X_pos, Y_pos, p_v_R, p_v_L, p_head, velo_set, p_pos_L, p_pos_R, root):
        
        self.root = root

        self.root.title('Live Romi Data')
        
        #Create window
        mainframe = ttk.Frame(self.root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        self.serial_lock = serial_lock
        self.ser = ser
        self.read_stop = read_stop
        self.write_stop = write_stop
        self.record_data = record_data
        self.recorded_data = recorded_data
        self.Ser_cmds = Ser_cmds
        self.go_plot = go_plot
        
        # Assign all queues as instance variables
        self.pos_L_queue = pos_L
        self.velo_L_queue = velo_L
        self.velo_R_queue = velo_R
        self.pos_R_queue = pos_R
        self.cmd_L_queue = cmd_L
        self.cmd_R_queue = cmd_R
        self.Eul_head_queue = Eul_head
        self.offset_queue = offset
        self.yaw_rate_queue = yaw_rate
        self.p_pos_L_queue = p_pos_L
        self.p_pos_R_queue = p_pos_R
        self.X_pos_queue = X_pos
        self.Y_pos_queue = Y_pos
        self.p_v_R_queue = p_v_R
        self.p_v_L_queue = p_v_L
        self.p_head_queue = p_head
        self.velo_set_queue = velo_set

        
        
        #Init variables
        # Initialize all as StringVar
        self.pos_L = StringVar()
        self.velo_L = StringVar()
        self.velo_R = StringVar()
        self.pos_R = StringVar()
        self.cmd_L = StringVar()
        self.cmd_R = StringVar()
        self.Eul_head = StringVar()
        self.offset = StringVar()
        self.SPD = StringVar()
        self.yaw_rate = StringVar()
        self.X_pos = StringVar()
        self.Y_pos = StringVar()
        self.p_v_R = StringVar()
        self.p_v_L = StringVar()
        self.p_head = StringVar()
        self.velo_set = StringVar()
        self.p_pos_L = StringVar()
        self.p_pos_R = StringVar()
        self.recording = StringVar()

        #Set default values (empty strings)
        self.pos_L.set("")
        self.velo_L.set("")
        self.velo_R.set("")
        self.pos_R.set("")
        self.cmd_L.set("")
        self.cmd_R.set("")
        self.Eul_head.set("")
        self.yaw_rate.set("")
        self.offset.set("")
        self.X_pos.set("")
        self.Y_pos.set("")
        self.p_v_R.set("")
        self.p_v_L.set("")
        self.p_head.set("")
        self.velo_set.set("")
        self.p_pos_L.set("")
        self.p_pos_R.set("")
        self.recording.set("Not Recording")

        self.record_enable = False #Controls whether setting speed and stopping will record data/plot
        
        #Create various "table entries" with variables and labels
        ttk.Button(mainframe, text="Update Code", command=self.update)


        #Control buttons and labels
        #Speed Control
        ttk.Entry(mainframe, textvariable=self.SPD).grid(column=7, row=5, sticky=W)
        ttk.Label(mainframe, text="Speed").grid(column=6, row=5, sticky=W)
        ttk.Button(mainframe, text="Update", command=self.speed).grid(column=8, row=5, sticky=W)
        ttk.Button(mainframe, text="STOP", command=self.stop).grid(column=8, row=6, sticky=W)
        ttk.Entry(mainframe, textvariable=self.SPD).grid(column=7, row=5, sticky=W)
        #Record Data
        ttk.Label(mainframe, textvariable=self.recording).grid(column=7, row=7, sticky=W)
        ttk.Button(mainframe, text="Record Data", command=self.toggle_record).grid(column=8, row=7, sticky=W)
        ttk.Button(mainframe, text="Plot", command=self.start_plotter).grid(column=8, row=8, sticky=W)




        #Line follower offset
        ttk.Label(mainframe, text="Line Follower Offset (in/s)").grid(column=6, row=4, sticky=W)
        ttk.Label(mainframe, textvariable=self.offset).grid(column=7, row=4, sticky=(W))



        # --- Unified Motor & Pose Table ----------------------------------------------
        row0 = 1

        # Headers
        ttk.Label(mainframe, text=" ").grid(column=1, row=row0, sticky=W)
        ttk.Label(mainframe, text="State").grid(column=2, row=row0, sticky=W)
        ttk.Label(mainframe, text="Predicted").grid(column=3, row=row0, sticky=W)
        ttk.Label(mainframe, text="Actual").grid(column=4, row=row0, sticky=W)
        ttk.Label(mainframe, text="Units").grid(column=5, row=row0, sticky=W)

        # --- Left Motor --------------------------------------------------------------
        # Control Signal row (Left Motor label on same row)
        ttk.Label(mainframe, text="Left Motor").grid(column=1, row=row0+1, sticky=W)
        ttk.Label(mainframe, text="Control Signal").grid(column=2, row=row0+1, sticky=W)
        ttk.Label(mainframe, text="-").grid(column=3, row=row0+1, sticky=W)
        ttk.Label(mainframe, textvariable=self.cmd_L).grid(column=4, row=row0+1, sticky=W)
        ttk.Label(mainframe, text="%").grid(column=5, row=row0+1, sticky=W)

        # Velocity row
        ttk.Label(mainframe, text="").grid(column=1, row=row0+2, sticky=W)
        ttk.Label(mainframe, text="Velocity").grid(column=2, row=row0+2, sticky=W)
        ttk.Label(mainframe, textvariable=self.p_v_L).grid(column=3, row=row0+2, sticky=W)
        ttk.Label(mainframe, textvariable=self.velo_L).grid(column=4, row=row0+2, sticky=W)
        ttk.Label(mainframe, text="in/s").grid(column=5, row=row0+2, sticky=W)

        # Displacement row
        ttk.Label(mainframe, text="").grid(column=1, row=row0+3, sticky=W)
        ttk.Label(mainframe, text="Displacement").grid(column=2, row=row0+3, sticky=W)
        ttk.Label(mainframe, textvariable=self.p_pos_L).grid(column=3, row=row0+3, sticky=W)
        ttk.Label(mainframe, textvariable=self.pos_L).grid(column=4, row=row0+3, sticky=W)
        ttk.Label(mainframe, text="in").grid(column=5, row=row0+3, sticky=W)

        # --- Right Motor -------------------------------------------------------------
        # Control Signal row (Right Motor label on same row)
        ttk.Label(mainframe, text="Right Motor").grid(column=1, row=row0+4, sticky=W)
        ttk.Label(mainframe, text="Control Signal").grid(column=2, row=row0+4, sticky=W)
        ttk.Label(mainframe, text="-").grid(column=3, row=row0+4, sticky=W)
        ttk.Label(mainframe, textvariable=self.cmd_R).grid(column=4, row=row0+4, sticky=W)
        ttk.Label(mainframe, text="%").grid(column=5, row=row0+4, sticky=W)

        # Velocity row
        ttk.Label(mainframe, text="").grid(column=1, row=row0+5, sticky=W)
        ttk.Label(mainframe, text="Velocity").grid(column=2, row=row0+5, sticky=W)
        ttk.Label(mainframe, textvariable=self.p_v_R).grid(column=3, row=row0+5, sticky=W)
        ttk.Label(mainframe, textvariable=self.velo_R).grid(column=4, row=row0+5, sticky=W)
        ttk.Label(mainframe, text="in/s").grid(column=5, row=row0+5, sticky=W)

        # Displacement row
        ttk.Label(mainframe, text="").grid(column=1, row=row0+6, sticky=W)
        ttk.Label(mainframe, text="Displacement").grid(column=2, row=row0+6, sticky=W)
        ttk.Label(mainframe, textvariable=self.p_pos_R).grid(column=3, row=row0+6, sticky=W)
        ttk.Label(mainframe, textvariable=self.pos_R).grid(column=4, row=row0+6, sticky=W)
        ttk.Label(mainframe, text="in").grid(column=5, row=row0+6, sticky=W)

        # --- Pose / Position Section -------------------------------------------------
        ttk.Label(mainframe, text="Psi").grid(column=2, row=row0+7, sticky=W)
        ttk.Label(mainframe, textvariable=self.p_head).grid(column=3, row=row0+7, sticky=W)
        ttk.Label(mainframe, textvariable=self.Eul_head).grid(column=4, row=row0+7, sticky=W)
        ttk.Label(mainframe, text="deg").grid(column=5, row=row0+7, sticky=W)

        ttk.Label(mainframe, text="X").grid(column=2, row=row0+8, sticky=W)
        ttk.Label(mainframe, text="-").grid(column=3, row=row0+8, sticky=W)
        ttk.Label(mainframe, textvariable=self.X_pos).grid(column=4, row=row0+8, sticky=W)
        ttk.Label(mainframe, text="inches").grid(column=5, row=row0+8, sticky=W)

        ttk.Label(mainframe, text="Y").grid(column=2, row=row0+9, sticky=W)
        ttk.Label(mainframe, text="-").grid(column=3, row=row0+9, sticky=W)
        ttk.Label(mainframe, textvariable=self.Y_pos).grid(column=4, row=row0+9, sticky=W)
        ttk.Label(mainframe, text="inches").grid(column=5, row=row0+9, sticky=W)
        # ----------------------------------------------------------------------------- 

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(2, weight=1)
        for child in mainframe.winfo_children(): 
            child.grid_configure(padx=5, pady=5)
        
        #Set to check update_display after 5 seconds
        self.root.after(5, self.update_display)


    def update(self):
        with self.serial_lock:
                try:    
                    os.kill(self.putty.pid, signal.SIGTERM)
                except:
                    pass
                #Tell serial com threads to stop reading and writing
                self.read_stop.set()
                self.write_stop.set()
                sleep(0.1)
                #self.ser.close() #Disconnect from serial port
                print('Copying files...')
                command = ["mpremote", "connect", "COM9", "cp", "-r", "./src/.", ":"]
                try:
                    result = subprocess.run(command, capture_output=True, text=True, check=True)
                    print(result.stdout)
                except:
                    print('Did you forget to close PuTTY???')
                #Reconnect to serial port
                #try:
                #    self.ser.open()
                #    print(f"Connected to {self.ser.name}")
                #    self.ser.reset_input_buffer()
                #except:
                #    print(f"Error opening serial port: {e}")
                #    exit()
                #Resume reading and writing
                self.read_stop.clear()
                self.write_stop.clear()
                self.putty = subprocess.Popen([r'c:\Program Files\PuTTY\putty.exe', "-load", 'Default Settings'])
                #Open PuTTY

    def update_display(self):
        roundlen = 2
        """Check each queue; if data exists, update its corresponding StringVar."""
        if not self.pos_L_queue.empty(): self.pos_L.set(round(self.pos_L_queue.get(), roundlen))
        if not self.velo_L_queue.empty(): self.velo_L.set(round(self.velo_L_queue.get(), roundlen))
        if not self.velo_R_queue.empty(): self.velo_R.set(round(self.velo_R_queue.get(), roundlen))
        if not self.pos_R_queue.empty(): self.pos_R.set(round(self.pos_R_queue.get(), roundlen))
        if not self.cmd_L_queue.empty(): self.cmd_L.set(round(self.cmd_L_queue.get(), roundlen))
        if not self.cmd_R_queue.empty(): self.cmd_R.set(round(self.cmd_R_queue.get(), roundlen))
        if not self.Eul_head_queue.empty(): self.Eul_head.set(round(self.Eul_head_queue.get()*57.29746, roundlen)) #Convert rad to deg
        if not self.yaw_rate_queue.empty(): self.yaw_rate.set(round(self.yaw_rate_queue.get()*57.29746, roundlen)) #Convert rad to deg
        if not self.offset_queue.empty(): self.offset.set(round(self.offset_queue.get(), roundlen))
        if not self.X_pos_queue.empty(): self.X_pos.set(round(self.X_pos_queue.get(), roundlen))
        if not self.Y_pos_queue.empty(): self.Y_pos.set(round(self.Y_pos_queue.get(), roundlen))
        if not self.p_v_R_queue.empty(): self.p_v_R.set(round(self.p_v_R_queue.get(), roundlen))
        if not self.p_v_L_queue.empty(): self.p_v_L.set(round(self.p_v_L_queue.get(), roundlen))
        if not self.p_head_queue.empty(): self.p_head.set(round(self.p_head_queue.get()*57.29746, roundlen))
        if not self.velo_set_queue.empty(): self.velo_set.set(round(self.velo_set_queue.get(), roundlen))
        if not self.p_pos_L_queue.empty(): self.p_pos_L.set(round(self.p_pos_L_queue.get(), roundlen))
        if not self.p_pos_R_queue.empty(): self.p_pos_R.set(round(self.p_pos_R_queue.get(), roundlen))


        self.root.after(5, self.update_display)
    
    def speed(self):
        if self.record_enable is True:
            self.record_data.set() #Start Recording data
        command = '$SPD' + str(self.SPD.get())
        self.Ser_cmds.put(command)

    def stop(self):
        if self.record_enable is True:
            self.start_plotter() #If data logging enabled, start the plotter
        command = '$SPD' + '0'
        self.Ser_cmds.put(command)

    def toggle_record(self):
        if self.record_enable is True:
            self.record_enable = False
            self.recording.set('Data Logging Off')
        else:
            self.record_enable = True
            for k in self.recorded_data.keys():
                self.recorded_data[k] = []
            self.recording.set('Data Logging On')

    def start_plotter(self):
        if not self.go_plot.is_set():
            self.record_data.clear()
            self.go_plot.set()

