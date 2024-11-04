from src.leash import SerialManager


class Light:
    """
    Manager for a Lumen ring light
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, index, sm: SerialManager):
        self.index = index
        self.sm = sm

    def off(self):
        s = 0 if self.index == "BOT" else 1

        self.sm.send(f"M150 P0 R0 U0 B0 S{s}")

    def on(self, r=255, g=255, b=255, a=255):
        s = 0 if self.index == "BOT" else 1

        self.sm.send(f"M150 P{a} R{r} U{g} B{b} S{s}")
