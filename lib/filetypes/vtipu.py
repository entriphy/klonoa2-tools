import filetype as ft

class vtIPU(ft.Type):
    MIME = ""
    EXTENSION = "vtipu" # Referred to as "vtIPU" in the debug log of the prototype build. Might be a similar format to ipu files?
    MAGIC = bytearray([0x76, 0x74, 0x69, 0x70])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC