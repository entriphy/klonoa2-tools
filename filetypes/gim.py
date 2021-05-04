import filetype as ft

class GIM(ft.Type):
    MIME = ""
    EXTENSION = "gim"
    MAGIC = bytearray([0x47, 0x49, 0x4D]) # GIM

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC