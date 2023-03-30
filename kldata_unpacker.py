from lib.structs.headpack_struct import Headpack
from lib.kldata_archives import *
import os

if __name__ == "__main__":
    with open("game_files/HEADPACK.BIN", "rb") as bin:
        headpack = Headpack.from_bytes(bin.read())
    with open("game_files/KLDATA.BIN", "rb") as bin:
        kldata_bytes = bin.read()
    
    output_dir = "game_files/KLDATA"
    if not os.access(output_dir, os.R_OK):
        os.mkdir(output_dir)
    for i, archive in enumerate(headpack.kldata.archives):
        archive_offset = archive.offset
        if i == 199:
            arc = SpritesArchive(kldata_bytes, archive_offset, name="sprites", index=i)
        else:
            arc = PreloadArchive(kldata_bytes, archive_offset, name="preload", index=i) if i % 2 == 0 else RootArchive(kldata_bytes, archive_offset, name="root", index=i)
        arc_dir = f"{output_dir}/{i}_{arc.name}"
        arc.write_files(arc_dir)
