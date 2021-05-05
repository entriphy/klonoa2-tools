import struct

def u16le(buf, offset):
    return struct.unpack("h", buf[offset:offset+2])[0]

def u32le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]
