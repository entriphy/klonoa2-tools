import struct

def u16le(buf: bytes, offset: int) -> int:
    return struct.unpack("h", buf[offset:offset+2])[0]

def u32le(buf: bytes, offset: int) -> int:
    return struct.unpack("<I", buf[offset:offset+4])[0]

def s32le(buf: bytes, offset: int) -> int:
    return struct.unpack("<i", buf[offset:offset+4])[0]
