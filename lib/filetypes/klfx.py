from lib.structs.klfa_struct import Klfa
from lib.structs.klfa_alt_struct import KlfaAlt
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

    def to_obj(path: str, mtl_path: str = "", textures: List[str] = []):
        buf = open(path, "rb").read()
        klfx = Klfx.from_bytes(buf)
        scale = klfx.header.scale
        obj_filename = path.replace(".klfx", ".obj")
        obj = open(obj_filename, "w")
        obj.write(f"mtllib {os.path.basename(mtl_path)}\n")
        obj.write("usemtl mtl0\n\n")
        vertex_acc, normal_acc, uv_acc = 1, 1, 1
        for i, part in enumerate(klfx.parts):
            if part.subpart_count > 0:
                vertices, normals = [], []
                for subpart in part.subparts:
                    vertices += [(vertex.x * scale, -vertex.y * scale, -vertex.z * scale) for vertex in subpart.vertices]
                    normals += [[normal.x / 0x1000, -normal.y / 0x1000, -normal.z / 0x1000] for normal in subpart.normals]
            else:
                vertices = [(vertex.x * scale, -vertex.y * scale, -vertex.z * scale) for vertex in part.vertices]
                normals = [[normal.x / 0x1000, -normal.y / 0x1000, -normal.z / 0x1000] for normal in part.normals]
            uvs = part.uvs
            faces = parse_faces(buf, part, vertices, normals)

            obj.write(f"# -- Part {i} ---\ng part{i}\n\n")
            obj.write(f"# Vertex count: {part.vertex_count}\n")
            # It takes ten times longer if everything is divided in the Kaitai struct.
            # lol...?
            for vertex in vertices: obj.write("v  %.7f %.7f %.7f\n" % (vertex[0], vertex[1], vertex[2]))
            obj.write(f"\n# Normal count: {part.normal_count}\n")
            for normal in normals: obj.write("vn %.7f %.7f %.7f\n" % (normal[0], normal[1], normal[2]))
            obj.write(f"\n# UV count: {part.uv_count}\n")
            for uv in uvs: obj.write("vt %.15f %.15f\n" % (uv.u / 16384, 1.0 - uv.v / 16384))
            obj.write(f"\n# Face count: {len(faces)}\n")
            has_uvs = part.uv_count > 0
            if not has_uvs: print(f"@@@ no UVs: {path}")
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
    
    def to_gltf(path: str, textures: List[str] = [], klfb: str = "", animations: List[str] = [], morphs: List[str] = [], embed_textures: bool = True, klonoa_fix: bool = False, output_file: str = ""):
        if output_file == "": output_file = path.replace(".klfx", ".gltf")
        if klfb != "": klfb = Klfb(KaitaiStream(open(klfb, "rb")))

        buf = open(path, "rb").read()
        klfx = Klfx.from_bytes(buf)
        
        vertices_bytes = bytes()
        normals_bytes = bytes()
        uvs_bytes = bytes()
        joints_bytes = bytes()
        weights_bytes = bytes()
        triangles_bytes = bytes()
        inverse_matrix_bytes = bytes()
        
        morph_list = morphs # Keep original file names
        morphs = [Klfz(klfx, KaitaiStream(open(morph, "rb"))) for morph in morphs]
        morph_map = {} # Used for morph animations
        
        fps = 60
        buffer_bytes = bytes()
        gltf = pygltflib.GLTF2(
            scene=0,
            scenes=[pygltflib.Scene(nodes=[])],
        )

        for i, part in enumerate(klfx.parts):
            vertices, normals, joints, weights = [], [], [], []
            if part.subpart_count > 0:
                for subpart in part.subparts:
                    vertices += [[vertex.x * klfx.header.scale, -vertex.y * klfx.header.scale, -vertex.z * klfx.header.scale] for vertex in subpart.vertices]
                    normals += [[normal.x / 0x1000, -normal.y / 0x1000, -normal.z / 0x1000] for normal in subpart.normals]
                    if klfb != "":
                        # Disable cheek joints code
                        if klonoa_fix and "Low" not in path and i == 5:
                            joints += [[19, 0, 0, 0] for i in range(len(subpart.vertices))]
                            weights += [[1.0, 0.0, 0.0, 0.0] for weight in subpart.weights]
                        else:
                            joints += [[subpart.joints.a + 1, subpart.joints.b + 1 if subpart.joints.b != 0xFFFF else 0, subpart.joints.c + 1 if subpart.joints.c != 0xFFFF else 0, subpart.joints.d + 1 if subpart.joints.d != 0xFFFF else 0] for i in range(len(subpart.vertices))]
                            for weight in subpart.weights:
                                # The vertex weights sometimes don't add up to 0xFF, so they are divided by the sum.
                                weights_sum = weight.a + weight.b + weight.c + weight.d
                                weights.append([weight.a / weights_sum, weight.b / weights_sum, weight.c / weights_sum, weight.d / weights_sum])
            else:
                vertices += [[vertex.x * klfx.header.scale, -vertex.y * klfx.header.scale, -vertex.z * klfx.header.scale] for vertex in part.vertices]
                normals += [[normal.x / 0x1000, -normal.y / 0x1000, -normal.z / 0x1000] for normal in part.normals]
                if klfb != "":
                    joints += [[0, 0, 0, 0] for _ in range(len(part.vertices))]
                    weights += [[0.0, 0.0, 0.0, 0.0] for _ in range(len(part.vertices))]

            if part.uv_count == 0: 
                print(f"@@@ no UVs: {i}, {path}")
                uvs = [uvs[-1]] # this is illegal lol
            else:
                uvs = [[uv.u / 16384, uv.v / 16384] for uv in part.uvs]
            
            indices = parse_faces(buf, part, vertices, normals)
            faces = [[face[0][0], face[1][0], face[2][0]] for face in indices]

            # glTF does not support multiple normals/UVs on one vertex
            # So we have to do this...
            indices_list = []
            vertices_fixed = []
            normals_fixed = []
            uvs_fixed = []
            joints_fixed = []
            weights_fixed = []
            indices_fixed = []
            vertices_map = []
            for face in indices:
                for x in range(3):
                    if face[x] not in indices_list:
                        indices_list.append(face[x])
                        vertices_fixed.append(vertices[face[x][0]])
                        normals_fixed.append(normals[face[x][2]])
                        uvs_fixed.append(uvs[face[x][1]])
                        if klfb != "":
                            # Fix glTF errors/warnings
                            joint = joints[face[x][0]]
                            weight = weights[face[x][0]]
                            for j in range(len(joint)):
                                if klfb != "" and joint[j] - 1 > klfb.count: 
                                    joint[j] = 0
                            if sum(weight) != 1.0:
                                weight[weight.index(max(weight))] += 1 - sum(weight)
                            for z in range(len(weight)):
                                if weight[z] == 0.0 and joint[z] != 0: joint[z] = 0
                            joints_fixed.append(joint)
                            weights_fixed.append(weight)
                        vertices_map.append(face[x][0])
                indices_fixed.append([indices_list.index(face[0]), indices_list.index(face[1]), indices_list.index(face[2])])

            # We don't need the old values, so just replace them
            vertices = vertices_fixed
            normals = normals_fixed
            weights = weights_fixed
            joints = joints_fixed
            uvs = uvs_fixed
            faces = indices_fixed
            
            # Create byte arrays for mesh part
            vertices_array = np.array(vertices, dtype=np.float32)
            normals_array = np.array(normals, dtype=np.float32)
            uvs_array = np.array(uvs, dtype=np.float32)
            joints_array = np.array(joints, dtype=np.uint16)
            weights_array = np.array(weights, dtype=np.float32)
            triangles_array = np.array(faces, dtype=np.uint16)

            mesh = pygltflib.Mesh(
                name=f"part{i}",
                primitives=[
                    pygltflib.Primitive(
                        attributes=pygltflib.Attributes(
                            POSITION=len(gltf.accessors),
                            NORMAL=len(gltf.accessors) + 1,
                            TEXCOORD_0=len(gltf.accessors) + 2,
                            JOINTS_0=len(gltf.accessors) + 3,
                            WEIGHTS_0=len(gltf.accessors) + 4,
                        ) if klfb != "" else pygltflib.Attributes(
                            POSITION=len(gltf.accessors),
                            NORMAL=len(gltf.accessors) + 1,
                            TEXCOORD_0=len(gltf.accessors) + 2
                        ),
                        targets=[],
                        indices=len(gltf.accessors) + (5 if klfb != "" else 3),
                        material=1 if klonoa_fix and i in ([15, 17, 18] if "Low" in path else [17, 19, 20]) else 0,
                        mode=pygltflib.TRIANGLES
                    )
                ]
            )

            # Add accessor for the part to the glTF file
            gltf.accessors.append(pygltflib.Accessor(
                name=f"part{i}_vertices",
                bufferView=0,
                byteOffset=len(vertices_bytes),
                componentType=pygltflib.FLOAT,
                count=len(vertices),
                type=pygltflib.VEC3,
                max=vertices_array.max(axis=0).tolist(),
                min=vertices_array.min(axis=0).tolist()
            ))
            gltf.accessors.append(pygltflib.Accessor(
                name=f"part{i}_normals",
                bufferView=1,
                byteOffset=len(normals_bytes),
                componentType=pygltflib.FLOAT,
                count=len(normals),
                type=pygltflib.VEC3,
                max=normals_array.max(axis=0).tolist(),
                min=normals_array.min(axis=0).tolist(),
            ))
            gltf.accessors.append(pygltflib.Accessor(
                name=f"part{i}_uvs",
                bufferView=2,
                byteOffset=len(uvs_bytes),
                componentType=pygltflib.FLOAT,
                count=len(uvs),
                type=pygltflib.VEC2,
                max=uvs_array.max(axis=0).tolist(),
                min=uvs_array.min(axis=0).tolist(),
            ))
            # Only add rig-related stuff if a rig is defined
            if klfb != "":
                gltf.accessors.append(pygltflib.Accessor(
                    name=f"part{i}_joints",
                    bufferView=3,
                    byteOffset=len(joints_bytes),
                    componentType=pygltflib.UNSIGNED_SHORT,
                    count=len(joints),
                    type=pygltflib.VEC4,
                    max=joints_array.max(axis=0).tolist(),
                    min=joints_array.min(axis=0).tolist(),
                ))
                gltf.accessors.append(pygltflib.Accessor(
                    name=f"part{i}_weights",
                    bufferView=4,
                    byteOffset=len(weights_bytes),
                    componentType=pygltflib.FLOAT,
                    count=len(weights),
                    type=pygltflib.VEC4,
                    max=weights_array.max(axis=0).tolist(),
                    min=weights_array.min(axis=0).tolist(),
                ))
            gltf.accessors.append(pygltflib.Accessor(
                name=f"part{i}_indices",
                bufferView=5 if klfb != "" else 3,
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

            # Add morph targets to gltf
            if len(morphs) > 0:
                for x, morph in enumerate(morphs):
                    if morph.parts[0].part_number != i: continue
                    morph_vertices = []
                    morph_normals = []
                    for subpart in morph.parts[0].subparts:
                        morph_vertices += [[vertex.x * morph.header.scale, -vertex.y * morph.header.scale, -vertex.z * morph.header.scale] for vertex in subpart.vertices]
                        morph_normals += [[normal.x / 0x1000, -normal.y / 0x1000, -normal.z / 0x1000] for normal in subpart.normals]

                    morph_vertices_fixed = []
                    morph_normals_fixed = []
                    for idx in vertices_map:
                        # glTF uses displacement values for morphs, meaning we have to take the difference of the morph data and the original data
                        morph_vertices_fixed.append([morph_vertices[idx][0] - vertices[vertices_map.index(idx)][0], morph_vertices[idx][1] - vertices[vertices_map.index(idx)][1], morph_vertices[idx][2] - vertices[vertices_map.index(idx)][2]])
                        morph_normals_fixed.append([morph_normals[idx][0] - normals[vertices_map.index(idx)][0], morph_normals[idx][1] - normals[vertices_map.index(idx)][1], morph_normals[idx][2] - normals[vertices_map.index(idx)][2]])

                    morph_vertices = morph_vertices_fixed
                    morph_normals = morph_normals_fixed

                    morph_vertices_array = np.array(morph_vertices, dtype=np.float32)
                    morph_normals_array = np.array(morph_normals, dtype=np.float32)
                    
                    mesh.primitives[0].targets.append(
                        pygltflib.Attributes(
                            POSITION=len(gltf.accessors),
                            NORMAL=len(gltf.accessors) + 1,
                        )
                    )

                    gltf.accessors.append(pygltflib.Accessor(
                        name=f"part{i}_morph{x}_vertices",
                        bufferView=0,
                        byteOffset=len(vertices_bytes),
                        componentType=pygltflib.FLOAT,
                        count=len(morph_vertices),
                        type=pygltflib.VEC3,
                        max=morph_vertices_array.max(axis=0).tolist(),
                        min=morph_vertices_array.min(axis=0).tolist()
                    ))
                    gltf.accessors.append(pygltflib.Accessor(
                        name=f"part{i}_morph{x}_normals",
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

                    # Keeps track of what the target mesh of each morph is
                    # Helpful for later when it comes to parsing animations that use morphs
                    morph_map[int(os.path.basename(morph_list[x]).split("_")[0])] = (i, len(mesh.primitives[0].targets) - 1)

            gltf.meshes.append(mesh)
            gltf.scenes[0].nodes.append(len(gltf.nodes))
            node = pygltflib.Node(name=f"part{i}", mesh=i)
            if klfb != "": node.skin = 0
            gltf.nodes.append(node)
            
        # Add buffer views
        gltf.bufferViews.append(pygltflib.BufferView(
            name="vertices",
            buffer=0,
            byteLength=len(vertices_bytes),
            byteOffset=0,
            byteStride=12,
            target=pygltflib.ARRAY_BUFFER
        ))
        buffer_bytes += vertices_bytes

        gltf.bufferViews.append(pygltflib.BufferView(
            name="normals",
            buffer=0,
            byteLength=len(normals_bytes),
            byteOffset=len(buffer_bytes),
            byteStride=12,
            target=pygltflib.ARRAY_BUFFER
        ))
        buffer_bytes += normals_bytes

        gltf.bufferViews.append(pygltflib.BufferView(
            name="uvs",
            buffer=0,
            byteLength=len(uvs_bytes),
            byteOffset=len(buffer_bytes),
            byteStride=8,
            target=pygltflib.ARRAY_BUFFER
        ))
        buffer_bytes += uvs_bytes

        if klfb != "":
            gltf.bufferViews.append(pygltflib.BufferView(
                name="joints",
                buffer=0,
                byteLength=len(joints_bytes),
                byteOffset=len(buffer_bytes),
                byteStride=8,
            ))
            buffer_bytes += joints_bytes

            gltf.bufferViews.append(pygltflib.BufferView(
                name="weights",
                buffer=0,
                byteLength=len(weights_bytes),
                byteOffset=len(buffer_bytes),
                byteStride=16,
                target=pygltflib.ARRAY_BUFFER
            ))
            buffer_bytes += weights_bytes
        
        gltf.bufferViews.append(pygltflib.BufferView(
            name="indices",
            buffer=0,
            byteLength=len(triangles_bytes),
            byteOffset=len(buffer_bytes),
            target=pygltflib.ELEMENT_ARRAY_BUFFER
        ))
        buffer_bytes += triangles_bytes
        if len(buffer_bytes) % 4 != 0: buffer_bytes += b"\0" * (4 - (len(buffer_bytes) % 4))

        if klfb != "":
            # Create inverse matrix for each joint
            inverse_matrix = []
            inverse_matrix.append([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0])
            for joint in klfb.global_joints:
                inverse_matrix.append([1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -joint.x, joint.y, joint.z, 1.0])
            inverse_matrix_array = np.array(inverse_matrix, dtype=np.float32)
            inverse_matrix_bytes = inverse_matrix_array.tobytes()
            gltf.accessors.append(pygltflib.Accessor(
                name="inverse_matrix",
                bufferView=len(gltf.bufferViews),
                byteOffset=0,
                componentType=pygltflib.FLOAT,
                count=len(inverse_matrix),
                type=pygltflib.MAT4,
                max=inverse_matrix_array.max(axis=0).tolist(),
                min=inverse_matrix_array.min(axis=0).tolist()
            ))
            gltf.bufferViews.append(pygltflib.BufferView(
                name="inverse_matrix",
                buffer=0,
                byteLength=len(inverse_matrix_bytes),
                byteOffset=len(buffer_bytes),
            ))
            buffer_bytes += inverse_matrix_bytes

            # Add rig/skin to glTF
            skin = pygltflib.Skin(
                joints=[len(gltf.nodes)],
                inverseBindMatrices=len(gltf.accessors) - 1,
                skeleton=len(gltf.nodes)
            )
            gltf.scenes[0].nodes.append(len(gltf.nodes))
            gltf.nodes.append(pygltflib.Node(name="root_joint", children=[]))
            joints_start = len(gltf.nodes) # Node index of joint0; subtract 1 to get root_joint
            for x, joint in enumerate(klfb.local_joints):
                gltf.nodes.append(pygltflib.Node(name=f"joint{x}", translation=[joint.x, -joint.y, -joint.z]))
                parent_joint = klfb.parent_joints[x]
                if parent_joint == 0xFFFF:
                    gltf.nodes[joints_start - 1].children.append(joints_start + x)
                else:
                    gltf.nodes[joints_start + parent_joint].children.append(joints_start + x)
                skin.joints.append(joints_start + x)
            gltf.skins.append(skin)

            # Parse animations
            if len(animations) > 0:
                translations_bytes = bytes()
                translations_keyframes_bytes = bytes()
                rotations_bytes = bytes()
                rotations_keyframes_bytes = bytes()
                morph_bytes = bytes()
                morph_keyframes_bytes = bytes()

                anim_list = [] # Keeps track of what animations have already been added based on animation names
                for animation in animations:
                    try:
                        try: klfa = Klfa.from_file(animation)
                        except: klfa = KlfaAlt.from_file(animation)
                        anim_name = klfa.name.replace("\u0000", "") # Removes empty unicode characters
                        if anim_name in anim_list: continue
                        else: anim_list.append(anim_name)
                        samplers = []
                        channels = []

                        root_keyframes_array = np.array([0.0], dtype=np.float32)
                        root_translations_array = np.array([[klfa.initial_pos.x, -klfa.initial_pos.y, -klfa.initial_pos.z]], dtype=np.float32)
                        root_keyframes_array_bytes = root_keyframes_array.tobytes()
                        root_translations_array_bytes = root_translations_array.tobytes()
                        gltf.accessors.append(
                            pygltflib.Accessor(
                                name=f"anim_{anim_name}_root_trans_keyframes",
                                bufferView=len(gltf.bufferViews),
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
                                name=f"anim_{anim_name}_root_trans",
                                bufferView=len(gltf.bufferViews) + 1,
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
                        
                        if isinstance(klfa, Klfa):
                            for i in range(klfa.joint_count):
                                translations_array = np.array([[translation.x * klfa.scale, -translation.y * klfa.scale, -translation.z * klfa.scale] for translation in klfa.joint_translations[i].coordinates], dtype=np.float32)
                                translations_keyframes_array = np.array([keyframe / fps for keyframe in klfa.joint_translations[i].keyframes], dtype=np.float32)
                                rotations_array = np.array([Rotation.from_euler("XYZ", [rotation.x / 0xFFFF * 360, -rotation.y / 0xFFFF * 360, -rotation.z / 0xFFFF * 360], degrees=True).as_quat() for rotation in klfa.joint_rotations[i].rotations], dtype=np.float32)
                                rotations_keyframes_array = np.array([keyframe / fps for keyframe in klfa.joint_rotations[i].keyframes], dtype=np.float32)

                                translations_array_bytes = translations_array.tobytes()
                                translations_keyframes_array_bytes = translations_keyframes_array.tobytes()
                                rotations_array_bytes = rotations_array.tobytes()
                                rotations_keyframes_array_bytes = rotations_keyframes_array.tobytes()

                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_trans_keyframes",
                                        bufferView=len(gltf.bufferViews),
                                        byteOffset=len(translations_keyframes_bytes),
                                        count=len(translations_keyframes_array),
                                        type=pygltflib.SCALAR,
                                        componentType=pygltflib.FLOAT,
                                        max=[translations_keyframes_array.max().tolist()],
                                        min=[translations_keyframes_array.min().tolist()],
                                    )
                                )
                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_trans",
                                        bufferView=len(gltf.bufferViews) + 1,
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

                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_rot_keyframes",
                                        bufferView=len(gltf.bufferViews) + 2,
                                        byteOffset=len(rotations_keyframes_bytes),
                                        count=len(rotations_keyframes_array),
                                        type=pygltflib.SCALAR,
                                        componentType=pygltflib.FLOAT,
                                        max=[rotations_keyframes_array.max().tolist()],
                                        min=[rotations_keyframes_array.min().tolist()],
                                    )
                                )
                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_rot",
                                        bufferView=len(gltf.bufferViews) + 3,
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

                            if klfa.morphs != None and len(morphs) > 0:
                                try:
                                    morph_weights_list = [[] for _ in range(klfa.morphs.morph_count)]
                                    morph_keyframes_list = [[] for _ in range(klfa.morphs.morph_count)]
                                    for keyframe, morph_keyframe in enumerate(klfa.morphs.morph_keyframes):
                                        for x in range(klfa.morphs.morph_count):
                                            try:
                                                keyframe_data = morph_keyframe.keyframe_data[x]
                                                morph_weights = [0.0] * len(gltf.meshes[morph_map[keyframe_data.morph0][0]].primitives[0].targets)
                                                morph_weights[morph_map[keyframe_data.morph1][1]] = keyframe_data.weight / 255
                                                morph_weights[morph_map[keyframe_data.morph0][1]] = (255 - keyframe_data.weight) / 255
                                                morph_weights_list[x].append(morph_weights)
                                                morph_keyframes_list[x].append(keyframe / fps)
                                            except:
                                                morph_weights = [0.0] * (len(morph_weights_list[x][-1]) if len(morph_weights_list[x]) > 0 else len(gltf.meshes[morph_map[list(morph_map)[0]][0]].primitives[0].targets))
                                                morph_weights_list[x].append(morph_weights)
                                                morph_keyframes_list[x].append(keyframe / fps)
                                    
                                    for x in range(klfa.morphs.morph_count):
                                        morph_part_weights_list = np.array(morph_weights_list[x], dtype=np.float32).flatten()
                                        morph_part_keyframes_list = np.array(morph_keyframes_list[x], dtype=np.float32)
                                        morph_part_weights_bytes = morph_part_weights_list.tobytes()
                                        morph_part_keyframes_bytes = morph_part_keyframes_list.tobytes()

                                        try:
                                            channels.append(
                                                pygltflib.AnimationChannel(
                                                    sampler=len(samplers),
                                                    target=pygltflib.AnimationChannelTarget(
                                                        node=morph_map[klfa.morphs.morph_keyframes[0].keyframe_data[x].morph0][0],
                                                        path=pygltflib.WEIGHTS
                                                    )
                                                )
                                            )
                                        except:
                                            if x > 0 and channels[-1].target == pygltflib.WEIGHTS: 
                                                continue
                                            else: 
                                                channels.append(
                                                    pygltflib.AnimationChannel(
                                                        sampler=len(samplers),
                                                        target=pygltflib.AnimationChannelTarget(
                                                            node=morph_map[list(morph_map)[0]][0],
                                                            path=pygltflib.WEIGHTS
                                                        )
                                                    )
                                                )

                                        gltf.accessors.append(
                                            pygltflib.Accessor(
                                                name=f"anim_{anim_name}_morph{i}_keyframes",
                                                bufferView=len(gltf.bufferViews) + 4,
                                                byteOffset=len(morph_keyframes_bytes),
                                                count=len(morph_part_keyframes_list),
                                                type=pygltflib.SCALAR,
                                                componentType=pygltflib.FLOAT,
                                                max=[morph_part_keyframes_list.max().tolist()],
                                                min=[morph_part_keyframes_list.min().tolist()],
                                            )
                                        )
                                        gltf.accessors.append(
                                            pygltflib.Accessor(
                                                name=f"anim_{anim_name}_morph{i}_weights",
                                                bufferView=len(gltf.bufferViews) + 5,
                                                byteOffset=len(morph_bytes),
                                                count=len(morph_part_weights_list),
                                                type=pygltflib.SCALAR,
                                                componentType=pygltflib.FLOAT,
                                                max=[morph_part_weights_list.max().tolist()],
                                                min=[morph_part_weights_list.min().tolist()],
                                            )
                                        )
                                        samplers.append(
                                            pygltflib.AnimationSampler(
                                                interpolation=pygltflib.ANIM_LINEAR,
                                                input=len(gltf.accessors) - 2,
                                                output=len(gltf.accessors) - 1
                                            )
                                        )

                                        morph_bytes += morph_part_weights_bytes
                                        morph_keyframes_bytes += morph_part_keyframes_bytes
                                except Exception as e:
                                    print(f"@@@ morph {animation}: {e}")
                        else:
                            for i in range(klfa.rotation_count):
                                rotations_array = []
                                rotations_keyframes_array = []
                                for x in range(klfa.keyframe_count):
                                    rotation = klfa.rotations[x].joint_rotations[i]
                                    rotations_array.append(Rotation.from_euler("XYZ", [rotation.x / 0xFFFF * 360, -rotation.y / 0xFFFF * 360, -rotation.z / 0xFFFF * 360], degrees=True).as_quat())
                                    rotations_keyframes_array.append(x / fps)
                                rotations_array = np.array(rotations_array, dtype=np.float32)
                                rotations_keyframes_array = np.array(rotations_keyframes_array, np.float32)
                                rotations_array_bytes = rotations_array.tobytes()
                                rotations_keyframes_array_bytes = rotations_keyframes_array.tobytes()
                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_rot_keyframes",
                                        bufferView=len(gltf.bufferViews) + 2,
                                        byteOffset=len(rotations_keyframes_bytes),
                                        count=len(rotations_keyframes_array),
                                        type=pygltflib.SCALAR,
                                        componentType=pygltflib.FLOAT,
                                        max=[rotations_keyframes_array.max().tolist()],
                                        min=[rotations_keyframes_array.min().tolist()],
                                    )
                                )
                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_rot",
                                        bufferView=len(gltf.bufferViews) + 3,
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
                            
                            target_bits = [int(digit) for digit in bin(klfa.joint_targets)[2:]][::-1]
                            target_joints = []
                            for i, x in enumerate(target_bits):
                                if x == 1: target_joints.append(i)

                            for i, target_joint in enumerate(target_joints):
                                translations_array = []
                                translations_keyframes_array = []
                                for x in range(klfa.keyframe_count):
                                    translation = klfa.translations[x].joint_translations[i]
                                    translations_array.append([translation.x * klfa.scale, -translation.y * klfa.scale, -translation.z * klfa.scale])
                                    translations_keyframes_array.append(x / fps)
                                translations_array = np.array(translations_array, dtype=np.float32)
                                translations_keyframes_array = np.array(translations_keyframes_array, np.float32)
                                translations_array_bytes = translations_array.tobytes()
                                translations_keyframes_array_bytes = translations_keyframes_array.tobytes()

                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_trans_keyframes",
                                        bufferView=len(gltf.bufferViews),
                                        byteOffset=len(translations_keyframes_bytes),
                                        count=len(translations_keyframes_array),
                                        type=pygltflib.SCALAR,
                                        componentType=pygltflib.FLOAT,
                                        max=[translations_keyframes_array.max().tolist()],
                                        min=[translations_keyframes_array.min().tolist()],
                                    )
                                )
                                gltf.accessors.append(
                                    pygltflib.Accessor(
                                        name=f"anim_{anim_name}_joint{i}_trans",
                                        bufferView=len(gltf.bufferViews) + 1,
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
                                            node=joints_start + target_joint,
                                            path=pygltflib.TRANSLATION
                                        )
                                    )
                                )

                                translations_bytes += translations_array_bytes
                                translations_keyframes_bytes += translations_keyframes_array_bytes
                        
                        if gltf.animations == None: gltf.animations = []
                        gltf.animations.append(
                            pygltflib.Animation(
                                name=f"{len(anim_list) - 1}_{anim_name}",
                                samplers=samplers,
                                channels=channels
                            )
                        )
                    except Exception as e:
                        print(f"@@@ anim {animation}: {e}")
                        pass
                
                if len(anim_list) > 0:
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
                            name="anim_translations",
                            buffer=0,
                            byteLength=len(translations_bytes),
                            byteOffset=len(buffer_bytes)
                        )
                    )
                    buffer_bytes += translations_bytes

                    gltf.bufferViews.append(
                        pygltflib.BufferView(
                            name="anim_rotations_keyframes",
                            buffer=0,
                            byteLength=len(rotations_keyframes_bytes),
                            byteOffset=len(buffer_bytes)
                        )
                    )
                    buffer_bytes += rotations_keyframes_bytes

                    gltf.bufferViews.append(
                        pygltflib.BufferView(
                            name="anim_rotations",
                            buffer=0,
                            byteLength=len(rotations_bytes),
                            byteOffset=len(buffer_bytes)
                        )
                    )
                    buffer_bytes += rotations_bytes

                    if len(morph_bytes) > 0:
                        gltf.bufferViews.append(
                            pygltflib.BufferView(
                                name="anim_morph_keyframes",
                                buffer=0,
                                byteLength=len(morph_keyframes_bytes),
                                byteOffset=len(buffer_bytes)
                            )
                        )
                        buffer_bytes += morph_keyframes_bytes

                        gltf.bufferViews.append(
                            pygltflib.BufferView(
                                name="anim_morph_weights",
                                buffer=0,
                                byteLength=len(morph_bytes),
                                byteOffset=len(buffer_bytes)
                            )
                        )
                        buffer_bytes += morph_bytes

        # Add textures to glTF
        if len(textures) > 0:
            # Use nearest texture filtering since that seems to work the best
            gltf.samplers.append(pygltflib.Sampler(
                magFilter=pygltflib.NEAREST,
                minFilter=pygltflib.NEAREST,
                wrapS=pygltflib.REPEAT,
                wrapT=pygltflib.REPEAT
            ))
            for x, texture in enumerate(textures):
                if embed_textures:
                    f = open(texture, "rb")
                    texture_bytes = f.read()
                    f.close()
                    gltf.images.append(pygltflib.Image(
                        name=os.path.basename(texture),
                        mimeType="image/png",
                        bufferView=len(gltf.bufferViews)
                    ))
                    gltf.bufferViews.append(
                        pygltflib.BufferView(
                            name=f"texture_{x}",
                            buffer=0,
                            byteLength=len(texture_bytes),
                            byteOffset=len(buffer_bytes)
                        )
                    )
                    buffer_bytes += texture_bytes
                else:
                    gltf.images.append(pygltflib.Image(
                        name=os.path.basename(texture),
                        uri=os.path.basename(texture)
                    ))
                
                gltf.materials.append(pygltflib.Material(
                    name=f"mtl{x}",
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
                ))
                gltf.textures.append(pygltflib.Texture(
                    name=os.path.basename(texture),
                    sampler=0,
                    source=x
                ))

        gltf.buffers.append(pygltflib.Buffer(
            byteLength=len(buffer_bytes),
            uri="data:application/gltf-buffer;base64," + base64.b64encode(buffer_bytes).decode("utf-8")
        ))
        gltf.save(output_file, asset=pygltflib.Asset(
            generator="klonoa2-tools (https://github.com/evilarceus/klonoa2-tools)",
            copyright="Models by Namco, extracted by t4ils"
        ))
        
