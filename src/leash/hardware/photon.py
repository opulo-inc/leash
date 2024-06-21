"""Manager for communicating with a Photon Feeder Bus
"""

import enum
import re

from ..base import util

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

    def __init__(self, mobo):

        self._mobo = mobo
        self._packetID = 0x00

        self._outstandingPackets = []

        self._activeFeeders = []

        # PRIVATE

        ## Bus Utils

    def incrementPacketID(self):
        if self._packetID == 0xFF:
            self._packetID = 0x00
        else:
            self._packetID = self._packetID + 1

    def buildPacketFromBytes(self, packet):

        crc = util.crc(packet)

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

        util.info("Sending packet payload: " + str(payload))
        # builds a packet without crc
        if payload is None:
            packet = [address, 0x00, self._packetID, 1, command]
        else:
            packet = [address, 0x00, self._packetID, len(payload) + 1, command] + payload

        sentPacketID = self._packetID

        print(packet)

        gcode = self.buildPacketFromBytes(packet)

        print(gcode)

        # open serial, send packet, close it
        self._mobo.openSerial()
        self._mobo._ser.read_all()
        response = self._mobo.send(gcode).strip()
        self._mobo.closeSerial()

        self.incrementPacketID()

        reMatch = re.search("rs485-reply: (.*)", response).group(1)

        if reMatch == None or reMatch == "TIMEOUT":
            return -1
        else:
            byteArray = self.buildBytesFromPacket(reMatch)

            print(byteArray)

            if byteArray[0] != 0x00:
                util.error("Received packet not addressed to host.")
                return False

            elif byteArray[1] != address and address != 0xFF:
                util.error("Received packet not from intended receipient.")
                return False

            elif byteArray[2] != sentPacketID:
                util.error("Received packet with wrong packet id.")
                return False

            elif byteArray[3] != len(byteArray) - 5:
                util.error("Received packet has wrong payload length.")
                return False

            else:
                sacrificialCRC = byteArray
                receivedCRC = sacrificialCRC[4]
                del sacrificialCRC[4]
                calcCRC = util.crc(sacrificialCRC)

                if receivedCRC != calcCRC:
                    util.error("Received packet with wrong crc.")
                    return False

                else:
                    respond = byteArray[4:]
                    return respond

    ## UNICAST

    def getFeederUUID(self, address):

        util.info("Requesting UUID from address: " + str(address))

        resp = self.sendPacket(address, Commands.GET_FEEDER_ID)

        if resp == -1:
            return -1
        elif resp == False:
            return False
        elif resp[0] != 0x00:
            return -2
        else:
            return resp[1:]

    def initializeFeeder(self, address, uuid):

        util.info("Requesting init at address: " + str(address))

        resp = self.sendPacket(address, Commands.INITIALIZE_FEEDER, payload = uuid)

        if resp[0] == 0x00:
            return True
        else:
            return False

    # def getVersion(address):

    def moveFeedForward(self, address, tenths):

        util.info("Requesting " + str(tenths) + " feed from address: " + str(address))

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
            resp = self.getFeederUUID(i)

            #if we got a response
            if resp is not None:

                uuid = resp[1:]

                #initialize
                if self.initializeFeeder(i, uuid):

                    # add to list of active feeders
                    self._activeFeeders[i] = resp[1:]

                else:
                    util.error("Found feeder at " + i + " but couldn't initialize")

    ## BROADCAST

    #def getFeederAddress(uuid):

    def identifyFeeder(self, uuid):

        util.info("Requesting identify from UUID: " + str(uuid))

        resp = self.sendPacket(0xFF, Commands.IDENTIFY_FEEDER, payload = uuid)

        print(resp)

        if resp[0] == 0x00:
            return True
        else:
            return False

    #def programFeederFloor(uuid, addressToProgram):

    #def uninitilizedFeedersRespond():
