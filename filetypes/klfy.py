import filetype as ft

# TODO: Create Kaitai Struct for this
class KLFY(ft.Type):
    MIME = ""
    EXTENSION = "klfy" # FX and FZ are used as magic headers, so why not FY? :P

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return len(buf) > 0x60 and buf[0x28] == 0x50 and buf[0x38] == 0x51 and buf[0x48] == 0x52 and buf[0x58] == 0x53