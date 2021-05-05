import os
from lib import kldata_archive
from lib.structs.headpack_struct import Headpack
from lib.filetypes.ppt import PPT

# Config
headpack_bin_path: str = "game_files/HEADPACK.BIN"
kldata_bin_path: str = "game_files/KLDATA.BIN"
bgmpack_bin_path: str = "game_files/BGMPACK.BIN"
pptpack_bin_path: str = "game_files/PPTPACK.BIN"
limit: int = 0 # Limits how many archives are extracted from KLDATA (200 total). Set to 0 to remove this limit.
convert = True # Set this to true to automatically convert files when extracting KLDATA. (klfx -> obj, klfy -> png, gim -> png, etc)


# Main
if __name__ == "__main__":
    headpack_buf = bytearray(open(headpack_bin_path, "rb").read())
    headpack = Headpack.from_bytes(headpack_buf)

    # Extract KLDATA.BIN
    kldata_buf = bytearray(open(kldata_bin_path, "rb").read())
    kldata_dir = os.path.splitext(kldata_bin_path)[0]
    if not os.access(kldata_dir, os.R_OK):
        print("Creating %s directory..." % kldata_dir)
        os.mkdir(kldata_dir)
    for i, archive in enumerate(headpack.kldata.archives):
        print("Extracting archive %i..." % i)
        archive_bytes = kldata_buf[archive.offset:archive.offset + archive.size]
        archive_dir = "%s/%i_%s" % (kldata_dir, i, hex(archive.offset))
        if not os.access(archive_dir, os.R_OK): os.mkdir(archive_dir)
        kldata_archive.unpack(archive_bytes, archive_dir, archive.offset, convert)
        if i != 0 and i == limit: break
    
    # Extract PPTPACK.BIN
    # .vag files are playable in foobar2000/WinAmp using the vgmstream plugin
    # https://github.com/vgmstream/vgmstream
    pptpack_buf = bytearray(open(pptpack_bin_path, "rb").read())
    pptpack_dir = os.path.splitext(pptpack_bin_path)[0]
    if not os.access(pptpack_dir, os.R_OK):
        print("Creating %s directory..." % pptpack_dir)
        os.mkdir(pptpack_dir)
    for i, archive in enumerate(headpack.pptpack.archives):
        ppt_bytes = pptpack_buf[archive.offset:archive.offset + archive.size]
        filename = "%s/%s.vag" % (pptpack_dir, str(i))
        PPT.to_vag(ppt_bytes, filename)

    # TODO: Figure out how to extract BGMPACK
