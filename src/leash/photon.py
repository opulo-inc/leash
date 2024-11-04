import enum
import re

from src.leash import log, SerialManager


class Commands(enum.IntEnum):
    GET_FEEDER_ID = 0x01
    INITIALIZE_FEEDER = 0x02
    GET_VERSION = 0x03
    MOVE_FEED_FORWARD = 0x04
    MOVE_FEED_BACKWARD = 0x05
    MOVE_FEED_STATUS = 0x06
    VENDOR_OPTIONS = 0xBF
    GET_FEEDER_ADDRESS = 0xC0
    IDENTIFY_FEEDER = 0xC1
    PROGRAM_FEEDER_FLOOR = 0xC2
    UNINITIALIZED_FEEDERS_RESPOND = 0xC3


class Photon:
    """
    Manager for communicating with a Photon Feeder Bus
    """

    def __init__(self, sm: SerialManager):
        self.sm = sm

        self._packet_id = 0x00

        self._outstanding_packets = []

        self.active_feeders = []

    # region Bus utils

    def crc(self, data: bytes) -> int:
        crc: int = 0
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc ^= 0x1070 << 3
                crc <<= 1

        return (crc >> 8) & 0xFF

    def byte_array_to_string(self, byte_array):
        hex_string = ""
        for i in byte_array:
            converted = hex(i)[2:]
            if len(converted) == 1:
                converted = "0" + converted
            hex_string = hex_string + converted

        return hex_string

    def increment_packet_id(self):
        if self._packet_id == 0xFF:
            self._packet_id = 0x00
        else:
            self._packet_id = self._packet_id + 1

    def build_packet_from_bytes(self, packet):
        crc = self.crc(packet)

        packet.insert(4, crc)

        packet_string = "M485 "

        # Convert byte to string and append to packet_string
        for i in packet:
            converted = hex(i)[2:]
            if len(converted) == 1:
                converted = "0" + converted
            packet_string = packet_string + converted

        return packet_string

    def build_bytes_from_packet(self, response_string):
        byte_array = []

        for i in range(int(len(response_string) / 2)):
            index = i * 2
            sliced = response_string[index: index + 2]
            hexed = int(sliced, 16)
            byte_array.append(hexed)

        return byte_array

    def send_packet(self, address, command: Commands, payload=None):
        log.info("Sending packet payload: " + str(payload))
        # Builds a packet without crc
        if payload is None:
            packet = [address, 0x00, self._packet_id, 1, command]
        else:
            packet = [
                         address,
                         0x00,
                         self._packet_id,
                         len(payload) + 1,
                         command,
                     ] + payload

        sent_packet_id = self._packet_id

        gcode = self.build_packet_from_bytes(packet)

        log.info("Gcode to send: " + str(gcode))

        # Open serial, send packet, close it
        self.sm.read_all()
        response = self.sm.send(gcode).strip()

        self.increment_packet_id()

        re_match = re.search("rs485-reply: (.*)", response).group(1)

        if re_match is None or re_match == "TIMEOUT":
            return -1
        else:
            byte_array = self.build_bytes_from_packet(re_match)

            if byte_array[0] != 0x00:
                log.error("Received packet not addressed to host.")
                return False

            elif byte_array[1] != address and address != 0xFF:
                log.error("Received packet not from intended recipient.")
                return False

            elif byte_array[2] != sent_packet_id:
                log.error("Received packet with wrong packet id.")
                return False

            elif byte_array[3] != len(byte_array) - 5:
                log.error("Received packet has wrong payload length.")
                return False

            else:
                sacrificial_crc = byte_array
                received_crc = sacrificial_crc[4]
                del sacrificial_crc[4]
                calc_crc = self.crc(sacrificial_crc)

                if received_crc != calc_crc:
                    log.error("Received packet with wrong crc.")
                    return False

                else:
                    respond = byte_array[4:]
                    return respond

    # endregion
    # region UNICAST

    def get_feeder_uuid(self, address):
        log.info("Requesting UUID from address: " + str(address))

        resp = self.send_packet(address, Commands.GET_FEEDER_ID)

        if resp == -1:
            return -1
        elif resp is False:
            return False
        elif resp[0] != 0x00:
            return -2
        else:
            if len(resp[1:]) == 12:
                return resp[1:]
            else:
                return False

    def initialize_feeder(self, address, uuid):
        log.info("Requesting init at address: " + str(address))

        resp = self.send_packet(address, Commands.INITIALIZE_FEEDER, payload=uuid)

        if resp != -1:
            if resp[0] == 0x00:
                return True
            else:
                return False

    def get_version(self, address):
        raise NotImplementedError

    def move_feed_forward(self, address, tenths):
        log.info("Requesting " + str(tenths) + " feed from address: " + str(address))

        resp = self.send_packet(address, Commands.MOVE_FEED_FORWARD, payload=tenths)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def move_feed_backward(self, address, tenths):
        resp = self.send_packet(address, Commands.MOVE_FEED_BACKWARD, payload=tenths)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def move_feed_status(self, address):
        resp = self.send_packet(address, Commands.MOVE_FEED_STATUS)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def vendor_options(self, address, payload):
        resp = self.send_packet(address, Commands.MOVE_FEED_FORWARD, payload=payload)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def scan(self, min=1, max=50):
        for i in range(min, max):
            # see if a feeder is there
            uuid = self.get_feeder_uuid(i)

            # if we got a response
            if uuid is not None and uuid != -1 and uuid != -2:
                # initialize
                if self.initialize_feeder(i, uuid):
                    log.info(
                        "Initialized feeder " + str(uuid) + " at address " + str(i)
                    )

                    # add to list of active feeders
                    self.active_feeders.append(uuid)

                else:
                    log.error("Found feeder at " + str(i) + " but couldn't initialize")

    # endregion

    # region BROADCAST

    def get_feeder_address(self, uuid):
        raise NotImplementedError

    def identify_feeder(self, uuid):
        log.info("Requesting identify from UUID: " + str(uuid))

        resp = self.send_packet(0xFF, Commands.IDENTIFY_FEEDER, payload=uuid)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def program_feeder_floor(self, uuid, address_to_program):
        raise NotImplementedError

    def uninitialized_feeders_respond(self):
        raise NotImplementedError

    # endregion
