

import re
from ..base import util
from .photon import Photon
import serial
import serial.tools.list_ports

class Lumen():

    def __init__(self):
        self._instance = None

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
            "G0 F35000"
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

        self.photon = Photon(self)

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
                return True
        return False

    def scanPorts(self):

        comports = serial.tools.list_ports.comports()

        device_id = "0483:5740"

        for port, desc, hwid in sorted(comports):
            if device_id in hwid:
                try:
                    s = serial.Serial(port)
                    s.close()
                    util.info("Found motherboard at port: " + " with hwid: " + hwid)
                    self._ser.port = port
                    return True

                except (OSError, serial.SerialException):
                    pass

        return False

    def openSerial(self):
        if self._ser.is_open:
            util.info("Serial port already open")
            return True
        
        if self._ser.port != "":
            self._ser.open()
            self._ser.timeout = 0.25
        else:
            util.error("No serial port selected")
            return False

        if self._ser.is_open:
            util.info("Connected to machine over serial port: " + self._ser.port)
            self._ser.read_all()
            return True
        else:
            util.error("Couldn't open serial port")
            return False

    def disconnect(self):
        self._ser.close()
        if self._ser.is_open:
            return False
        else:
            return True
        
    def sendBootCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._bootCommands:
            if not self.send(i):
               util.error("Halted sending boot commands because sending failed.")
               break

        self.closeSerial()

    def sendPreHomingCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._preHomeCommands:
            if not self.send(i):
               util.error("Halted sending pre homing commands because sending failed.")
               break

        self.closeSerial()

    def sendPostHomingCommands(self):

        if not self._ser.is_open:
            self.openSerial()

        for i in self._postHomeCommands:
            if not self.send(i):
               util.error("Halted sending post homing commands because sending failed.")
               break

        self.closeSerial()

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
            print(str(resp))
            return resp
        else:
            print("Serial port isn't open.")
            return False
        
    def sendBlind(self, message):
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode('utf-8')
            self._ser.write(encoded + b'\n')
            return True
        else:
            print("Serial port isn't open.")
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
            print(str(resp))
            decoded_resp = ""
            i = 0
            while i < len(resp):
                print(str(resp[i]))
                decoded_resp = decoded_resp + resp[i].decode('utf-8')
                i = i + 1
            return decoded_resp
        else:
            print("Serial port isn't open.")
            return False
        

    def readLeftVac(self): # returns vacuum sensor value for left vac

        self.sendBootCommands();

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

        print("regex concat")
        print(val)

        val = int("0x" + val, 16)

        print("convert from hex")
        print(val)
        print(str(bin(val)))

        sign = (val >> 23) & 1

        print("sign")
        print(sign)

        if (sign):
            sign = 1
        else:
            sign = -1

        
        print(sign)

        val &= ~(1 << 23)

        print("clearing msb")
        print(val)
        print(str(bin(val)))

        return val * sign

    def readRightVac(self): # returns vacuum sensor value for right vac
        
        self.sendBootCommands();

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
        
        print("regex concat")
        print(val)

        val = int("0x" + val, 16)

        print("convert from hex")
        print(val)
        print(str(bin(val)))

        sign = (val >> 23) & 1

        print("sign")
        print(sign)

        if (sign):
            sign = 1
        else:
            sign = -1

        
        print(sign)

        val &= ~(1 << 23)

        print("clearing msb")
        print(val)
        print(str(bin(val)))

        return val * sign