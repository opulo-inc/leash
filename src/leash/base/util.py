
from datetime import datetime


def error(message):
    error_string = "ERROR - " + str(datetime.now()) + " - " + message
    print(error_string)
    # Append-adds at last

def info(message):
    info_string = "INFO - " + str(datetime.now()) + " - " + message
    print(info_string)

def crc(data: bytes) -> int:
    crc: int = 0
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc ^= (0x1070 << 3)
            crc <<= 1
    
    return (crc >> 8) & 0xFF

def byteArrayToString(byteArray):
    hexString = ""
    for i in byteArray:
        converted = hex(i)[2:]
        if len(converted) == 1:
            converted = "0" + converted
        hexString = hexString + converted

    return hexString