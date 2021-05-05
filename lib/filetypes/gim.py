import filetype as ft
from ..util import read_bytes
from PIL import Image

class GIM(ft.Type):
    MIME = ""
    EXTENSION = "gim"
    MAGIC = bytearray([0x47, 0x49, 0x4D]) # GIM

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC
    
    def to_png(buf, path):
        width = read_bytes.u16le(buf, 0x1C)
        height = read_bytes.u16le(buf, 0x1E)
        eight_bit_color = read_bytes.u32le(buf, 0x14) == 0x02 # TODO: This is not actually what makes it 8-bit. Fix it.
        
        palette_offset = 0x30 + (width * height) // (2 if not eight_bit_color else 1)
        palette = []
        for i in range(16 if not eight_bit_color else 256):
            color_offset = palette_offset + (i * 4)
            r = buf[color_offset]
            g = buf[color_offset + 1]
            b = buf[color_offset + 2]
            a = buf[color_offset + 3]
            palette.append((r, g, b, a))

        img = Image.new("RGBA", (width, height))
        pixels = img.load()
        if not eight_bit_color:
            for i in range((width * height) // 2):
                x = (i * 2) % width
                y = (i * 2) // width
                pixel = buf[0x20 + i]
                color_1 = palette[pixel % 16]
                color_2 = palette[pixel // 16]
                pixels[x, y] = color_1
                pixels[x + 1, y] = color_2
        else:
            for i in range(width * height):
                x = i % width
                y = i // width
                pixel = buf[0x20 + i]
                pixels[x, y] = palette[pixel]
        
        img.save(path.replace(".gim", ".png"))