import struct

from google.protobuf.json_format import MessageToDict


def parseProtobufObj(obj):
    return MessageToDict(obj, False, False, False)


def readInt(byteArray, start):
    return struct.unpack("!L", byteArray[start:][0:4])[0]


def toBigInt(byteArray):
    array = byteArray[::-1]
    out = 0
    for key, value in enumerate(array):
        decoded = struct.unpack("B", bytes([value]))[0]
        out = out | decoded << key * 8
    return out
