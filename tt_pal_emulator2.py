from threading import Thread, Lock
from time import sleep, ctime, asctime

echo_queries = False

class Serial:
    def __init__(self, port="PortName", baudrate=9600, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.target = "none"  # Options are "tt", "pal", or "controller"

        # Create dictionaries of valid commands and the time (seconds) they take to execute
        self.tt_commands = {"233": 3,  # ttHome
                            "234": 2,  # ttMoveAbs
                            "232": 0.5,  # ttServo
                            "212": 2,  # ttMoving Query
                            "238": 3}  # ttStop

        self.pal_commands = {":01060D001010CC\r\n": 1,  # palHome
                             ":01060D030001E8\r\n": 1,  # palSet_position_1
                             ":01060D030002E7\r\n": 1,  # palSet_position_2
                             ":01060D001000DC\r\n": 1,  # palCSTR_off
                             ":01060D001008D4\r\n": 2,  # palCSTR_on
                             ":01039007000164\r\n": 1,  # palQuery_moving
                             ":01039005000166\r\n": 1,  # palQuery_home
                             ":01050427FF00D0\r\n": 1}  # enableModbus

        self.command_buffer = list()
        self.process_time = list()
        self.returned_message = list()
        self.axis_busy_state = list()
        self.ready_for_next_command = list()
        self.thread_list = list()

        if port == "COM3":
            self.target = "pal"
            self.command_buffer.append(list())
            self.axis_busy_state.append(False)
            self.ready_for_next_command.append(True)
            self.process_time.append(0)
            th = Thread(target=self.axis_server, args=(0,))
            th.daemon = True
            self.thread_list.append(th)
            self.thread_list[0].start()

        if port == "COM4":
            self.target = "tt"
            for i in range(3):
                self.command_buffer.append(list())
                self.axis_busy_state.append(False)
                self.ready_for_next_command.append(True)
                self.process_time.append(0)
                th = Thread(target=self.axis_server, args=(i,))
                th.daemon = True
                self.thread_list.append(th)
                self.thread_list[i].start()

        if port == "COM5":
            self.target = "controller"


    def write(self, msg):
        axis = 0
        if self.target == "tt":
            # Extract command from serial message
            msg_command = msg[3:6]
            # If command is valid AND not a query, add to command buffer
            if msg_command in self.tt_commands:
                # Determine relevant axis in message
                if msg[7] == "1":
                    axis = 0
                if msg[7] == "2":
                    axis = 1
                if msg[7] == "4":
                    axis = 2
                # If command is not a query, add command and command duration to command_buffer
                if msg_command != "212":
                    self.command_buffer[axis].append((msg_command,
                                                 list(self.tt_commands.values())[
                                                     list(self.tt_commands.keys()).index(msg_command)]))
                    self.returned_message.append(msg_command)
                    print("Message sent: {} at time: {}".format(msg, ctime()))
                # If command is a query for busy state, add busy state to returned message
                else:
                    self.returned_message.append(msg_command)
                    self.returned_message.append(self.axis_busy_state[axis])
            else:
                self.returned_message.append("invalid tt command")

        if self.target == "pal":
            msg_command = msg
            if msg_command in self.pal_commands:
                # If command is valid AND not a query, add to command buffer
                if msg_command != ":01039007000164\r\n":
                    self.command_buffer[0].append((msg_command,
                                                list(self.pal_commands.values())[
                                                    list(self.pal_commands.keys()).index(msg_command)]))
                    self.returned_message.append(msg_command)
                    print("Message sent: {} at time: {}".format(msg, ctime()))
                # If command is a query for busy state, add busy state to returned message
                else:
                    self.returned_message.append(msg_command)
                    self.returned_message.append(self.axis_busy_state[0])
            else:
                self.returned_message.append("invalid pal command")


    def readline(self):
        msg = self.returned_message[0]
        # If command is a query for busy state, return busy state instead of normal message echo
        if msg == "212" or msg == ":01039007000164\r\n":
            if echo_queries:
                print("Echo message: ", self.returned_message)
            msg = self.returned_message[1]
            del self.returned_message[0:2]
        else:
            print("Echo message: ", msg)
            del self.returned_message[0:1]
        return msg


    def axis_server(self, axis=0):
        while True:
            # Check if command exists in buffer and axis is ready to execute next command
            if self.command_buffer[axis] and self.ready_for_next_command[axis]:
                print("\nStarting command {} for {} axis {} at  {}\n".format(self.command_buffer[axis][0],
                                                                         self.target,
                                                                         axis,
                                                                         ctime()))
                self.axis_busy_state[axis] = True
                self.ready_for_next_command[axis] = False
                self.process_time[axis] = self.command_buffer[axis][0][1]
                sleep(self.process_time[axis])
                print("\nCompleted command {} for {} axis {} at  {}\n".format(self.command_buffer[axis][0],
                                                                         self.target,
                                                                         axis,
                                                                         ctime()))
                del self.command_buffer[axis][0]
                self.ready_for_next_command[axis] = True
                if not self.command_buffer[axis]:
                    self.axis_busy_state[axis] = False


channel1 = Serial(port="COM4")
print("Opening channel 1: ", ctime())
channel1.write("!9923301")
unused = channel1.readline()


channel1.write("!9923304")
unused = channel1.readline()

channel1.write("!9923304")
unused = channel1.readline()

channel2 = Serial(port="COM3")
print("Opening channel 2: ", ctime())
channel2.write(":01060D001008D4\r\n")
unused = channel2.readline()

channel2.write(":01060D001008D4\r\n")
unused = channel2.readline()

channel2.write(":01060D001000DC\r\n")
unused = channel2.readline()

channel1.write("!9921201")
busy1a = channel1.readline()
channel1.write("!9921202")
busy1b = channel1.readline()
channel1.write("!9921204")
busy1c = channel1.readline()
channel2.write(":01039007000164\r\n")
busy2 = channel2.readline()
while (busy1a or busy1b or busy1c or busy2):
    # print("Busy: {} ... Channel 1a: {}... Channel 1b: {}... Channel 1c: {}... Channel 2: {}".format(
    #     ctime(), busy1a, busy1b, busy1c, busy2))
    sleep(0.5)
    channel1.write("!9921201")
    busy1a = channel1.readline()
    channel1.write("!9921202")
    busy1b = channel1.readline()
    channel1.write("!9921204")
    busy1c = channel1.readline()
    channel2.write(":01039007000164\r\n")
    busy2 = channel2.readline()

print("Ended: ", ctime())
print(channel2.tt_commands["234"])
