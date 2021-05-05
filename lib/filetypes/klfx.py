import filetype as ft
from ..structs.klfx_struct import Klfx
from ..util.read_bytes import u16le
from ..util.klfx_indices import parse_faces
import os

class KLFX(ft.Type):
    MIME = ""
    EXTENSION = "klfx"
    MAGIC = bytearray([0x46, 0x58])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC and buf[0x04] == 0x80 and buf[0x06] == 0x40

    def to_obj(buf, path, mtl=True):
        klfx = Klfx.from_bytes(buf)
        obj_filename = path.replace(".klfx", ".obj")
        obj = open(obj_filename, "w")
        if mtl:
            mtl_filename = path.replace(".klfx", ".mtl")
            obj.write("mtllib %s\n" % os.path.basename(mtl_filename))
            obj.write("usemtl mtl0\n\n")
        vertex_acc, normal_acc, uv_acc = 1, 1, 1
        for i, part in enumerate(klfx.parts):
            if part.subpart_count == 0: continue # TODO: Find out what it means when this equals zero instead of skipping it
            vertices, normals = [], []
            for subpart in part.subparts:
                vertices += subpart.vertices
                normals += subpart.normals
            uvs = part.uvs
            faces = parse_faces(buf, part)

            obj.write("# -- Part %i ---\ng part%i\n\n" % (i, i))
            obj.write("# Vertex count: %i\n" % part.vertex_count)
            # It takes ten times longer if everything is divided in the Kaitai struct.
            # lol...?
            for vertex in vertices: obj.write("v  %.7f %.7f %.7f\n" % (vertex.x / 2048, -vertex.y / 2048, -vertex.z / 2048))
            obj.write("\n# Normal count: %i\n" % part.normal_count)
            for normal in normals: obj.write("vn %.7f %.7f %.7f\n" % (normal.x / 2048, -normal.y / 2048, -normal.z / 2048))
            obj.write("\n# UV count: %i\n" % part.uv_count)
            for uv in uvs: obj.write("vt %.15f %.15f\n" % (uv.u / 16384, 1.0 - uv.v / 16384))
            obj.write("\n# Face count: %i\n" % len(faces))
            for face in faces: obj.write("f %i/%i/%i %i/%i/%i %i/%i/%i\n" % (
                vertex_acc + face[0][0], uv_acc + face[0][1], normal_acc + face[0][2],
                vertex_acc + face[1][0], uv_acc + face[1][1], normal_acc + face[1][2],
                vertex_acc + face[2][0], uv_acc + face[2][1], normal_acc + face[2][2]
            ))
            obj.write("\n")

            vertex_acc += part.vertex_count
            normal_acc += part.normal_count
            uv_acc     += part.uv_count
    
        obj.close()

        if mtl:
            mtl = open(mtl_filename, "w")
            mtl.write("newmtl mtl0\nKa 0.2 0.2 0.2\nKd 0.50000 0.50000 0.50000\nKs 0.00000 0.00000 0.00000\nd 1.00000\nillum 1\nmap_Kd model.png")
            mtl.close()
