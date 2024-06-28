"""Manager for controlling and reading pressure from pumps
"""

import re

class Pump():

    def __init__(self, index, sm, log):
        
        self.index = index
        self.sm = sm
        self.log = log

    def getPressure(self):

        if self.index == "LEFT":
            try:
                #selects vac 1 through multiplexer
                self.sm.send("M260 A112 B1 S1")

                #read addresses 0x06 0x07 and 0x08 for pressure reading
                self.sm.send("M260 A109 B6 S1")
                msb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                self.sm.send("M260 A109 B7 S1")
                csb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                self.sm.send("M260 A109 B8 S1")
                lsb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                val = msb.group(1)+csb.group(1)+lsb.group(1)

                result = int(val, 16)

                if(result & (1 << 23)):
                    result = result - 2**24

                return result
            except Exception as e: 
                print(e)
                return False

        elif self.index == "RIGHT":

            try:
                #selects vac 1 through multiplexer
                self.sm.send("M260 A112 B2 S1")

                #read addresses 0x06 0x07 and 0x08 for pressure reading
                self.sm.send("M260 A109 B6 S1")
                msb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                self.sm.send("M260 A109 B7 S1")
                csb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                self.sm.send("M260 A109 B8 S1")
                lsb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

                val = msb.group(1)+csb.group(1)+lsb.group(1)

                result = int(val, 16)

                if(result & (1 << 23)):
                    result = result - 2**24

                return result
            except Exception as e: 
                print(e)
                return False
            
    def getTemperature(self):

        try:
            if self.index == "LEFT":
                #selects vac 1 through multiplexer
                self.sm.send("M260 A112 B1 S1")
            elif self.index == "RIGHT":
                self.sm.send("M260 A112 B2 S1")

            # Assuming sensor is an object or interface to communicate with the sensor
            
            # Read REG0x09 and REG0x0A
            self.sm.send("M260 A109 B9 S1")
            REG0x09 = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            self.sm.send("M260 A109 B10 S1")
            REG0x0A = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))
            
            # Calculate the temperature ADC value
            N = REG0x09 * 256 + REG0x0A
            
            # Determine if temperature is positive or negative
            if N < 2**15:
                # Temperature is positive
                temperature = N / 256.0
            else:
                # Temperature is negative, apply the formula
                temperature = (N - 2**16) / 256.0
            
            return temperature
    
        except Exception as e: 
            print(e)
            return False

    def off(self):
        if self.index == "LEFT":
            self.sm.send("M107")
            self.sm.send("M107 P1")

        elif self.index == "RIGHT":
            self.sm.send("M107 P2")
            self.sm.send("M107 P3")


    def on(self):
        if self.index == "LEFT":
            # turn on pump
            self.sm.send("M106")
            # turn on valve
            self.sm.send("M106 P1 S255")
            self.sm.send("G4 50")
            self.sm.send("M106 P1 S150")

        elif self.index == "RIGHT":
            #turn on pump
            self.sm.send("M106 P2 S255")
            #turn on valve
            self.sm.send("M106 P3 S255")
            self.sm.send("G4 50")
            self.sm.send("M106 P3 S150")
 
            
