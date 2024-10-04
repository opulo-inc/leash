"""Manager for a Lumen ring light
"""

class Light():
    def __init__(self, index, sm, log):

        self.index = index
        self.sm = sm
        self.log = log

    def off(self):
        s = 0 if self.index == "BOT" else 1

        self.sm.send(f"M150 P0 R0 U0 B0 S{s}")

    def on(self, r=255, g=255, b=255, a=255):

        s = 0 if self.index == "BOT" else 1

        self.sm.send(f"M150 P{a} R{r} U{g} B{b} S{s}")
