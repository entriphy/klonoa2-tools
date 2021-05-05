import filetype as ft

class KLNull(ft.Type):
    MIME = ""
    EXTENSION = "klnull"
    MAGIC = bytearray([0x6E, 0x75, 0x6C, 0x6C])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return len(buf) == 0x10 and buf[:len(self.MAGIC)] == self.MAGIC