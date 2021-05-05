import filetype as ft

class KL0(ft.Type):
    MIME = ""
    EXTENSION = "kl0"
    MAGIC = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf == self.MAGIC