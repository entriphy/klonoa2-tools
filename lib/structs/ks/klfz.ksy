meta:
  id: klfz
  endian: le
  imports:
    - klfx
params:
  - id: input_klfx
    type: klfx
    doc: |
      Like subparts in klfx, morph vertices/normals are split into
      subparts and are 16-byte aligned. The only problem is that subparts
      are not defined in this file, which is why the klfx file that corresponds
      to this file is required.
      
      Other than that, this is pretty much the same as how vertices and normals
      are defined in a klfx file. When the morph is used, the klfx part's (defined in 
      part_number) vertices and normals are set to the ones defined in this
      file.
seq:
  - id: header
    type: header
  - id: parts
    type: part(input_klfx)
    repeat: expr
    repeat-expr: header.part_count
types:
  header:
    seq:
      - id: magic
        contents: FZ
      - id: part_count
        type: u2
      - id: magic2
        contents: [0x80, 0x00, 0x40, 0x00]
      - id: scale
        type: f4
      - id: reserved
        contents: [0x00, 0x00, 0x00, 0x00]
  part:
    params:
      - id: klfxx
        type: klfx
    seq:
      - id: part_number
        type: u2
      - id: data_size
        type: u2
      - id: vertex_count
        type: u2
      - id: normal_count
        type: u2
      - id: vertices_offset
        type: u4
      - id: normals_offset
        type: u4
      - id: reserved
        size: 16
    instances:
      subparts:
        type: subpart(_index, klfxx)
        repeat: expr
        repeat-expr: klfxx.parts[part_number].subpart_count
  subpart:
    params:
      - id: i
        type: u2
      - id: klfxx
        type: klfx
    instances:
      vertices:
        pos: prev_vertices
        type: coordinate
        repeat: expr
        repeat-expr: klfxx.parts[_parent.part_number].subparts[i].vertex_count
      normals:
        pos: prev_normals
        type: coordinate
        repeat: expr
        repeat-expr: klfxx.parts[_parent.part_number].subparts[i].normal_count
      prev_vertices:
        value: "i == 0 ? _parent.vertices_offset : (_parent.subparts[i - 1].res_vertices).as<u4>"
      res_vertices:
        value: "prev_vertices + klfxx.parts[_parent.part_number].subparts[i].vertex_count * 6 + ((klfxx.parts[_parent.part_number].subparts[i].vertex_count * 6) % 16 != 0 ? 16 - (klfxx.parts[_parent.part_number].subparts[i].vertex_count * 6) % 16 : 0)"
      prev_normals:
        value: "i == 0 ? _parent.normals_offset : (_parent.subparts[i - 1].res_normals).as<u4>"
      res_normals:
        value: "prev_normals + klfxx.parts[_parent.part_number].subparts[i].normal_count * 6 + ((klfxx.parts[_parent.part_number].subparts[i].normal_count * 6) % 16 != 0 ? 16 - (klfxx.parts[_parent.part_number].subparts[i].normal_count * 6) % 16 : 0)"
  coordinate:
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2