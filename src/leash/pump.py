"""Manager for controlling and reading pressure from pumps
"""

import re

class Pump():

    def __init__(self, index, sm, log):
        
        self.index = index
        self.sm = sm
        self.log = log

    def read(self):

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



    def toggle(self, command):
        if self.index == "LEFT":
            if command:
                # turn on pump
                self.sm.send("M106")
                # turn on valve
                self.sm.send("M106 P1 S255")
            else:
                self.sm.send("M107 P1")
                self.sm.send("M107")

        elif self.index == "RIGHT":
            if command:
                #turn on pump
                self.sm.send("M106 P2 S255")
                #turn on valve
                self.sm.send("M106 P3 S255")
            else:
                self.sm.send("M107 P2")
                self.sm.send("M107 P3")
            
