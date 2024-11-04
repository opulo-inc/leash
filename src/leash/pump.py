import re
import time

from src.leash import log, SerialManager


class Pump:
    """
    Manager for controlling and reading pressure from pumps
    """

    def __init__(self, index, sm: SerialManager):
        self.index = index
        self.sm = sm

    def get_pressure(self):
        try:
            if self.index == "LEFT":
                # selects vac 1 through multiplexer
                self.sm.send("M260 A112 B1 S1")

            elif self.index == "RIGHT":
                # selects vac 2 through multiplexer
                self.sm.send("M260 A112 B2 S1")

            self.sm.send("M260 A109")
            self.sm.send("M260 B48")
            self.sm.send("M260 B27")
            self.sm.send("M260 S1")

            time.sleep(0.03)

            # read addresses 0x06 0x07 and 0x08 for pressure reading
            self.sm.send("M260 A109 B6 S1")
            msb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            self.sm.send("M260 A109 B7 S1")
            csb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            self.sm.send("M260 A109 B8 S1")
            lsb = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            val = msb.group(1) + csb.group(1) + lsb.group(1)

            result = int(val, 16)

            if result & (1 << 23):
                result = result - 2 ** 24

            return result
        except Exception as e:
            log.error(e)
            return False

    def get_temperature(self):
        try:
            if self.index == "LEFT":
                # selects vac 1 through multiplexer
                self.sm.send("M260 A112 B1 S1")
            elif self.index == "RIGHT":
                self.sm.send("M260 A112 B2 S1")

            # Assuming sensor is an object or interface to communicate with the sensor

            # Read REG0x09 and REG0x0A
            self.sm.send("M260 A109 B9 S1")
            reg0x09 = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            self.sm.send("M260 A109 B10 S1")
            reg0x0_a = re.search("data:(..)", self.sm.send("M261 A109 B1 S1"))

            # Calculate the temperature ADC value
            n = float(reg0x09.group() * 256 + reg0x0_a.group())

            # Determine if temperature is positive or negative
            if n < 2 ** 15:
                # Temperature is positive
                temperature = n / 256.0
            else:
                # Temperature is negative, apply the formula
                temperature = (n - 2 ** 16) / 256.0

            return temperature

        except Exception as e:
            log.error(e)
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
            # self.sm.send("G4 50")
            # self.sm.send("M106 P1 S150")

        elif self.index == "RIGHT":
            # turn on pump
            self.sm.send("M106 P2 S255")
            # turn on valve
            self.sm.send("M106 P3 S255")
            # self.sm.send("G4 50")
            # self.sm.send("M106 P3 S150")
