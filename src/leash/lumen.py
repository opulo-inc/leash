"""Lumen object, containing all other subsystems
"""

from .logger import Logger
from .serial import SerialManager

from .photon import Photon
from .camera import Camera
from .pump import Pump

class Lumen():

    def __init__(self, debug=True, topCam = False, botCam = False):

        self.log = Logger(debug)

        self.sm = SerialManager()
        self.photon = Photon(self.sm, self.log)

        self.leftPump = Pump("LEFT", self.sm, self.log)
        self.rightPump = Pump("RIGHT", self.sm, self.log)

        if topCam:
            self.topCam = Camera(0)

        if botCam:
            self.botCam = Camera(1)


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


#####################
# Serial
#####################

    def connect(self):
        if self.sm.scanPorts():
            if self.sm.openSerial():
                self.sendBootCommands()
                return True
            
        return False
    
    def disconnect(self):
        self.sm._ser.close()
        if self.sm._ser.is_open:
            return False
        else:
            return True
        
    def finishMoves(self):

        self.sm.clearQueue()
    

    def goto(self, x=None, y=None, z=None, a=None, b=None):
        command = "G0"
        if x is not None:
            command = command + " X" + str(x)
        if y is not None:
            command = command + " Y" + str(y)
        if z is not None:
            command = command + " Z" + str(z)
        if z is not None:
            command = command + " A" + str(a)
        if z is not None:
            command = command + " B" + str(b)

        self.send(command)

        
    def sendBootCommands(self):

        for i in self._bootCommands:
            if not self.sm.send(i):
               self.log.error("Halted sending boot commands because sending failed.")
               break


    def sendPreHomingCommands(self):

        for i in self._preHomeCommands:
            if not self.sm.send(i):
               self.log.error("Halted sending pre homing commands because sending failed.")
               break

    def home(self, x = True, y = True, z = True):

        self.log.info("Homing")

        self.sendPreHomingCommands()

        if x and y and z:
            self.sm.send("G28")
        else:
            if x or y or z:
                command = "G28"
                if x:
                    command = command + " X"
                if y:
                    command = command + " Y"
                if z:
                    command = command + " Z"

                self.sm.send(command)
        
        self.sendPostHomingCommands()

    def sendPostHomingCommands(self):

        for i in self._postHomeCommands:
            if not self.sm.send(i):
               self.log.error("Halted sending post homing commands because sending failed.")
               break
        
    def safeZ(self):
        self.goto(z=31.5)
