from ..structs.klfx_struct import Klfx
from .read_bytes import u16le
import numpy as np

def __check_winding_correct(vertex_indices, normal_indices, vertices, normals): # TODO: Klonoa's eyelids' faces are messed up because of this function
    A = vertices[vertex_indices[0]]
    B = vertices[vertex_indices[1]]
    C = vertices[vertex_indices[2]]
    An = normals[normal_indices[0]]
    Bn = normals[normal_indices[1]]
    Cn = normals[normal_indices[2]]
    normal = ((An[0] + Bn[0] + Cn[0]) / 3, (An[1] + Bn[1] + Cn[1]) / 3, (An[2] + Bn[2] + Cn[2]) / 3)
    BA = np.subtract(B, A)
    CA = np.subtract(C, A)
    cross = np.cross(BA, CA)
    dot = np.dot(normal, cross)
    return (dot >= 0)

def parse_faces(buf, part: Klfx.Part, vertices, normals):
        faces = []
        indices, tstrips = [], []
        current_part = 0
        current_offset = part.indices_offset
        while current_part < part.indices_part_count:
            normal_index = u16le(buf, current_offset)
            uv_index = u16le(buf, current_offset + 0x02)
            face_index = u16le(buf, current_offset + 0x04)
            indices.append((normal_index, uv_index, face_index))

            if u16le(buf, current_offset + 0x06) != 0:
                if u16le(buf, current_offset + 0x06) == -1:
                    current_part += 1
                else:
                    tstrips.append(u16le(buf, current_offset + 0x06))

            current_offset += 0x08
        
        for i, tstrip in enumerate(tstrips):
            face_tstrips = tstrips[0:i + 1]
            start_idx = sum(face_tstrips) + 1 - tstrip
            face_indices = indices[start_idx - 1:start_idx - 1 + tstrip]
            for x in range(len(face_indices) - 2):
                vertex_indices = [face_indices[x][2], face_indices[x + 1][2], face_indices[x + 2][2]]
                normal_indices = [face_indices[x][0], face_indices[x + 1][0], face_indices[x + 2][0]]
                winding = __check_winding_correct(vertex_indices, normal_indices, vertices, normals)
                faces.append((
                    (face_indices[x][2], face_indices[x][1], face_indices[x][0]),
                    (face_indices[x + 1][2], face_indices[x + 1][1], face_indices[x + 1][0]),
                    (face_indices[x + 2][2], face_indices[x + 2][1], face_indices[x + 2][0]),
                ) if winding else (
                    (face_indices[x][2], face_indices[x][1], face_indices[x][0]),
                    (face_indices[x + 2][2], face_indices[x + 2][1], face_indices[x + 2][0]),
                    (face_indices[x + 1][2], face_indices[x + 1][1], face_indices[x + 1][0])
                ))

        return faces