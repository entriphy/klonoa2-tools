import os, sys, struct, hashlib

def get_u32_le(buf, offset):
    return struct.unpack("<I", buf[offset:offset+4])[0]

def get_u16_le(buf, offset):
    return struct.unpack("h", buf[offset:offset+2])[0]

def parse_part_descriptor(model_offset, offset):
    return {
        "vertex_count": get_u16_le(buf, offset + 0x0C),
        "normal_count": get_u16_le(buf, offset + 0x0E),
        "uv_count": get_u16_le(buf, offset + 0x08),
        "subpart_count": get_u16_le(buf, offset + 0x0A),
        "indices_part_count": get_u16_le(buf, offset + 0x06),

        "vertices_offset":  model_offset + get_u32_le(buf, offset + 0x18),
        "normals_offset": model_offset + get_u32_le(buf, offset + 0x1C),
        "uvs_offset": model_offset + get_u32_le(buf, offset + 0x14),
        "indices_offset": model_offset + get_u32_le(buf, offset + 0x10),
        "descriptor_offset": offset,
        "subpart_descriptor_offset": model_offset + get_u32_le(buf, offset + 0x20)
    }

def parse_subpart_descriptor(offset):
    return (
        get_u16_le(buf, offset + 0x0A), # Vertex count
        get_u16_le(buf, offset + 0x0A) # Normal count
    )

bin_path = input("Enter name of .bin file (ex. KLDATA.BIN): ")
if not os.access(bin_path, os.R_OK):
    print("%s could not be found in the local directory." % bin_path)
    sys.exit(1)

out_dir = input("Enter name of folder to extract to: ")
if not os.access(out_dir, os.R_OK):
    print("Creating directory...")
    os.mkdir(out_dir)

with open(bin_path, "rb") as bin:
    bin_bytes = bin.read()
    bin_md5 = hashlib.md5(bin_bytes).hexdigest()
    buf = bytearray(bin_bytes)

