import filetype as ft

class HD(ft.Type):
    MIME = ""
    EXTENSION = "hd"
    MAGIC = bytearray([0x49, 0x45, 0x43, 0x53, 0x73, 0x72, 0x65, 0x56]) # IECSsreV

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC