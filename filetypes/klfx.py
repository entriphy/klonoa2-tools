import filetype as ft
from ..struct.klfx_struct import Klfx

class KLFX(ft.Type):
    MIME = ""
    EXTENSION = "klfx"
    MAGIC = bytearray([0x46, 0x58])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC and buf[0x04] == 0x80 and buf[0x06] == 0x40

    def parse_klfx(buf, path=None) -> Klfx:
        if path != None: buf = open(path, "rb").read()
        return Klfx.from_bytes(buf)