model_header = bytes([0x46, 0x58]) # FX
model_idx = 0
model_offset = buf.find(model_header)
while model_offset != -1:
    if buf[model_offset + 0x04] != 0x80 or buf[model_offset + 0x06] != 0x40: # Verify header (FX..€.@)
        model_offset = buf.find(model_header, model_offset + 1)
        continue

    parts = []
    part_count = get_u16_le(buf, model_offset + 0x02)
    for i in range(part_count):
        part_descriptor_offset = model_offset + 0x10 + (i * 0x30)
        part_descriptor = parse_part_descriptor(model_offset, part_descriptor_offset)
        if part_descriptor["subpart_count"] == 0: # TODO: Find out what it means when this equals zero instead of skipping it
            continue
        parts.append(part_descriptor)

    for part in parts:
        # Vertices
        vertices = []
        current_offset = part["vertices_offset"]
        for i in range(part["subpart_count"]):
            subpart_vertex_count = parse_subpart_descriptor(part["subpart_descriptor_offset"] + (i * 0x20))[0]
            for i in range(subpart_vertex_count):
                vertex_x = get_u16_le(buf, current_offset)
                vertex_y = -get_u16_le(buf, current_offset + 2)
                vertex_z = -get_u16_le(buf, current_offset + 4)
                vertices.append((vertex_x, vertex_y, vertex_z))
                current_offset += 6
            if current_offset % 16 != 0:
                current_offset += 16 - (current_offset % 16)
        part["vertices"] = vertices

        # Normals
        normals = []
        current_offset = part["normals_offset"]
        for i in range(part["subpart_count"]):
            subpart_normal_count = parse_subpart_descriptor(part["subpart_descriptor_offset"] + (i * 0x20))[1]
            for i in range(subpart_normal_count):
                normal_x = get_u16_le(buf, current_offset)
                normal_y = -get_u16_le(buf, current_offset + 2)
                normal_z = -get_u16_le(buf, current_offset + 4)
                normals.append((normal_x, normal_y, normal_z))
                current_offset += 6
            if current_offset % 16 != 0:
                current_offset += 16 - (current_offset % 16)
        part["normals"] = normals

        # UVs
        uvs = []
        current_offset = part["uvs_offset"]
        for i in range(part["uv_count"]):
            u = get_u16_le(buf, part["uvs_offset"] + (i * 0x08)) / 8192 # TODO: Find correct number to divide UV values by
            v = 1.0 - get_u16_le(buf, part["uvs_offset"] + (i * 0x08) + 4) / 8192
            uvs.append((u, v))
        part["uvs"] = uvs

        # Indices + Faces
        indices, tstrips = [], []
        current_offset = part["indices_offset"]
        current_part = 0
        while current_part < part["indices_part_count"]:
            normal_index = get_u16_le(buf, current_offset) + 1
            uv_index = get_u16_le(buf, current_offset + 0x02) + 1
            face_index = get_u16_le(buf, current_offset + 0x04) + 1
            indices.append((normal_index, uv_index, face_index))

            if get_u16_le(buf, current_offset + 0x06) != 0:
                if get_u16_le(buf, current_offset + 0x06) == -1:
                    current_part += 1
                else:
                    tstrips.append(get_u16_le(buf, current_offset + 0x06))
            
            current_offset += 0x08
        part["indices"] = indices
        part["tstrips"] = tstrips

    # Write model to .obj file
    model_directory = "%s/%s_%s" % (out_dir, str(model_idx), hex(model_offset))
    if not os.access(model_directory, os.R_OK):
        os.mkdir(model_directory)
    obj_filename = "%s/model.obj" % (model_directory)
    obj = open(obj_filename, "w")
    obj.write("# File: %s (MD5 %s)\n\n" % (bin_path, bin_md5))
    vertex_accumulator, normal_accumulator, uv_accumulator = 0, 0, 0
    part_idx = 0
    for part in parts:
        obj.write("# -- Part %s --\n" % str(part_idx))
        obj.write("g part%s\n" % str(part_idx))

        filename = "%s/%s.obj" % (model_directory, str(part_idx))
        f = open(filename, "w")
        f.write("# File: %s (MD5 %s)\n" % (bin_path, bin_md5))
        f.write("# Part header: %s\n\n" % (hex(part["descriptor_offset"])))

        vertices = part["vertices"]
        f.write("# Vertex count: %s, offset: %s\n" % (str(part["vertex_count"]), hex(part["vertices_offset"])))
        obj.write("# Vertex count: %s, offset: %s\n" % (str(part["vertex_count"]), hex(part["vertices_offset"])))
        for vertex in vertices:
            f.write("v %s %s %s\n" % (str(vertex[0]), str(vertex[1]), str(vertex[2])))
            obj.write("v %s %s %s\n" % (str(vertex[0]), str(vertex[1]), str(vertex[2])))
        
        f.write("\n")
        obj.write("\n")

        normals = part["normals"]
        f.write("# Normal count: %s, offset: %s\n" % (str(part["normal_count"]), hex(part["normals_offset"])))
        obj.write("# Normal count: %s, offset: %s\n" % (str(part["normal_count"]), hex(part["normals_offset"])))
        for normal in normals:
            f.write("vn %s %s %s\n" % (str(normal[0]), str(normal[1]), str(normal[2])))
            obj.write("vn %s %s %s\n" % (str(normal[0]), str(normal[1]), str(normal[2])))

        f.write("\n")
        obj.write("\n")

        uvs = part["uvs"]
        f.write("# UV count: %s, offset: %s\n" % (str(part["uv_count"]), hex(part["uvs_offset"])))
        obj.write("# UV count: %s, offset: %s\n" % (str(part["uv_count"]), hex(part["uvs_offset"])))
        for uv in uvs:
            f.write("vt %s %s\n" % (str(uv[0]), str(uv[1])))
            obj.write("vt %s %s\n" % (str(uv[0]), str(uv[1])))

        f.write("\n")
        obj.write("\n")

        f.write("# TStrip count: %s, offset: %s\n" % (str(len(part["tstrips"])), hex(part["indices_offset"])))
        obj.write("# TStrip count: %s, offset: %s\n" % (str(len(part["tstrips"])), hex(part["indices_offset"])))
        for i, tstrip in enumerate(part["tstrips"]):
            tstrips = part["tstrips"][0:i + 1]
            start_idx = sum(tstrips) + 1 - tstrip
            indices = part["indices"][start_idx - 1:start_idx - 1 + tstrip]
            f.write("# - TStrip %s, %s vertices\n" % (str(i), str(tstrip)))
            obj.write("# - TStrip %s, %s vertices\n" % (str(i), str(tstrip)))
            for x in range(len(indices) - 2):
                f.write("f %s/%s/%s %s/%s/%s %s/%s/%s\n" % (
                    str(indices[x][2]), str(indices[x][1]), str(indices[x][0]),
                    str(indices[x + 1][2]), str(indices[x + 1][1]), str(indices[x + 1][0]),
                    str(indices[x + 2][2]), str(indices[x + 2][1]), str(indices[x + 2][0])
                ))
                obj.write("f %s/%s/%s %s/%s/%s %s/%s/%s\n" % (
                    str(vertex_accumulator + indices[x][2]), str(uv_accumulator + indices[x][1]), str(normal_accumulator + indices[x][0]),
                    str(vertex_accumulator + indices[x + 1][2]), str(uv_accumulator + indices[x + 1][1]), str(normal_accumulator + indices[x + 1][0]),
                    str(vertex_accumulator + indices[x + 2][2]), str(uv_accumulator + indices[x + 2][1]), str(normal_accumulator + indices[x + 2][0])
                ))
        
        f.close()
        vertex_accumulator += part["vertex_count"]
        normal_accumulator += part["normal_count"]
        uv_accumulator += part["uv_count"]
        obj.write("\n")
        part_idx += 1

    obj.close()

    model_offset = buf.find(model_header, model_offset + 1)
    model_idx += 1