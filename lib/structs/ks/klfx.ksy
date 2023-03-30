meta:
  id: klfx
  endian: le
  bit-endian: le
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
      - id: scale
        type: f4
      - id: reserved
        contents: [0x00, 0x00, 0x00, 0x00]
  part:
    seq:
      - id: enable
        type: u2
        doc: |
          Decides whether or not to render this part.
          This value seems to only be used for Lolo's low-poly model.
      - id: some_number
        type: u2
      - id: tristrip_count
        type: u2
      - id: tristrip_group_count
        type: u2
      - id: uv_count
        type: u2
        doc: |
          There is one model in the game that has a UV count of 0. In this case,
          simply use the last UV from the previous part of the model.
      - id: subpart_count
        type: u2
        doc: |
          See note in the "subparts" instance.
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
      - id: tex0
        type: gsreg_tex0
    instances:
      subparts:
        pos: subparts_offset
        type: subpart(_index)
        repeat: expr
        repeat-expr: subpart_count
        doc: |
          All parts that have a joint influence have at least 1 subpart.
          Parts that need to have more than 4 joint influences will have more
          than 1 subpart.
          Some parts may not even have subparts/joint influences, hence why 
          there are instances for vertices and normals in the part type.
          
          The start of a subpart's vertices/normals must be 16-byte aligned.
          This is very important for parts with more than 1 subpart, since subparts
          do not define a vertices/normals offset for that specific subpart.
          See the "prev_(vertices/normals)" and "res_(vertices/normals)" instances
          in the subpart type to see how this is handled.
          (Kaitai is very finnicky when doing that type of stuff, but it works :P)
      uvs:
        pos: uvs_offset
        type: uv
        repeat: expr
        repeat-expr: uv_count
      vertices:
        pos: vertices_offset
        type: coordinate
        repeat: expr
        repeat-expr: subpart_count == 0 ? vertex_count : 0
      normals:
        pos: normals_offset
        type: coordinate
        repeat: expr
        repeat-expr: subpart_count == 0 ? normal_count : 0
      tristrip_groups:
        pos: indices_offset
        type: tristrip_group
        repeat: expr
        repeat-expr: tristrip_group_count
  subpart:
    params:
      - id: i
        type: u4
    seq:
      - id: joints
        type: joints
      - id: vertex_count
        type: u2
      - id: normal_count
        type: u2
      - id: some_numbers
        size: 4
      - id: reserved
        size: 4
      - id: weights_offset
        type: u4
      - id: some_other_numbers
        size: 8
    instances:
      vertices:
        pos: prev_vertices
        type: coordinate
        repeat: expr
        repeat-expr: vertex_count
        doc: |
          Vertices must be multiplied by the scale value in the header of the
          model.
      normals:
        pos: prev_normals
        type: coordinate
        repeat: expr
        repeat-expr: normal_count
        doc: |
          Normals must be divided by 0x1000 (4096).
      weights:
        pos: weights_offset
        type: weight
        repeat: expr
        repeat-expr: vertex_count
      prev_vertices:
        value: "i == 0 ? _parent.vertices_offset : (_parent.subparts[i - 1].res_vertices).as<u4>"
      res_vertices:
        value: "prev_vertices + _parent.subparts[i].vertex_count * 6 + ((_parent.subparts[i].vertex_count * 6) % 16 != 0 ? 16 - (_parent.subparts[i].vertex_count * 6) % 16 : 0)"
      prev_normals:
        value: "i == 0 ? _parent.normals_offset : (_parent.subparts[i - 1].res_normals).as<u4>"
      res_normals:
        value: "prev_normals + _parent.subparts[i].normal_count * 6 + ((_parent.subparts[i].normal_count * 6) % 16 != 0 ? 16 - (_parent.subparts[i].normal_count * 6) % 16 : 0)"
  coordinate:
    doc: |
      The coordinates are Y-UP, but remember: Y and Z are inverted!
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
  uv:
    doc: |
      The origin point for UVs is at the top left of the image.
    
      Currently, it is recommended to make a 1024x1024 image for the texture 
      (even if the texture is not actually that big, but it's just to ensure
      everything fits in) and divide the UVs by 16384.
    seq:
      - id: u
        type: u4
      - id: v
        type: u4
  joints:
    doc: |
      Joint influences that have a value of 0xFFFF (65535) are essentially "N/A".
    seq:
      - id: a
        type: u2
      - id: b
        type: u2
      - id: c
        type: u2
      - id: d
        type: u2
  weight:
    doc: |
      Since these vertex weights do not always add up to 255 (0xFF), it is 
      recommended to divide the weights by the sum of all the weights.
    seq:
      - id: a
        type: u1
      - id: b
        type: u1
      - id: c
        type: u1
      - id: d
        type: u1
  tristrip_group:
    seq:
      - id: tristrips
        type: tristrip
        repeat: until
        repeat-until: _.indices[_.start.flag - 2].flag == -1
  tristrip:
    seq:
      - id: start
        type: index
      - id: indices
        type: index
        repeat: expr
        repeat-expr: start.flag - 1
  index:
    seq:
      - id: vertex
        type: u2
      - id: uv
        type: u2
      - id: normal
        type: u2
      - id: flag
        type: s2
  gsreg_tex0:
    seq:
      - id: tbp0
        type: b14
      - id: tbw
        type: b6
      - id: psm
        type: b6
        enum: gs_psm
      - id: tw
        type: b4
      - id: th
        type: b4
      - id: tcc
        type: b1
      - id: tfx
        type: b2
      - id: cbp
        type: b14
      - id: cpsm
        type: b4
        enum: gs_psm
      - id: csm
        type: b1
      - id: csa
        type: b5
      - id: cld
        type: b3
enums:
  gs_psm:
    0x00: psmct32
    0x01: psmct24
    0x02: psmct16
    0x0A: psmct16s
    0x13: psmt8
    0x14: psmt4
    0x1B: psmt8h
    0x24: psmt4hl
    0x2C: psmt4hh
    0x30: psmz32
    0x31: psmz24
    0x32: psmz16
    0x3A: psmz16s