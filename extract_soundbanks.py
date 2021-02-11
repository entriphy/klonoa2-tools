import os, sys, struct

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

bin_path = input("Enter name of .BIN file (ex. KLDATA.BIN): ")
if not os.access(bin_path, os.R_OK):
    print("The file could not be found in the local directory.")
    sys.exit(1)

out_dir = input("Enter name of folder to extract to: ")
if not os.access(out_dir, os.R_OK):
    print("Creating directory...")
    os.mkdir(out_dir)

bin_filename = os.path.splitext(bin_path)[0]

with open(bin_path, "rb") as bin:
    buf = bytearray(bin.read())

idx = 0
hd_idx = buf.find(b"IECSsreV")
while hd_idx != -1:
    new_buf = buf[hd_idx:]
    hd_size = get_u32_le(new_buf, 0x1C)
    bd_size = get_u32_le(new_buf, 0x20)
    hd_buf = new_buf[:hd_size]
    bd_buf = new_buf[hd_size:hd_size + bd_size]

    # Write .hd file
    hd_filename = "%s/%s_%s.hd" % (out_dir, bin_filename, str(idx))
    print("Writing %s..." % hd_filename)
    hd_file = open(hd_filename, "wb")
    hd_file.write(hd_buf)
    hd_file.close()

    # Write .bd file
    bd_filename = "%s/%s_%s.bd" % (out_dir, bin_filename, str(idx))
    print("Writing %s..." % bd_filename)
    bd_file = open(bd_filename, "wb")
    bd_file.write(bd_buf)
    bd_file.close()

    # Find next soundbank
    idx += 1
    hd_idx = buf.find(b"IECSsreV", hd_idx + 1)

print("Done. Use this script to extract the soundbanks: https://github.com/Nisto/ps2-bankmod/blob/master/ps2-bankmod.py")