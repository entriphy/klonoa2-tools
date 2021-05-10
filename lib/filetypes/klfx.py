import os, math, base64
import filetype as ft
import numpy as np
import pygltflib
from ..structs.klfx_struct import Klfx
from ..util.read_bytes import u16le
from ..util.klfx_indices import parse_faces


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

    def __normalize(arr): # Unused
        normalized = []
        for a in arr:
            magnitudeSquared = a[0] ** 2 + a[1] ** 2 + a[2] ** 2
            magnitude = math.sqrt(magnitudeSquared)
            x = a[0] / magnitude
            y = a[1] / magnitude
            z = a[1] / magnitude
            normalized.append([x, y, z])
        return np.array(normalized, dtype=np.float32)
    
    def to_gltf(buf, path, texture_path):
        klfx = Klfx.from_bytes(buf)
        gltf_filename = path.replace(".klfx", ".gltf")
        vertices_bytes = bytes()
        normals_bytes = bytes()
        uvs_bytes = bytes()
        triangles_bytes = bytes()
        texture_bytes = open(texture_path, "rb").read()

        meshes = []
        accessors = []

        for i, part in enumerate(klfx.parts):
            if part.subpart_count == 0: continue # TODO: Find out what it means when this equals zero instead of skipping it
            vertices, normals = [], []
            for subpart in part.subparts:
                vertices += [[vertex.x / 2048, vertex.y / -2048, vertex.z / -2048] for vertex in subpart.vertices]
                normals += [[normal.x / 2048, normal.y / -2048, normal.z / -2048] for normal in subpart.normals]
            uvs = [[uv.u / 16384, uv.v / 16384] for uv in part.uvs]
            indices = parse_faces(buf, part)
            faces = [[face[0][0], face[1][0], face[2][0]] for face in indices]

            # glTF does not support multiple normals/UVs on one vertex
            # So we have to do this...
            indices_list = []
            vertices_fixed = []
            normals_fixed = []
            uvs_fixed = []
            indices_fixed = []
            for face in indices:
                if face[0] not in indices_list:
                    indices_list.append(face[0])
                    vertices_fixed.append(vertices[face[0][0]])
                    normals_fixed.append(normals[face[0][2]])
                    uvs_fixed.append(uvs[face[0][1]])
                if face[1] not in indices_list:
                    indices_list.append(face[1])
                    vertices_fixed.append(vertices[face[1][0]])
                    normals_fixed.append(normals[face[1][2]])
                    uvs_fixed.append(uvs[face[1][1]])
                if face[2] not in indices_list:
                    indices_list.append(face[2])
                    vertices_fixed.append(vertices[face[2][0]])
                    normals_fixed.append(normals[face[2][2]])
                    uvs_fixed.append(uvs[face[2][1]])
                indices_fixed.append([indices_list.index(face[0]), indices_list.index(face[1]), indices_list.index(face[2])])

            vertices = vertices_fixed
            normals = normals_fixed
            uvs = uvs_fixed
            faces = indices_fixed
            
            vertices_array = np.array(vertices, dtype=np.float32)
            normals_array = np.array(normals, dtype=np.float32)
            uvs_array = np.array(uvs, dtype=np.float32)
            triangles_array = np.array(faces, dtype=np.uint16)

            accessors.append(pygltflib.Accessor(
                name="part%i_vertices" % (i),
                bufferView=0,
                byteOffset=len(vertices_bytes),
                componentType=pygltflib.FLOAT,
                count=len(vertices),
                type=pygltflib.VEC3,
                max=vertices_array.max(axis=0).tolist(),
                min=vertices_array.min(axis=0).tolist()
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_normals" % (i),
                bufferView=1,
                byteOffset=len(normals_bytes),
                componentType=pygltflib.FLOAT,
                count=len(normals),
                type=pygltflib.VEC3,
                max=normals_array.max(axis=0).tolist(),
                min=normals_array.min(axis=0).tolist(),
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_uvs" % (i),
                bufferView=2,
                byteOffset=len(uvs_bytes),
                componentType=pygltflib.FLOAT,
                count=len(uvs),
                type=pygltflib.VEC2,
                max=uvs_array.max(axis=0).tolist(),
                min=uvs_array.min(axis=0).tolist(),
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_indices" % (i),
                bufferView=3,
                byteOffset=len(triangles_bytes),
                componentType=pygltflib.UNSIGNED_SHORT,
                count=triangles_array.size,
                type=pygltflib.SCALAR,
                max=[int(triangles_array.max())],
                min=[int(triangles_array.min())],
            ))

            meshes.append(pygltflib.Mesh(
                name="part" + str(i),
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(
                            POSITION=(i * 4),
                            NORMAL=(i * 4) + 1,
                            TEXCOORD_0=(i * 4) + 2
                        ),
                        indices=(i * 4) + 3,
                        material=0,
                        mode=pygltflib.TRIANGLES
                    )
                ]
            ))

            vertices_bytes += vertices_array.tobytes()
            normals_bytes += normals_array.tobytes()
            uvs_bytes += uvs_array.tobytes()
            triangles_bytes += triangles_array.flatten().tobytes()
    
        buffer_bytes = vertices_bytes + normals_bytes + uvs_bytes + triangles_bytes + texture_bytes
        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[i for i in range(len(klfx.parts))])],
            meshes=meshes,
            accessors=accessors,
            nodes=[
                *[pygltflib.Node(name="part" + str(i), mesh=i) for i in range(len(klfx.parts)) if klfx.parts[i].subpart_count != 0]
            ],
            buffers=[
                pygltflib.Buffer(
                    byteLength=len(buffer_bytes),
                    uri="data:application/gltf-buffer;base64," + base64.b64encode(buffer_bytes).decode("utf-8")
                )
            ],
            bufferViews=[
                pygltflib.BufferView(
                    name="vertices",
                    buffer=0,
                    byteLength=len(vertices_bytes),
                    byteOffset=0,
                    byteStride=12,
                    target=pygltflib.ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="normals",
                    buffer=0,
                    byteLength=len(normals_bytes),
                    byteOffset=len(vertices_bytes),
                    byteStride=12,
                    target=pygltflib.ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="uvs",
                    buffer=0,
                    byteLength=len(uvs_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes),
                    byteStride=8,
                    target=pygltflib.ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="indices",
                    buffer=0,
                    byteLength=len(triangles_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(uvs_bytes),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="texture",
                    buffer=0,
                    byteLength=len(texture_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(uvs_bytes) + len(triangles_bytes),
                ),
            ],
            images=[
                pygltflib.Image(
                    name=os.path.basename(texture_path),
                    mimeType="image/png",
                    bufferView=4
                )
            ],
            materials=[
                pygltflib.Material(
                    name="mtl0",
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        baseColorTexture=pygltflib.TextureInfo(
                            index=0
                        ),
                        baseColorFactor=[1, 1, 1, 1],
                        metallicFactor=0,
                        roughnessFactor=1
                    ),
                    emissiveFactor=[0, 0, 0],
                    alphaMode=pygltflib.OPAQUE,
                    doubleSided=True
                )
            ],
            samplers=[
                pygltflib.Sampler(
                    magFilter=pygltflib.NEAREST,
                    minFilter=pygltflib.NEAREST,
                    wrapS=pygltflib.REPEAT,
                    wrapT=pygltflib.REPEAT
                )
            ],
            textures=[
                pygltflib.Texture(
                    name=os.path.basename(texture_path),
                    sampler=0,
                    source=0
                )
            ]
        )

        gltf.save(gltf_filename)
        

