
import re, time, serial, cv2
import numpy as np
import serial.tools.list_ports

from .logger import Logger
from .photon import Photon
from .camera import Camera

class Lumen():

    def __init__(self, debug=True, topCam = True, botCam = True):
        self._instance = None

        self.log = Logger(debug)

        self._bootCommands = [
            "G90",
            "M260 A112 B1 S1",
            "M260 A109",
            "M260 B48",
            "M260 B27",
            "M260 S1",
            "M260 A112 B2 S1",
            "M260 A109",
            "M260 B48",
            "M260 B27",
            "M260 S1",
            "G0 F50000",
            "M204 T4000"
        ]

        self._preHomeCommands = [
            "M204 T2000"
        ]

        self._postHomeCommands = [
            "M115"
        ]

        self._ser = serial.Serial()
        self._ser.baudrate = 119200
        self._ser.timeout = 1

        self.photon = Photon(self, self.log)

        if topCam:
            self.topCam = Camera(0)

        if botCam:
            self.botCam = Camera(1)

    @classmethod
    def getInstance(cls):
        if not cls._instance:
            cls._instance = Lumen()

        return cls._instance


#####################
# Serial
#####################

    def connect(self):
        if self.scanPorts():
            if self.openSerial():
                self.sendBootCommands()
                return True
            
        return False
    
    def disconnect(self):
        self._ser.close()
        if self._ser.is_open:
            return False
        else:
            return True
    
    def waitForEmptyPlanner(self):
        messages = [
            "M400"
            "M118 E1 done"
        ]

        # send messages
        for i in messages:
            self.send(i)

        #wait for done to arrive with timeout
        start = time.perf_counter()

        while True:
            response = self._ser.readline().decode('utf-8')
            reMatch = re.search("echo: done", response)
            if reMatch is not None:
                break

            if time.perf_counter() - start > 3:
                break

    def goto(self, x=None, y=None, z=None):
        command = "G0"
        if x is not None:
            command = command + " X" + str(x)
        if y is not None:
            command = command + " Y" + str(y)
        if z is not None:
            command = command + " Z" + str(z)

        self.send(command)


    def scanPorts(self):

        comports = serial.tools.list_ports.comports()

        device_id = "0483:5740"

        for port, desc, hwid in sorted(comports):
            if device_id in hwid:
                try:
                    s = serial.Serial(port)
                    s.close()
                    self.log.info("Found motherboard at port: " + " with hwid: " + hwid)
                    self._ser.port = port
                    return True

                except (OSError, serial.SerialException):
                    pass

        return False

    def openSerial(self):
        if self._ser.is_open:
            self.log.info("Serial port already open")
            return True
        
        if self._ser.port != "":
            self._ser.open()
            self._ser.timeout = 1
        else:
            self.log.error("No serial port selected")
            return False

        if self._ser.is_open:
            self.log.info("Connected to machine over serial port: " + self._ser.port)
            self._ser.read_all()
            return True
        else:
            self.log.error("Couldn't open serial port")
            return False
        
    def sendBootCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._bootCommands:
            if not self.send(i):
               self.log.error("Halted sending boot commands because sending failed.")
               break


    def sendPreHomingCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._preHomeCommands:
            if not self.send(i):
               self.log.error("Halted sending pre homing commands because sending failed.")
               break

    def home(self, x = True, y = True, z = True):

        self.log.info("Homing")

        self.sendPreHomingCommands()

        if x and y and z:
            self.send("G28")
        else:
            if x or y or z:
                command = "G28"
                if x:
                    command = command + " X"
                if y:
                    command = command + " Y"
                if z:
                    command = command + " Z"

                self.send(command)
        
        self.sendPostHomingCommands

        self.waitForEmptyPlanner()

    def sendPostHomingCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._postHomeCommands:
            if not self.send(i):
               self.log.error("Halted sending post homing commands because sending failed.")
               break

    def send(self, message):
        # send can return two things
        # it can return bool False if port isnt open
        # or it can respond with marlin's response
        
        #check to see if serial port is open
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode('utf-8')
            self._ser.write(encoded + b'\n')
            resp = self._ser.readline().decode('utf-8')
            return resp
        else:
            self.log.error("Serial port isn't open.")
            return False
        
    def sendBlind(self, message):
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode('utf-8')
            self._ser.write(encoded + b'\n')
            return True
        else:
            self.log.error("Serial port isn't open.")
            return False

    def send_rtn_lines(self, message):
        # send can return two things
        # it can return bool False if port isnt open
        # or it can respond with marlin's response
        
        #check to see if serial port is open
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode('utf-8')
            self._ser.write(encoded + b'\n')
            resp = self._ser.readlines()
            decoded_resp = ""
            i = 0
            while i < len(resp):
                decoded_resp = decoded_resp + resp[i].decode('utf-8')
                i = i + 1
            return decoded_resp
        else:
            self.log.error("Serial port isn't open.")
            return False
        

    def readLeftVac(self): # returns vacuum sensor value for left vac

        try:
            #selects vac 1 through multiplexer
            self.send("M260 A112 B1 S1")

            #read addresses 0x06 0x07 and 0x08 for pressure reading
            self.send("M260 A109 B6 S1")
            msb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            self.send("M260 A109 B7 S1")
            csb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            self.send("M260 A109 B8 S1")
            lsb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            val = msb.group(1)+csb.group(1)+lsb.group(1)

            result = int(val, 16)

            if(result & (1 << 23)):
                result = result - 2**24

            return result
        except Exception as e: 
            print(e)
            return False
        
    def readRightVac(self): # returns vacuum sensor value for left vac

        try:
            #selects vac 1 through multiplexer
            self.send("M260 A112 B2 S1")

            #read addresses 0x06 0x07 and 0x08 for pressure reading
            self.send("M260 A109 B6 S1")
            msb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            self.send("M260 A109 B7 S1")
            csb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            self.send("M260 A109 B8 S1")
            lsb = re.search("data:(..)", self.send("M261 A109 B1 S1"))

            val = msb.group(1)+csb.group(1)+lsb.group(1)

            result = int(val, 16)

            if(result & (1 << 23)):
                result = result - 2**24

            return result
        except Exception as e: 
            print(e)
            return False
            