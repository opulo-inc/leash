"""Manager for serial communications
"""

import serial.tools.list_ports
import serial, time, re

class SerialManager():

    def __init__(self, log):

        self._ser = serial.Serial()
        self._ser.baudrate = 119200
        self._ser.timeout = 1

        self.log = log

    def clearQueue(self, timeout=3):
        messages = [
            "M400",
            "M118 E1 done"
        ]

        # send messages
        for i in messages:
            response = self.send(i)
            reMatch = re.search("echo:done", response)
            if reMatch is not None:
                return True

        #wait for done to arrive with timeout
        start = time.perf_counter()

        while True:
            response = self._ser.readline().decode('utf-8')
            reMatch = re.search("echo:done", response)
            if reMatch is not None:
                return True

            if time.perf_counter() - start > timeout:
                return False
            

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

        self.log.error("Was unable to find a connected Lumen")
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
            self.log.info("Connected to Lumen over serial port: " + self._ser.port)
            self._ser.read_all()
            return True
        else:
            self.log.error("Couldn't open serial port")
            return False
        
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