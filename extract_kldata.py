import os, sys, struct

pack_header = bytes([0x08, 0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00])

def get_u32_le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]

def get_file_arg(message):
    x = ''
    while not os.path.isfile(x):
        x = input(message).strip('"')
    return os.path.realpath(x)

def get_dir_arg(message):
    x = ''
    while not os.path.isdir(x):
        x = input(message).strip('"')
    return os.path.realpath(x)

bin_path = "KLDATA.BIN"
if not os.access(bin_path, os.R_OK):
    print("KLDATA.BIN could not be found in the local directory.")
    sys.exit(1)

out_dir = input("Enter name of folder to extract to: ")
if not os.access(out_dir, os.R_OK):
    print("Creating directory...")
    os.mkdir(out_dir)

with open(bin_path, "rb") as bin:
    buf = bytearray(bin.read())

idx = 0 # Used for naming folders (KLDATA_%d)
pack_offset = buf.find(pack_header)
while pack_offset != -1:
    if pack_offset % 2048 != 0: # Invalid pack header, skip
        pack_offset = buf.find(pack_header, pack_offset + 1)
        continue
    
    pack_size = get_u32_le(buf, pack_offset + 0x20) - 0x20
    if pack_size == 0x80: # Empty pack
        idx += 1
        pack_offset = buf.find(pack_header, pack_offset + 1)
        continue

    dir_name = "%s/KLDATA_%s" % (out_dir, str(idx))
    if not os.access(dir_name, os.R_OK):
        os.mkdir(dir_name)
    pack_buf = buf[pack_offset:pack_offset + pack_size]
    pack_files_offset = 0x30
    while get_u32_le(pack_buf, pack_files_offset) == 0xFFFFFFFF: # Often times, the number at 0x30 is 0xFFFFFFFF. This might be indicating something, but let's just ignore it for now.
        pack_files_offset += 0x10
    pack_file_count = get_u32_le(pack_buf, pack_files_offset)
    for file_idx in range(1, pack_file_count + 1):
        file_start_offset = pack_files_offset + get_u32_le(pack_buf, pack_files_offset + 0x04 * file_idx)
        if file_idx == pack_file_count:
            file_end_offset = pack_size
        else:
            file_end_offset = pack_files_offset + get_u32_le(pack_buf, pack_files_offset + 0x04 * (file_idx + 1))
        file_buf = pack_buf[file_start_offset:file_end_offset]

        filename = "%s/%s.kldata" % (dir_name, str(file_idx))
        f = open(filename, "wb")
        f.write(file_buf)
        f.close()

    idx += 1
    pack_offset = buf.find(pack_header, pack_offset + 1)