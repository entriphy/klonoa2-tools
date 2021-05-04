import filetype as ft

class KLFZ(ft.Type):
    MIME = ""
    EXTENSION = "klfz"
    MAGIC = bytearray([0x46, 0x5A])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC and buf[0x04] == 0x80 and buf[0x06] == 0x40