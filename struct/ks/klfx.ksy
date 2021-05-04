meta:
  id: klfx
  endian: le
seq:
  - id: header
    type: header
  - id: parts
    type: part
    repeat: expr
    repeat-expr: header.part_count
types:
  header:
    seq:
      - id: magic
        contents: FX
      - id: part_count
        type: u2
      - id: magic2
        contents: [0x80, 0x00, 0x40, 0x00]
      - id: unknown_bytes
        size: 4
      - id: reserved
        size: 4
  part:
    seq:
      - id: part_thing
        size: 2
      - id: some_number
        type: u2
      - id: triangle_strip_count
        type: u2
      - id: indices_part_count
        type: u2
      - id: uv_count
        type: u2
      - id: subpart_count
        type: u2
      - id: vertex_count
        type: u2
      - id: normal_count
        type: u2
      - id: indices_offset
        type: u4
      - id: uvs_offset
        type: u4
      - id: vertices_offset
        type: u4
      - id: normals_offset
        type: u4
      - id: subparts_offset
        type: u4
      - id: reserved
        type: u4
      - id: uv_thing
        size: 6
      - id: part_end
        size: 2
    instances:
      subparts:
        pos: subparts_offset
        type: subpart(_index)
        repeat: expr
        repeat-expr: subpart_count
      uvs:
        pos: uvs_offset
        type: uv
        repeat: expr
        repeat-expr: uv_count
  subpart:
    params:
      - id: i
        type: u4
    seq:
      - id: ids
        size: 8
      - id: vertex_count
        type: u2
      - id: normal_count
        type: u2
      - id: some_numbers
        size: 4
      - id: some_other_numbers
        size: 16
    instances:
      vertices:
        pos: "i > 0 ? _parent.vertices_offset + _parent.subparts[i - 1].vertex_count * 6 + 16 - (_parent.subparts[i - 1].vertex_count * 6) % 16 : _parent.vertices_offset"
        type: coordinate
        repeat: expr
        repeat-expr: vertex_count
      normals:
        pos: "i > 0 ? _parent.normals_offset + _parent.subparts[i - 1].normal_count * 6 + 16 - (_parent.subparts[i - 1].normal_count * 6) % 16 : _parent.normals_offset"
        type: coordinate
        repeat: expr
        repeat-expr: vertex_count
  coordinate:
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
  uv:
    seq:
      - id: u
        type: u4
      - id: v
        type: u4