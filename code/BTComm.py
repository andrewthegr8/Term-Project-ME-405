#Class for communicating using serial via a bluetooth module.
#Having a seperate class for this is maybe slightly less memory and time effiecient (more lines of code),
#But the main script was getting crowded
import micropython

class BTComm:
    def __init__(self, serial_device):
        #Initializer function. inits class variables and handles serial communications
        self.serial_device = serial_device
        #self._line          = str()
        self.command       = str() #Decoded commands to be intrepreted
        self._buf          = bytearray(24) #Buffer for individual characters 
        self._idx          = 0 #Index to keep track of where we are in the buffer     



    #def handshake(self,command):
    #    #Send command handshake over serial
    #    padding = b'\x00'*(self.packet_length-3-len(command)) #Add padding so our glorious packet is the right length
    #    #***^^^ THIS ASSUMES COMMAND IS LESS THAT 36 BYTES!
    #    data = self.sync + b'\xFF' + command.encode('utf-8') + padding
    #    self.serial_device.write(data)

    @micropython.native
    def check(self):
        #Check for data, maintain buffer, send completed lines of data4
        #Returns [True, command] if a complete line was recieved
        #Otherwise, returns false
        """! MUCH IS BORROWED FROM DR RIDGLEY'S CODE (and ChatGPT)
        This is run within a task function to watch for characters
        coming through a serial port. As characters are received, it assembles
        them into a line and makes a reference to the line available when the
        user has pressed Enter.
        """
            
        if self.serial_device.any():
            b = self.serial_device.read(1)[0]
            if b == 13:   # If carriage return, command is complete!
                self.command = self._buf[:self._idx].decode('utf-8') #Decode what we have in the buffer
                self._idx = 0 #Reset index to zero
                return True
            elif b == 10: #New line '\n'. Ignore
                pass
            elif b == 8 and self._idx: #For backspace, just move the index back one
                self._idx -= 1
            elif self._idx < len(self._buf): #As long as buffer isn't full, add to the buffer
                self._buf[self._idx] = b
                self._idx += 1
        return False #Return false unless new command is availables
    
    @micropython.native
    def get_command(self):
        #Returns most recent command recieved over serial
        return self.command

    @micropython.native     
    def ship(self, packet):
        #Send pre-built packet
        self.serial_device.write(memoryview(packet)) #send off the data!
        #Not sure why memoryview() is necessary but chat recommended and I figured it couldn't hurt

