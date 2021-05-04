import filetype as ft

class KLName(ft.Type):
    MIME = ""
    EXTENSION = "klname"

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return len(buf) == 0x90 and buf[0x60:0x90] == bytearray([0x00 for _ in range(0x30)])