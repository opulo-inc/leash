import re
import time

import serial
import serial.tools.list_ports

from leash.utils import log


class SerialManager:
    """
    Manager for serial communications
    """

    def __init__(self):
        self._ser = serial.Serial()
        self._ser.baudrate = 119200
        self._ser.timeout = 1

    def close(self):
        self._ser.close()

    def is_open(self):
        return self._ser.is_open

    def read_all(self):
        return self._ser.read_all()

    def clear_queue(self, timeout=3):
        messages = ["M400", "M118 E1 done"]

        # send messages
        for i in messages:
            response = self.send(i)
            re_match = re.search("echo:done", response)
            if re_match is not None:
                return True

        # wait for done to arrive with timeout
        start = time.perf_counter()

        while True:
            response = self._ser.readline().decode("utf-8")
            re_match = re.search("echo:done", response)
            if re_match is not None:
                return True

            if time.perf_counter() - start > timeout:
                return False

    def scan_ports(self):
        comports = serial.tools.list_ports.comports()

        device_id = "0483:5740"

        for port, desc, hwid in sorted(comports):
            if device_id in hwid:
                try:
                    s = serial.Serial(port)
                    s.close()
                    log.info("Found motherboard at port: " + " with hwid: " + hwid)
                    self._ser.port = port
                    return True

                except (OSError, serial.SerialException):
                    pass

        log.error("Was unable to find a connected Lumen")
        return False

    def open(self):
        if self._ser.is_open:
            log.info("Serial port already open")
            return True

        if self._ser.port != "":
            self._ser.open()
            self._ser.timeout = 1
        else:
            log.error("No serial port selected")
            return False

        if self._ser.is_open:
            log.info("Connected to Lumen over serial port: " + self._ser.port)
            self._ser.read_all()
            return True
        else:
            log.error("Couldn't open serial port")
            return False

    def send(self, message: str):
        """
        Send can return two things; it can return False if port isn't open, or it can respond with marlin's response
        :param message:
        :return:
        """

        # Check to see if serial port is open
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode("utf-8")
            self._ser.write(encoded + b"\n")
            resp = self._ser.readline().decode("utf-8")
            return resp
        else:
            log.error("Serial port isn't open.")
            return False

    def send_blind(self, message):
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode("utf-8")
            self._ser.write(encoded + b"\n")
            return True
        else:
            log.error("Serial port isn't open.")
            return False

    def send_rtn_lines(self, message):
        """
        Send can return two things; it can return bool False if port isn't open, or it can respond with marlin's response
        :param message:
        :return:
        """

        # check to see if serial port is open
        if self._ser.is_open:
            self._ser.reset_input_buffer()
            encoded = message.encode("utf-8")
            self._ser.write(encoded + b"\n")
            resp = self._ser.readlines()
            decoded_resp = ""
            i = 0
            while i < len(resp):
                decoded_resp = decoded_resp + resp[i].decode("utf-8")
                i = i + 1
            return decoded_resp
        else:
            log.error("Serial port isn't open.")
            return False
