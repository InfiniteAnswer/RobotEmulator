from threading import Thread
from time import sleep, ctime, asctime


class Serial:
    def __init__(self, port="PortName", baudrate=9600, timeout=2):
        self.print_time = 0
        self.command_buffer = list()
        self.returned_messages = list()
        self.busy = False
        self.ready_for_next_command = True
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

        th = Thread(target=self.newPrintThread)
        th.daemon = True
        th.start()

    def write(self, msg):

        # Set the target type (only allowed once)
        if self.target == "none":
            if msg[0] == "!":
                self.target = "tt"
            elif msg[0] == ":":
                self.target = "pal"
            else:
                print("Unknown Target")

        # If command is valid, add to command buffer
        if self.target == "tt":
            msg_command = msg[3:6]
            if msg_command in self.tt_commands:
                self.command_buffer.append((msg_command,
                                            list(self.tt_commands.values())[
                                                list(self.tt_commands.keys()).index(msg_command)]))
                self.returned_messages.append(msg_command)
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
