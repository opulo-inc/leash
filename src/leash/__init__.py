import time

from .camera import Camera
from .light import Light
from .photon import Photon
from .pump import Pump
from .serial import SerialManager
from .utils import log


class Lumen:
    """Lumen object, containing all other subsystems"""

    def __init__(self, top_cam=False, bot_cam=False):
        self.sm = SerialManager()
        self.photon = Photon(self.sm)

        self.left_pump = Pump("LEFT", self.sm)
        self.right_pump = Pump("RIGHT", self.sm)

        self.top_light = Light("TOP", self.sm)
        self.bot_light = Light("BOT", self.sm)

        self.position = {"x": 0, "y": 0, "z": 0, "a": 0, "b": 0}

        if top_cam:
            self.top_cam = Camera(0)

        if bot_cam:
            self.bot_cam = Camera(1)

        self._boot_cmds = [
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
            "M204 T4000",
            "G90",
        ]

        self._pre_home_cmds = ["M204 T2000"]

        self._post_home_cmds = ["M204 T4000"]

        self.park_x = 220
        self.park_y = 400
        self.park_z = 31.5

    # region SERIAL

    def connect(self):
        if self.sm.scan_ports():
            if self.sm.open():
                self.send_boot_commands()
                return True

        return False

    def disconnect(self):
        self.sm.close()
        if self.sm.is_open():
            return False
        else:
            return True

    def finish_moves(self):
        self.sm.clear_queue()

    def sleep(self, seconds: float):
        self.finish_moves()
        time.sleep(seconds)

    def get_hardware_id(self):
        """
        Probe for all hardware pull-up pins, plus chimera jumper.
        If any of these commands fail, it means is probably v3 or earlier.
        This also uses M115 to learn about the firmware
        :return:
        """
        raise NotImplementedError

    # endregion
    # region MOVEMENT

    def goto(self, x=None, y=None, z=None, a=None, b=None):
        cmd = "G0"
        vector = {"x": x, "y": y, "z": z, "a": a, "b": b}

        for name, value in vector.items():
            if value is not None:
                cmd += name.upper() + str(value)
                self.position[name] = value

        log.debug(cmd)
        self.sm.send(cmd)

    def set_speed(self, f=None):
        if f is not None:
            command = "G0 F" + str(f)
            self.sm.send(command)

    def send_boot_commands(self):
        for i in self._boot_cmds:
            if not self.sm.send(i):
                log.error("Halted sending boot commands because sending failed.")
                break

    def send_pre_homing_commands(self):
        for i in self._pre_home_cmds:
            if not self.sm.send(i):
                log.error("Halted sending pre homing commands because sending failed.")
                break

    def idle(self):
        self.left_pump.off()
        self.right_pump.off()

        self.top_light.off()
        self.bot_light.off()

        self.safe_z()

        self.goto(x=self.park_x, y=self.park_y)

    def home(self, x=True, y=True, z=True):
        log.info("Homing...")

        self.send_pre_homing_commands()

        cmd = "G28"
        for k, v in {"x": x, "y": y, "z": z}.items():
            if v:
                self.position[k] = 0
                cmd += " " + k

        self.sm.send(cmd)

        self.finish_moves()
        self.send_post_homing_commands()

    def send_post_homing_commands(self):
        for i in self._post_home_cmds:
            if not self.sm.send(i):
                log.error("Halted sending post homing commands because sending failed.")
                break

    def safe_z(self):
        self.goto(z=self.park_z)

    def probe(self, nozzle, start_z=None):
        """
        This function moves a given nozzle down until it detects a pressure change. it returns the XYZ position of the probed point
        :param nozzle:
        :param start_z:
        :return:
        """

        if nozzle == "LEFT":
            if start_z is not None:
                self.goto(z=start_z)
            else:
                self.safe_z()

            self.left_pump.on()
            self.sleep(0.5)

            base_vac = self.left_pump.get_pressure()

            log.info("Calibrated probe ambient is " + str(base_vac))

            while self.position["z"] >= 0.1:
                # left nozzle, z value goes down
                self.goto(z=self.position["z"] - 0.05)
                self.sleep(0.1)

                running_vac = self.left_pump.get_pressure()

                log.info("Probe vac value: " + str(running_vac))

                if (base_vac - running_vac > 35000) and (running_vac is not False):
                    log.info("Initial probe location")

                    self.left_pump.off()
                    pos = [
                        self.position["x"],
                        self.position["y"],
                        self.position["z"] * 1.5,
                    ]
                    log.info("Found probe at " + str(pos))
                    return pos

                rough_probe = self.position["z"]

                self.goto(z=rough_probe + 1)

                self.sleep(1)

                base_vac = self.left_pump.get_pressure()

                while self.position["z"] > rough_probe:
                    self.goto(z=self.position["z"] - 0.1)
                    self.sleep(0.1)
                    running_vac = self.left_pump.get_pressure()

                    log.info("Probe vac value: " + str(running_vac))

                    if (base_vac - running_vac > 20000) and (running_vac is not False):
                        self.left_pump.off()
                        pos = [
                            self.position["x"],
                            self.position["y"],
                            self.position["z"],
                        ]
                        log.info("Found probe at " + str(pos))
                        return pos

            log.info("Couldn't find probe point")
            self.left_pump.off()
            return False

        elif nozzle == "RIGHT":
            self.right_pump.on()

            # ToDo: Implement the rest of the function

        else:
            log.error("probe() requires a nozzle of option either LEFT or RIGHT")

    # endregion
