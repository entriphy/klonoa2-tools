from lib.structs.klfa_struct import Klfa
from lib.structs.klfb_struct import Klfb
from typing import List

from kaitaistruct import KaitaiStream
from ..structs.klfz_struct import Klfz
import os, math, base64
import filetype as ft
import numpy as np
import pygltflib
from ..structs.klfx_struct import Klfx
from ..util.read_bytes import u16le
from ..util.klfx_indices import parse_faces
from scipy.spatial.transform import Rotation

class KLFX(ft.Type):
    MIME = ""
    EXTENSION = "klfx"
    MAGIC = bytearray([0x46, 0x58])

    def __init__(self):
        super().__init__(self.MIME, self.EXTENSION)

    def match(self, buf):
        return buf[:len(self.MAGIC)] == self.MAGIC and buf[0x04] == 0x80 and buf[0x06] == 0x40

    def to_obj(path: str, textures: List[str] = []):
        buf = open(path, "rb").read()
        klfx = Klfx.from_bytes(buf)
        scale = klfx.header.scale
        obj_filename = path.replace(".klfx", ".obj")
        obj = open(obj_filename, "w")
        mtl_filename = path.replace(".klfx", ".mtl")
        obj.write("mtllib %s\n" % os.path.basename(mtl_filename))
        obj.write("usemtl mtl0\n\n")
        vertex_acc, normal_acc, uv_acc = 1, 1, 1
        for i, part in enumerate(klfx.parts):
            if part.subpart_count > 0:
                vertices, normals = [], []
                for subpart in part.subparts:
                    vertices += [(vertex.x * scale, -vertex.y * scale, -vertex.z * scale) for vertex in subpart.vertices]
                    normals += [[normal.x / 0xFFFF, -normal.y / 0xFFFF, -normal.z / 0xFFFF] for normal in subpart.normals]
            else:
                vertices = [(vertex.x * scale, -vertex.y * scale, -vertex.z * scale) for vertex in part.vertices]
                normals = [[normal.x / 0xFFFF, -normal.y / 0xFFFF, -normal.z / 0xFFFF] for normal in part.normals]
            uvs = part.uvs
            faces = parse_faces(buf, part, vertices, normals)

            obj.write("# -- Part %i ---\ng part%i\n\n" % (i, i))
            obj.write("# Vertex count: %i\n" % part.vertex_count)
            # It takes ten times longer if everything is divided in the Kaitai struct.
            # lol...?
            for vertex in vertices: obj.write("v  %.7f %.7f %.7f\n" % (vertex[0], vertex[1], vertex[2]))
            obj.write("\n# Normal count: %i\n" % part.normal_count)
            for normal in normals: obj.write("vn %.7f %.7f %.7f\n" % (normal[0], normal[1], normal[2]))
            obj.write("\n# UV count: %i\n" % part.uv_count)
            for uv in uvs: obj.write("vt %.15f %.15f\n" % (uv.u / 16384, 1.0 - uv.v / 16384))
            obj.write("\n# Face count: %i\n" % len(faces))
            has_uvs = part.uv_count > 0
            for face in faces: obj.write("f %i/%i/%i %i/%i/%i %i/%i/%i\n" % (
                vertex_acc + face[0][0], (uv_acc + face[0][1]) if has_uvs else (uv_acc + face[0][1] - 1), normal_acc + face[0][2],
                vertex_acc + face[1][0], (uv_acc + face[1][1]) if has_uvs else (uv_acc + face[1][1] - 1), normal_acc + face[1][2],
                vertex_acc + face[2][0], (uv_acc + face[2][1]) if has_uvs else (uv_acc + face[2][1] - 1), normal_acc + face[2][2]
            ))
            obj.write("\n")

            vertex_acc += part.vertex_count
            normal_acc += part.normal_count
            uv_acc     += part.uv_count
    
        obj.close()

        mtl = open(mtl_filename, "w")
        for i, texture in enumerate(textures):
            mtl.write(f"newmtl mtl{i}\nKa 0.2 0.2 0.2\nKd 0.50000 0.50000 0.50000\nKs 0.00000 0.00000 0.00000\nd 1.00000\nillum 1\nmap_Kd {os.path.basename(texture)}\n\n")
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
    
    def to_gltf(path: str, textures: List[str], joints_path: str, animations: List[str] = [], morphs: List[str] = [], embed_textures: bool = True):
        buf = open(path, "rb").read()
        klfx = Klfx.from_bytes(buf)
        klfb = Klfb(KaitaiStream(open(joints_path, "rb")))
        gltf_filename = path.replace(".klfx", ".gltf")
        vertices_bytes = bytes()
        normals_bytes = bytes()
        weights_bytes = bytes()
        joints_bytes = bytes()
        inverse_matrix_bytes = bytes()
        uvs_bytes = bytes()
        triangles_bytes = bytes()
        if len(morphs) > 0: morphs = [Klfz(klfx, KaitaiStream(open(morph, "rb"))) for morph in morphs]

        meshes = []
        accessors = []

        for i, part in enumerate(klfx.parts):
            # if part.subpart_count == 0: continue # TODO: Find out what it means when this equals zero instead of skipping it
            vertices, normals, weights, joints = [], [], [], []
            for subpart in part.subparts:
                vertices += [[vertex.x * klfx.header.scale, -vertex.y * klfx.header.scale, -vertex.z * klfx.header.scale] for vertex in subpart.vertices]
                normals += [[normal.x / 0xFFFF, -normal.y / 0xFFFF, -normal.z / 0xFFFF] for normal in subpart.normals]
                weights += [[weight.a / 0xFF, weight.b / 0XFF, weight.c / 0XFF, weight.d / 0XFF] for weight in subpart.weights]
                joints += [[subpart.joints.a + 1, subpart.joints.b + 1 if subpart.joints.b != 0xFFFF else 0, subpart.joints.c + 1 if subpart.joints.c != 0xFFFF else 0, subpart.joints.d + 1 if subpart.joints.d != 0xFFFF else 0] for i in range(len(subpart.vertices))]
            uvs = [[uv.u / 16384, uv.v / 16384] for uv in part.uvs]
            indices = parse_faces(buf, part, vertices, normals)
            faces = [[face[0][0], face[1][0], face[2][0]] for face in indices]

            # glTF does not support multiple normals/UVs on one vertex
            # So we have to do this...
            indices_list = []
            vertices_fixed = []
            normals_fixed = []
            weights_fixed = []
            joints_fixed = []
            uvs_fixed = []
            indices_fixed = []
            vertices_map = []
            for face in indices:
                for x in range(3):
                    if face[x] not in indices_list:
                        indices_list.append(face[x])
                        vertices_fixed.append(vertices[face[x][0]])
                        normals_fixed.append(normals[face[x][2]])
                        weights_fixed.append(weights[face[x][0]])
                        joints_fixed.append(joints[face[x][0]])
                        uvs_fixed.append(uvs[face[x][1]])
                        vertices_map.append(face[x][0])
                indices_fixed.append([indices_list.index(face[0]), indices_list.index(face[1]), indices_list.index(face[2])])

            vertices = vertices_fixed
            normals = normals_fixed
            weights = weights_fixed
            joints = joints_fixed
            uvs = uvs_fixed
            faces = indices_fixed
            
            vertices_array = np.array(vertices, dtype=np.float32)
            normals_array = np.array(normals, dtype=np.float32)
            weights_array = np.array(weights, dtype=np.float32)
            joints_array = np.array(joints, dtype=np.uint16)
            uvs_array = np.array(uvs, dtype=np.float32)
            triangles_array = np.array(faces, dtype=np.uint16)

            mesh = pygltflib.Mesh(
                name="part" + str(i),
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(
                            POSITION=len(accessors),
                            NORMAL=len(accessors) + 1,
                            WEIGHTS_0=len(accessors) + 2,
                            JOINTS_0=len(accessors) + 3,
                            TEXCOORD_0=len(accessors) + 4
                        ),
                        targets=[],
                        indices=len(accessors) + 5,
                        material=0,
                        mode=pygltflib.TRIANGLES
                    )
                ]
            )

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
                name="part%i_weights" % (i),
                bufferView=2,
                byteOffset=len(weights_bytes),
                componentType=pygltflib.FLOAT,
                count=len(weights),
                type=pygltflib.VEC4,
                max=weights_array.max(axis=0).tolist(),
                min=weights_array.min(axis=0).tolist(),
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_joints" % (i),
                bufferView=3,
                byteOffset=len(joints_bytes),
                componentType=pygltflib.UNSIGNED_SHORT,
                count=len(joints),
                type=pygltflib.VEC4,
                max=joints_array.max(axis=0).tolist(),
                min=joints_array.min(axis=0).tolist(),
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_uvs" % (i),
                bufferView=5,
                byteOffset=len(uvs_bytes),
                componentType=pygltflib.FLOAT,
                count=len(uvs),
                type=pygltflib.VEC2,
                max=uvs_array.max(axis=0).tolist(),
                min=uvs_array.min(axis=0).tolist(),
            ))
            accessors.append(pygltflib.Accessor(
                name="part%i_indices" % (i),
                bufferView=6,
                byteOffset=len(triangles_bytes),
                componentType=pygltflib.UNSIGNED_SHORT,
                count=triangles_array.size,
                type=pygltflib.SCALAR,
                max=[int(triangles_array.max())],
                min=[int(triangles_array.min())],
            ))


            vertices_bytes += vertices_array.tobytes()
            normals_bytes += normals_array.tobytes()
            weights_bytes += weights_array.tobytes()
            joints_bytes += joints_array.tobytes()
            uvs_bytes += uvs_array.tobytes()
            triangles_bytes += triangles_array.flatten().tobytes()

            if len(morphs) > 0:
                for x, morph in enumerate(morphs):
                    if morph.parts[0].part_number != i: continue
                    morph_vertices = []
                    morph_normals = []
                    for subpart in morph.parts[0].subparts:
                        morph_vertices += [[vertex.x * morph.header.scale, -vertex.y * morph.header.scale, -vertex.z * morph.header.scale] for vertex in subpart.vertices]
                        morph_normals += [[normal.x / 0xFFFF, -normal.y / 0xFFFF, -normal.z / 0xFFFF] for normal in subpart.normals]

                    morph_vertices_fixed = []
                    morph_normals_fixed = []
                    for idx in vertices_map:
                        morph_vertices_fixed.append([morph_vertices[idx][0] - vertices[vertices_map.index(idx)][0], morph_vertices[idx][1] - vertices[vertices_map.index(idx)][1], morph_vertices[idx][2] - vertices[vertices_map.index(idx)][2]])
                        morph_normals_fixed.append([morph_normals[idx][0] - normals[vertices_map.index(idx)][0], morph_normals[idx][1] - normals[vertices_map.index(idx)][1], morph_normals[idx][2] - normals[vertices_map.index(idx)][2]])

                    morph_vertices = morph_vertices_fixed
                    morph_normals = morph_normals_fixed

                    morph_vertices_array = np.array(morph_vertices, dtype=np.float32)
                    morph_normals_array = np.array(morph_normals, dtype=np.float32)
                    
                    mesh.primitives[0].targets.append(
                        pygltflib.Attributes(
                            POSITION=len(accessors),
                            NORMAL=len(accessors) + 1,
                        )
                    )

                    accessors.append(pygltflib.Accessor(
                        name="part%i_morph%i_vertices" % (i, x),
                        bufferView=0,
                        byteOffset=len(vertices_bytes),
                        componentType=pygltflib.FLOAT,
                        count=len(morph_vertices),
                        type=pygltflib.VEC3,
                        max=morph_vertices_array.max(axis=0).tolist(),
                        min=morph_vertices_array.min(axis=0).tolist()
                    ))
                    accessors.append(pygltflib.Accessor(
                        name="part%i_morph%i_normals" % (i, x),
                        bufferView=1,
                        byteOffset=len(normals_bytes),
                        componentType=pygltflib.FLOAT,
                        count=len(morph_normals),
                        type=pygltflib.VEC3,
                        max=morph_normals_array.max(axis=0).tolist(),
                        min=morph_normals_array.min(axis=0).tolist(),
                    ))

                    vertices_bytes += morph_vertices_array.tobytes()
                    normals_bytes += morph_normals_array.tobytes()

            meshes.append(mesh)
        
        inverse_matrix = []
        inverse_matrix.append([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        for joint in klfb.global_joints:
            inverse_matrix.append([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -joint.x, joint.y, joint.z, 1.0])
        inverse_matrix_array = np.array(inverse_matrix, dtype=np.float32)
        inverse_matrix_bytes = inverse_matrix_array.tobytes()
        accessors.append(pygltflib.Accessor(
            name="inverse_matrix",
            bufferView=4,
            byteOffset=0,
            componentType=pygltflib.FLOAT,
            count=len(inverse_matrix),
            type=pygltflib.MAT4,
            max=inverse_matrix_array.max(axis=0).tolist(),
            min=inverse_matrix_array.min(axis=0).tolist()
        ))
    
        buffer_bytes = vertices_bytes + normals_bytes + weights_bytes + joints_bytes + inverse_matrix_bytes + uvs_bytes + triangles_bytes
        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[x for x in range(len(klfx.parts) + 1)])],
            meshes=meshes,
            accessors=accessors,
            nodes=[
                *[pygltflib.Node(name="part" + str(x), mesh=x, skin=0) for x in range(len(klfx.parts)) if klfx.parts[x].subpart_count != 0],
                pygltflib.Node(name="root_joint", children=[]),
                *[pygltflib.Node(name="joint" + str(x), translation=[joint.x, -joint.y, -joint.z]) for x, joint in enumerate(klfb.local_joints)]
            ],
            skins=[
                pygltflib.Skin(
                    joints=[x for x in range(len(klfx.parts), len(klfx.parts) + len(klfb.global_joints) + 1)],
                    inverseBindMatrices=len(accessors) - 1,
                    skeleton=len(klfx.parts)
                )
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
                    name="weights",
                    buffer=0,
                    byteLength=len(weights_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes),
                    byteStride=16,
                    target=pygltflib.ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="joints",
                    buffer=0,
                    byteLength=len(joints_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(weights_bytes),
                    byteStride=8,
                ),
                pygltflib.BufferView(
                    name="inverse_matrix",
                    buffer=0,
                    byteLength=len(inverse_matrix_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(weights_bytes) + len(joints_bytes),
                ),
                pygltflib.BufferView(
                    name="uvs",
                    buffer=0,
                    byteLength=len(uvs_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(weights_bytes) + len(joints_bytes) + len(inverse_matrix_bytes),
                    byteStride=8,
                    target=pygltflib.ARRAY_BUFFER
                ),
                pygltflib.BufferView(
                    name="indices",
                    buffer=0,
                    byteLength=len(triangles_bytes),
                    byteOffset=len(vertices_bytes) + len(normals_bytes) + len(weights_bytes) + len(joints_bytes) + len(inverse_matrix_bytes) + len(uvs_bytes),
                    target=pygltflib.ELEMENT_ARRAY_BUFFER
                )
            ],
            images=[
                pygltflib.Image(
                    name=os.path.basename(texture),
                    uri=os.path.basename(texture)
                ) for texture in textures
            ] if not embed_textures else [
                pygltflib.Image(
                    name=os.path.basename(texture),
                    mimeType="image/png",
                    bufferView=7 + x
                ) for x, texture in enumerate(textures)
            ],
            materials=[
                pygltflib.Material(
                    name="mtl" + str(x),
                    pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                        baseColorTexture=pygltflib.TextureInfo(
                            index=x
                        ),
                        baseColorFactor=[1, 1, 1, 1],
                        metallicFactor=0,
                        roughnessFactor=1
                    ),
                    emissiveFactor=[0, 0, 0],
                    alphaMode=pygltflib.OPAQUE,
                    alphaCutoff=None,
                    doubleSided=True
                ) for x in range(len(textures))
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
                    name=os.path.basename(texture),
                    sampler=0,
                    source=x
                ) for x, texture in enumerate(textures)
            ]
        )

        joints_start = len(klfx.parts) + 1 # Node index of joint0; subtract 1 to get root_joint
        for x, joint in enumerate(klfb.global_joints):
            parent_joint = klfb.parent_joints[x]
            if parent_joint == 0xFFFF:
                gltf.nodes[joints_start - 1].children.append(joints_start + x)
            else:
                if gltf.nodes[joints_start + parent_joint].children == None: gltf.nodes[joints_start + parent_joint].children = []
                gltf.nodes[joints_start + parent_joint].children.append(joints_start + x)

        if embed_textures:
            textures_bytes = [open(texture, "rb").read() for texture in textures]
            for x, texture in enumerate(textures_bytes):
                gltf.bufferViews.append(
                    pygltflib.BufferView(
                        name="texture_%i" % x,
                        buffer=0,
                        byteLength=len(texture),
                        byteOffset=len(buffer_bytes)
                    )
                )
                buffer_bytes += texture

        translations_bytes = bytes()
        translations_keyframes_bytes = bytes()
        rotations_bytes = bytes()
        rotations_keyframes_bytes = bytes()

        def euler_to_quat(rotation):
            # x = rotation.x / 0xFFFF * 360
            # if x > 180.0: x = -360 + x
            # y = -rotation.y / 0xFFFF * 360
            # if y < -180.0: y = 360 + y
            # z = -rotation.z / 0xFFFF * 360
            # if z < -180.0: z = 360 + z

            return Rotation.from_euler("XYZ", [rotation.x / 0xFFFF * 360, -rotation.y / 0xFFFF * 360, -rotation.z / 0xFFFF * 360], degrees=True).as_quat()

        anim_list = []
        for animation in animations:
            try:
                klfa = Klfa.from_file(animation)
                scale = klfa.scale
                anim_name = klfa.name.replace("\u0000", "") # Removes empty unicode characters
                if anim_name in anim_list: continue
                else: anim_list.append(anim_name)
                samplers = []
                channels = []

                # Initial position
                root_keyframes_array = np.array([(float(klfa.keyframe_count) - 1.0) / 60.0], dtype=np.float32)
                root_translations_array = np.array([[klfa.initial_pos.x, -klfa.initial_pos.y, -klfa.initial_pos.z]], dtype=np.float32)
                root_keyframes_array_bytes = root_keyframes_array.tobytes()
                root_translations_array_bytes = root_translations_array.tobytes()
                gltf.accessors.append(
                    pygltflib.Accessor(
                        name="anim_%s_root_trans_keyframes" % (anim_name),
                        bufferView=len(gltf.bufferViews) + 1,
                        byteOffset=len(translations_keyframes_bytes),
                        count=len(root_keyframes_array),
                        type=pygltflib.SCALAR,
                        componentType=pygltflib.FLOAT,
                        max=[root_keyframes_array.max().tolist()],
                        min=[root_keyframes_array.min().tolist()],
                    )
                )
                gltf.accessors.append(
                    pygltflib.Accessor(
                        name="anim_%s_root_trans" % (anim_name),
                        bufferView=len(gltf.bufferViews),
                        byteOffset=len(translations_bytes),
                        count=len(root_translations_array),
                        type=pygltflib.VEC3,
                        componentType=pygltflib.FLOAT,
                        max=root_translations_array.max(axis=0).tolist(),
                        min=root_translations_array.min(axis=0).tolist(),
                    )
                )
                samplers.append(
                    pygltflib.AnimationSampler(
                        interpolation=pygltflib.ANIM_LINEAR,
                        input=len(gltf.accessors) - 2,
                        output=len(gltf.accessors) - 1
                    )
                )
                channels.append(
                    pygltflib.AnimationChannel(
                        sampler=len(samplers) - 1,
                        target=pygltflib.AnimationChannelTarget(
                            node=joints_start - 1,
                            path=pygltflib.TRANSLATION
                        )
                    )
                )

                translations_bytes += root_translations_array_bytes
                translations_keyframes_bytes += root_keyframes_array_bytes

                for i, joint_translation in enumerate(klfa.joint_translations):
                    translations_array = np.array([[translation.x * scale, -translation.y * scale, -translation.z * scale] for translation in joint_translation.coordinates], dtype=np.float32)
                    translations_keyframes_array = np.array([(float(keyframe) - 1.0) / 60.0 for keyframe in joint_translation.keyframes], dtype=np.float32)
                    rotations_array = np.array([euler_to_quat(rotation) for rotation in klfa.joint_rotations[i].rotations], dtype=np.float32)
                    rotations_keyframes_array = np.array([(float(keyframe) - 1.0) / 60.0 for keyframe in klfa.joint_rotations[i].keyframes], dtype=np.float32)

                    translations_array_bytes = translations_array.tobytes()
                    translations_keyframes_array_bytes = translations_keyframes_array.tobytes()
                    rotations_array_bytes = rotations_array.tobytes()
                    rotations_keyframes_array_bytes = rotations_keyframes_array.tobytes()

                    # Keyframes
                    gltf.accessors.append(
                        pygltflib.Accessor(
                            name="anim_%s_joint%i_trans_keyframes" % (anim_name, i),
                            bufferView=len(gltf.bufferViews) + 1,
                            byteOffset=len(translations_keyframes_bytes),
                            count=len(translations_keyframes_array),
                            type=pygltflib.SCALAR,
                            componentType=pygltflib.FLOAT,
                            max=[translations_keyframes_array.max().tolist()],
                            min=[translations_keyframes_array.min().tolist()],
                        )
                    )
                    # Translation
                    gltf.accessors.append(
                        pygltflib.Accessor(
                            name="anim_%s_joint%i_trans" % (anim_name, i),
                            bufferView=len(gltf.bufferViews),
                            byteOffset=len(translations_bytes),
                            count=len(translations_array),
                            type=pygltflib.VEC3,
                            componentType=pygltflib.FLOAT,
                            max=translations_array.max(axis=0).tolist(),
                            min=translations_array.min(axis=0).tolist(),
                        )
                    )
                    samplers.append(
                        pygltflib.AnimationSampler(
                            interpolation=pygltflib.ANIM_LINEAR,
                            input=len(gltf.accessors) - 2,
                            output=len(gltf.accessors) - 1
                        )
                    )
                    channels.append(
                        pygltflib.AnimationChannel(
                            sampler=len(samplers) - 1,
                            target=pygltflib.AnimationChannelTarget(
                                node=joints_start + i,
                                path=pygltflib.TRANSLATION
                            )
                        )
                    )

                    translations_bytes += translations_array_bytes
                    translations_keyframes_bytes += translations_keyframes_array_bytes

                    # Keyframes
                    gltf.accessors.append(
                        pygltflib.Accessor(
                            name="anim_%s_joint%i_rot_keyframes" % (anim_name, i),
                            bufferView=len(gltf.bufferViews) + 3,
                            byteOffset=len(rotations_keyframes_bytes),
                            count=len(rotations_keyframes_array),
                            type=pygltflib.SCALAR,
                            componentType=pygltflib.FLOAT,
                            max=[rotations_keyframes_array.max().tolist()],
                            min=[rotations_keyframes_array.min().tolist()],
                        )
                    )
                    # Translation
                    gltf.accessors.append(
                        pygltflib.Accessor(
                            name="anim_%s_joint%i_rot" % (anim_name, i),
                            bufferView=len(gltf.bufferViews) + 2,
                            byteOffset=len(rotations_bytes),
                            count=len(rotations_array),
                            type=pygltflib.VEC4,
                            componentType=pygltflib.FLOAT,
                            max=rotations_array.max(axis=0).tolist(),
                            min=rotations_array.min(axis=0).tolist(),
                        )
                    )
                    samplers.append(
                        pygltflib.AnimationSampler(
                            interpolation=pygltflib.ANIM_LINEAR,
                            input=len(gltf.accessors) - 2,
                            output=len(gltf.accessors) - 1
                        )
                    )
                    channels.append(
                        pygltflib.AnimationChannel(
                            sampler=len(samplers) - 1,
                            target=pygltflib.AnimationChannelTarget(
                                node=joints_start + i,
                                path=pygltflib.ROTATION
                            )
                        )
                    )

                    rotations_bytes += rotations_array_bytes
                    rotations_keyframes_bytes += rotations_keyframes_array_bytes
                
                if gltf.animations == None: gltf.animations = []
                gltf.animations.append(
                    pygltflib.Animation(
                        name=anim_name,
                        samplers=samplers,
                        channels=channels
                    )
                )
            except Exception as e:
                print(f"@@@ anim {animation}: {e}")
                pass

        if len(anim_list) > 0:
            if len(buffer_bytes) % 4 != 0: buffer_bytes += b"\0" * (4 - (len(buffer_bytes) % 4))
            
            gltf.bufferViews.append(
                pygltflib.BufferView(
                    name="anim_translations",
                    buffer=0,
                    byteLength=len(translations_bytes),
                    byteOffset=len(buffer_bytes)
                )
            )
            buffer_bytes += translations_bytes

            gltf.bufferViews.append(
                pygltflib.BufferView(
                    name="anim_translations_keyframes",
                    buffer=0,
                    byteLength=len(translations_keyframes_bytes),
                    byteOffset=len(buffer_bytes)
                )
            )
            buffer_bytes += translations_keyframes_bytes

            gltf.bufferViews.append(
                pygltflib.BufferView(
                    name="anim_rotations",
                    buffer=0,
                    byteLength=len(rotations_bytes),
                    byteOffset=len(buffer_bytes)
                )
            )
            buffer_bytes += rotations_bytes

            gltf.bufferViews.append(
                pygltflib.BufferView(
                    name="anim_rotations_keyframes",
                    buffer=0,
                    byteLength=len(rotations_keyframes_bytes),
                    byteOffset=len(buffer_bytes)
                )
            )
            buffer_bytes += rotations_keyframes_bytes



        gltf.buffers = [pygltflib.Buffer(byteLength=len(buffer_bytes), uri="data:application/gltf-buffer;base64," + base64.b64encode(buffer_bytes).decode("utf-8"))]
        gltf.save(gltf_filename)
