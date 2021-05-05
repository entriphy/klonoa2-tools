import filetype as ft
import struct
from ..util import read_bytes

class PPT(ft.Type):
    MIME = ""
    EXTENSION = "ppt"

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return False
    
    def to_vag(ppt_bytes, path):
        ppt_bytes = ppt_bytes[0x10:]
        while read_bytes.u16le(ppt_bytes, 0) == 0x020C:
            ppt_bytes = ppt_bytes[0x10:]
        while read_bytes.u16le(ppt_bytes, len(ppt_bytes) - 0x10) == 0x0200:
            ppt_bytes = ppt_bytes[:len(ppt_bytes) - 0x10]
        
        vag_file = open(path, "wb")
        vag_file.write(bytearray([0x56, 0x41, 0x47, 0x70])) # Magic (VAGp)
        vag_file.write(bytearray([0x00, 0x00, 0x00, 0x20])) # Version
        vag_file.write(bytearray([0x00, 0x00, 0x00, 0x00])) # Reserved
        vag_file.write(struct.pack(">I", len(ppt_bytes))) # Waveform data size
        vag_file.write(bytearray([0x00, 0x00, 0x56, 0x22])) # Sample rate (22050 Hz)
        vag_file.write(bytearray([0x00 for _ in range(0x1C)])) # Zeros
        vag_file.write(ppt_bytes)
        vag_file.close()