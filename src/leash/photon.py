"""Manager for communicating with a Photon Feeder Bus
"""

import enum
import re

from . import logger

class Commands(enum.IntEnum):
    GET_FEEDER_ID = 0x01
    INITIALIZE_FEEDER = 0x02 
    GET_VERSION = 0x03
    MOVE_FEED_FORWARD = 0x04
    MOVE_FEED_BACKWARD = 0x05
    MOVE_FEED_STATUS = 0x06
    VENDOR_OPTIONS = 0xbf
    GET_FEEDER_ADDRESS = 0xc0
    IDENTIFY_FEEDER = 0xc1
    PROGRAM_FEEDER_FLOOR = 0xc2
    UNINITIALIZED_FEEDERS_RESPOND = 0xc3

class Photon():

    def __init__(self, sm, log):

        self.sm = sm
        self.log = log
        
        self._packetID = 0x00

        self._outstandingPackets = []

        self.activeFeeders = []

        # PRIVATE

        ## Bus Utils

    def crc(self, data: bytes) -> int:
        crc: int = 0
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc ^= (0x1070 << 3)
                crc <<= 1
        
        return (crc >> 8) & 0xFF
    
    def byteArrayToString(self, byteArray):
        hexString = ""
        for i in byteArray:
            converted = hex(i)[2:]
            if len(converted) == 1:
                converted = "0" + converted
            hexString = hexString + converted

        return hexString

    def incrementPacketID(self):
        if self._packetID == 0xFF:
            self._packetID = 0x00
        else:
            self._packetID = self._packetID + 1

    def buildPacketFromBytes(self, packet):

        crc = self.crc(packet)

        packet.insert(4, crc)

        packetString = "M485 "

        # convert byte to string and append to packetString
        for i in packet:
            converted = hex(i)[2:]
            if len(converted) == 1:
                converted = "0" + converted
            packetString = packetString + converted

        return packetString

    def buildBytesFromPacket(self, responseString):
        byteArray = []

        for i in range(int(len(responseString)/2)):
            index = i*2
            sliced = responseString[index:index+2]
            hexed = int(sliced, 16)
            byteArray.append(hexed)

        return byteArray


    def sendPacket(self, address, command: Commands, payload = None):

        self.log.info("Sending packet payload: " + str(payload))
        # builds a packet without crc
        if payload is None:
            packet = [address, 0x00, self._packetID, 1, command]
        else:
            packet = [address, 0x00, self._packetID, len(payload) + 1, command] + payload

        sentPacketID = self._packetID

        gcode = self.buildPacketFromBytes(packet)

        self.log.info("Gcode to send: " + str(gcode))

        # open serial, send packet, close it
        self.sm._ser.read_all()
        response = self.sm.send(gcode).strip()

        self.incrementPacketID()

        reMatch = re.search("rs485-reply: (.*)", response).group(1)

        if reMatch == None or reMatch == "TIMEOUT":
            return -1
        else:
            byteArray = self.buildBytesFromPacket(reMatch)

            if byteArray[0] != 0x00:
                self.log.error("Received packet not addressed to host.")
                return False

            elif byteArray[1] != address and address != 0xFF:
                self.log.error("Received packet not from intended receipient.")
                return False

            elif byteArray[2] != sentPacketID:
                self.log.error("Received packet with wrong packet id.")
                return False

            elif byteArray[3] != len(byteArray) - 5:
                self.log.error("Received packet has wrong payload length.")
                return False

            else:
                sacrificialCRC = byteArray
                receivedCRC = sacrificialCRC[4]
                del sacrificialCRC[4]
                calcCRC = self.crc(sacrificialCRC)

                if receivedCRC != calcCRC:
                    self.log.error("Received packet with wrong crc.")
                    return False

                else:
                    respond = byteArray[4:]
                    return respond

    ## UNICAST

    def getFeederUUID(self, address):

        self.log.info("Requesting UUID from address: " + str(address))

        resp = self.sendPacket(address, Commands.GET_FEEDER_ID)

        if resp == -1:
            return -1
        elif resp == False:
            return False
        elif resp[0] != 0x00:
            return -2
        else:
            if len(resp[1:]) == 12:
                return resp[1:]
            else:
                return False

    def initializeFeeder(self, address, uuid):

        self.log.info("Requesting init at address: " + str(address))

        resp = self.sendPacket(address, Commands.INITIALIZE_FEEDER, payload = uuid)

        if resp != -1:
            if resp[0] == 0x00:
                return True
            else:
                return False

    # def getVersion(address):

    def moveFeedForward(self, address, tenths):

        self.log.info("Requesting " + str(tenths) + " feed from address: " + str(address))

        resp = self.sendPacket(address, Commands.MOVE_FEED_FORWARD, payload = tenths)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def moveFeedBackward(self, address, tenths):

        resp = self.sendPacket(address, Commands.MOVE_FEED_BACKWARD, payload = tenths)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def moveFeedStatus(self, address):

        resp = self.sendPacket(address, Commands.MOVE_FEED_STATUS)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def vendorOptions(self, address, payload):

        resp = self.sendPacket(address, Commands.MOVE_FEED_FORWARD, payload = payload)

        if resp[0] == 0x00:
            return True
        else:
            return False

    def scan(self, min = 1, max = 50):

        for i in range(min, max):

            #see if a feeder is there
            uuid = self.getFeederUUID(i)

            #if we got a response
            if uuid is not None and uuid != -1 and uuid != -2:

                #initialize
                if self.initializeFeeder(i, uuid):

                    self.log.info("Initialized feeder " + str(uuid) + " at address " + str(i))

                    # add to list of active feeders
                    self.activeFeeders.append(uuid)

                else:
                    self.log.error("Found feeder at " + str(i) + " but couldn't initialize")

    ## BROADCAST

    #def getFeederAddress(uuid):

    def identifyFeeder(self, uuid):

        self.log.info("Requesting identify from UUID: " + str(uuid))

        resp = self.sendPacket(0xFF, Commands.IDENTIFY_FEEDER, payload = uuid)

        if resp[0] == 0x00:
            return True
        else:
            return False

    #def programFeederFloor(uuid, addressToProgram):

    #def uninitilizedFeedersRespond():
