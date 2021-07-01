from kaitaistruct import KaitaiStream
from lib.structs.klfx_struct import Klfx
from lib.structs.klfz_struct import Klfz
import os, glob, shutil
from .util.read_bytes import u32le
from . import filetypes

def __is_archive(archive_bytes):
    if len(archive_bytes) == 0: return False
    # Check that the integer at the beginning seems "reasonable" for an archive
    archive_check = u32le(archive_bytes, 0)
    if archive_check == 1 \
        and (u32le(archive_bytes, 0x08) == len(archive_bytes) \
        or (u32le(archive_bytes, 0x04) == 0x10 \
        and u32le(archive_bytes, 0x08) == 0x10)):
            return True
    elif archive_check < 2 or archive_check > 1000: return False
    # Check that file offsets are valid
    file_offsets = [0]
    for i in range(archive_check):
        file_offset = u32le(archive_bytes, 0x04 + (i * 0x04))
        if file_offset >= 16 and file_offset % 16 == 0 and file_offset >= file_offsets[-1] and file_offset <= len(archive_bytes):
            file_offsets.append(file_offset)
        else:
            return False
    return True

def unpack(buf, dir, offset, convert=True):
    is_model = False
    file_offsets = []
    file_count = u32le(buf, 0x00)
    for i in range(file_count):
        file_offset = u32le(buf, 0x04 + (i * 0x04))
        if file_offset not in file_offsets: file_offsets.append(file_offset) # Models and some other archives have duplicate offsets
    for i, file_offset in enumerate(file_offsets):
        file_start_offset = file_offset
        file_end_offset = file_offsets[i + 1] if i != len(file_offsets) - 1 else len(buf)
        file_kldata_offset = offset + file_start_offset # Get offset for file in KLDATA.BIN. Only used for naming the extracted file/archive.
        file_bytes = buf[file_start_offset:file_end_offset]
        is_archive = __is_archive(file_bytes)
        if is_archive:
            archive_dir = "%s/%i_%s" % (dir, i, hex(file_kldata_offset))
            if not os.access(archive_dir, os.R_OK): os.mkdir(archive_dir)
            unpack(file_bytes, archive_dir, file_kldata_offset, convert)
        else:
            extension = filetypes.ft.guess_extension(file_bytes)
            if extension not in filetypes.kl2_filetypes: extension = "kldata"
            filename = "%s/%i_%s.%s" % (dir, i, hex(file_kldata_offset), extension)
            f = open(filename, "wb")
            f.write(file_bytes)
            f.close()
            if convert:
                try:
                    if extension == "gim": filetypes.gim.GIM.to_png(file_bytes, filename)
                    elif extension == "klfx": 
                        filetypes.klfx.KLFX.to_obj(filename)
                        is_model = True
                    elif extension == "klfy": filetypes.klfy.KLFY.to_png(filename)
                except Exception as e:
                    print("Error %s:" % filename, e)
    
    # Copy texture to .obj directory
    if is_model and convert:
        files = glob.glob(dir + "/**/*.png", recursive=True)
        if len(files) > 0:
            png_path = files[0]
            try: shutil.copyfile(png_path, dir + "/model.png")
            except shutil.SameFileError: pass
        else:
            files = glob.glob(dir + "/../**/*.png", recursive=True)
            if len(files) > 0:
                png_path = files[0]
                shutil.copyfile(png_path, dir + "/model.png")
    # if is_model and convert:
    #     try:
    #         png_files = list(filter(lambda x: not x.endswith("model.png"), glob.glob(dir + "/../**/*.png", recursive=True)))
    #         klfx_files = glob.glob(dir + "/*.klfx", recursive=True)
    #         klfz_files = glob.glob(dir + "/**/*.klfz", recursive=True)
    #         klfb_files = glob.glob(dir + "/**/*.kldata", recursive=True)
    #         klfzs = []
    #         if len(png_files) == 0: return
    #         if len(klfx_files) == 0: return
    #         if len(klfb_files) == 0: return
    #         if len(klfz_files) > 0:
    #             for klfz in klfz_files: klfzs.append(klfz)
    #         filetypes.klfx.KLFX.to_gltf(klfx_files[0], png_files, joints_path=klfb_files[0], morphs=klfzs, animations=klfb_files[1:])
    #     except: pass
