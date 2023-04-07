import argparse
import os

from PIL import Image
from lib.structs.gms_struct import Gms
from lib.filetypes import klfy

def main():
    parser = argparse.ArgumentParser(
        prog="fx_to_obj",
        description="Converts a .fx file to a .obj file",
        epilog="meow :3"
    )
    parser.add_argument("gms", help="Path to .gms file")
    parser.add_argument("output", help="Name of output folder")
    args = parser.parse_args()

    gms_path = args.gms
    if not os.path.exists(gms_path):
        raise Exception("GMS file does not exist: " + gms_path)
    gms = Gms.from_file(gms_path)
    to_pngs(gms, args.output)
    
def to_pngs(gms: Gms, output_dir: str):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    texture_packet: Gms.Packet = None
    for packet in gms.packets:
        if packet.is_palette:
            palette_packet = packet
            width = texture_packet.data.trxreg.rrw
            height = texture_packet.data.trxreg.rrh
            start_x = texture_packet.data.trxpos.dsax
            start_y = texture_packet.data.trxpos.dsay
            tbp = texture_packet.data.bitbltbuf.dbp
            cbp = palette_packet.data.bitbltbuf.dbp
            filename = f"tbp{hex(tbp)}_cbp{hex(cbp)}_{width}x{height}_x{start_x}y{start_y}.png"

            img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            pixels = img.load()
            
            palette: list[Gms.Rgba32] = palette_packet.palette
            if len(palette) == 16: # 4-bit color
                for i, pixel in enumerate(texture_packet.texture):
                    x = i % width
                    y = i // width
                    color = palette[pixel]
                    try:
                        pixels[x, y] = (color.r, color.g, color.b, 0xFF if color.a == 0x80 else color.a * 2)
                    except Exception as e:
                        break # Happens when the texture data is not row-aligned, just skip the rest of the texture
            else: # 8-bit color
                for i, pixel in enumerate(texture_packet.texture):
                    x = i % width
                    y = i // width
                    mod = pixel % 0x20
                    if mod >= 0x08 and mod <= 0x0F:
                        pixel += 0x08
                    elif mod >= 0x10 and mod <= 0x17:
                        pixel -= 0x08
                    color = palette[pixel]
                    pixels[x, y] = (color.r, color.g, color.b, 0xFF if color.a == 0x80 else color.a * 2)
            
            img.save(os.path.join(output_dir, filename))
        else:
            texture_packet = packet

if __name__ == "__main__":
    main()
