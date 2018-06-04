from threading import Thread
from time import sleep, ctime, asctime


class Serial:
    def __init__(self, port="PortName", baudrate=9600, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.target = "none"  # Options are "tt", "pal", or "controller"

        # Create dictionaries of valid commands and the time (seconds) they take to execute
        self.tt_commands = {"233": 1,  # ttHome
                            "234": 2,  # ttMoveAbs
                            "232": 0.5,  # ttServo
                            "212": 0.1,  # ttMoving Query
                            "238": 0.1}  # ttStop

        self.pal_commands = {":01060D001010CC\r\n": 1,  # palHome
                             ":01060D030001E8\r\n": 1,  # palSet_position_1
                             ":01060D030002E7\r\n": 1,  # palSet_position_2
                             ":01060D001000DC\r\n": 1,  # palCSTR_off
                             ":01060D001008D4\r\n": 5,  # palCSTR_on
                             ":01039007000164\r\n": 1,  # palQuery_moving
                             ":01039005000166\r\n": 1,  # palQuery_home
                             ":01050427FF00D0\r\n": 1}  # enableModbus

        if port=="COM3":
            self.target = "pal"
            self.command_buffer_ax1 = list()
            self.returned_messages_ax1 = list()
            self.busy_ax1 = False
            self.ready_for_next_command_ax1 = True
            self.process_time_ax1 = 0
            th1 = Thread(target=self.ax1_server)
            th1.daemon = True
            th1.start()   
        if port=="COM4":
            self.target = "tt"
            self.command_buffer_ax1 = list()
            self.returned_messages_ax1 = list()
            self.busy_ax1 = False
            self.ready_for_next_command_ax1 = True
            self.process_time_ax1 = 0
            self.command_buffer_ax2 = list()
            self.returned_messages_ax2 = list()
            self.busy_ax2 = False
            self.ready_for_next_command_ax2 = True
            self.process_time_ax2 = 0
            self.command_buffer_ax3 = list()
            self.returned_messages_ax3 = list()
            self.busy_ax3 = False
            self.ready_for_next_command_ax3 = True
            self.process_time_ax3 = 0
            th1 = Thread(target=self.ax1_server)
            th1.daemon = True
            th2 = Thread(target=self.ax2_server)
            th2.daemon = True
            th3 = Thread(target=self.ax3_server)
            th3.daemon = True
            th1.start()
            th2.start()
            th3.start()
        if port=="COM5":
            self.target = "controller"
        

    def write(self, msg):
        # If command is valid, add to command buffer
        if self.target == "tt":
            msg_command = msg[3:6]
            if msg_command in self.tt_commands:
                # check to see which acis and behave apprpriately...
                if ...
                
                self.command_buffer.append((msg_command,
                                            list(self.tt_commands.values())[
                                                list(self.tt_commands.keys()).index(msg_command)]))
                self.returned_messages.append(msg_command)
                # Remove all query commands from command_buffer
                if msg_command == "212":
                    del self.command_buffer[-1]
            else:
                self.returned_messages.append("invalid tt command")
        if self.target == "pal":
            msg_command = msg
            if msg_command in self.pal_commands:
                self.command_buffer.append((msg_command,
                                            list(self.pal_commands.values())[
                                                list(self.pal_commands.keys()).index(msg_command)]))
                self.returned_messages.append(msg_command)
                # Remove all query commands from command_buffer
                if msg_command == ":01039007000164\r\n":
                    del self.command_buffer[-1]
            else:
                self.returned_messages.append("invalid pal command")


    def readline(self):
        msg = self.returned_messages[0]
        if msg == "212" or msg == ":01039007000164\r\n":
            msg = self.busy
        del self.returned_messages[0]
        return msg


    def ax1_server(self):
        while True:
            if self.command_buffer_ax1 and self.ready_for_next_command_ax1:
                self.busy_ax1 = True
                self.ready_for_next_command_ax1 = False
                self.process_time_ax1 = self.command_buffer_ax1[0][1]
                del self.command_buffer_ax1[0]
                print(
                    "\nStarting new {} task for duration {} at time {}\n".format(self.target, self.process_time_ax1, ctime()))
                sleep(self.process_time_ax1)
                self.ready_for_next_command_ax1 = True
                if not self.command_buffer_ax1:
                    self.busy_ax1 = False
                    
    
    def ax2_server(self):
        while True:
            if self.command_buffer_ax2 and self.ready_for_next_command_ax2:
                self.busy_ax2 = True
                self.ready_for_next_command_ax2 = False
                self.process_time_ax2 = self.command_buffer_ax2[0][1]
                del self.command_buffer_ax2[0]
                print(
                    "\nStarting new {} task for duration {} at time {}\n".format(self.target, self.process_time_ax2, ctime()))
                sleep(self.process_time_ax2)
                self.ready_for_next_command_ax2 = True
                if not self.command_buffer_ax2:
                    self.busy_ax2 = False


    def ax3_server(self):
        while True:
            if self.command_buffer_ax3 and self.ready_for_next_command_ax3:
                self.busy_ax3 = True
                self.ready_for_next_command_ax3 = False
                self.process_time_ax3 = self.command_buffer_ax3[0][1]
                del self.command_buffer_ax3[0]
                print(
                    "\nStarting new {} task for duration {} at time {}\n".format(self.target, self.process_time_ax3, ctime()))
                sleep(self.process_time_ax3)
                self.ready_for_next_command_ax3 = True
                if not self.command_buffer_ax3:
                    self.busy_ax3 = False


    def newPrintThread(self):
        while True:
            if self.command_buffer and self.ready_for_next_command:
                self.busy = True
                self.ready_for_next_command = False
                self.print_time = self.command_buffer[0][1]
                del self.command_buffer[0]
                print(
                    "\nStarting new {} task for duration {} at time {}\n".format(self.target, self.print_time, ctime()))
                sleep(self.print_time)
                self.ready_for_next_command = True
                if not self.command_buffer:
                    self.busy = False


channel1 = Serial()
print("Opening channel 1 and sending print: ", ctime())
channel1.write("!99233")
unused = channel1.readline()
print(unused)
print("Print started: ", ctime(), "\n")

channel2 = Serial()
print("Opening channel 2 and sending print: ", ctime())
channel2.write(":01060D001008D4\r\n")
unused = channel2.readline()
print(unused)
print("Print started: ", ctime(), "\n")
channel2.write(":01060D001008D4\r\n")
unused = channel2.readline()
print(unused)
print("Adding 2nd PAL command to channel 2 buffer: ", ctime(), "\n")
channel2.write(":01060D001000DC\r\n")
unused = channel2.readline()
print(unused)
print("Adding 3rd PAL command to channel 2 buffer: ", ctime(), "\n")

channel1.write("!99212")
busy1 = channel1.readline()
channel2.write(":01039007000164\r\n")
busy2 = channel2.readline()
while (busy1 or busy2):
    print("Busy: {} ... Channel 1: {}... Channel 2: {}".format(ctime(), busy1, busy2))
    sleep(0.5)
    channel1.write("!99212")
    busy1 = channel1.readline()
    channel2.write(":01039007000164\r\n")
    busy2 = channel2.readline()

print("Ended: ", ctime())
print(channel2.tt_commands["234"])
