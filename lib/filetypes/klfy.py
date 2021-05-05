import filetype as ft
from PIL import Image
from ..util.read_bytes import u16le

# TODO: Create Kaitai Struct for this
class KLFY(ft.Type):
    MIME = ""
    EXTENSION = "klfy" # FX and FZ are used as magic headers, so why not FY? :P

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return len(buf) > 0x60 and buf[0x28] == 0x50 and buf[0x38] == 0x51 and buf[0x48] == 0x52 and buf[0x58] == 0x53

    def to_png(buf, path):
        buf = buf[0x10:]
        img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        pixels = img.load()
        while buf[0x08:0x0A] == bytearray([0xEE, 0xEE]):
            width = u16le(buf, 0x30)
            height = u16le(buf, 0x34)
            start_x = u16le(buf, 0x24)
            start_y = u16le(buf, 0x26)
            eight_bit_color = False

            palette_offset = 0x60 + (width * height) // 2 + 0x60
            palette = []
            for i in range(16 if not eight_bit_color else 256):
                color_offset = palette_offset + (i * 4)
                r = buf[color_offset]
                g = buf[color_offset + 1]
                b = buf[color_offset + 2]
                a = buf[color_offset + 3]
                palette.append((r, g, b, 255))

            if not eight_bit_color:
                for i in range((width * height) // 2):
                    x = start_x + (i * 2) % width
                    y = start_y + (i * 2) // width
                    pixel = buf[0x60 + i]
                    color_1 = palette[pixel % 16]
                    color_2 = palette[pixel // 16]
                    pixels[x, y] = color_1
                    pixels[x + 1, y] = color_2
            else:
                for i in range(width * height):
                    x = start_x + i % width
                    y = start_y + i // width
                    pixel = buf[0x60 + i]
                    pixels[x, y] = palette[pixel]
            buf = buf[palette_offset + 0x40:]

        img.save(path.replace(".klfy", ".png"))