meta:
  id: klfa
  endian: le
seq:
  - id: joint_count
    type: u2
  - id: keyframe_count
    type: u2
  - id: more_joint_counts
    size: 4
  - id: name
    type: str
    terminator: 0
    size: 8
    encoding: ASCII
  - id: st
    size: 4
  - id: morphs_offset
    type: u4
  - id: data_offset
    type: u4
  - id: more_stuff
    size: 6 + (data_offset) - 32 + 6
  - id: initial_pos
    type: float_coordinate
  - id: scale
    type: f4
  - id: joint_translations
    type: joint_translation
    repeat: expr
    repeat-expr: joint_count
  - id: joint_rotations
    type: joint_rotation
    repeat: expr
    repeat-expr: joint_count
instances:
  morphs:
    if: morphs_offset != 0
    pos: morphs_offset
    type: morph_data
types:
  morph_data:
    seq:
      - id: morph_count
        type: u1
      - id: morph_keyframes
        type: morph_keyframe
        repeat: expr
        repeat-expr: _parent.keyframe_count
  morph_keyframe:
    seq:
      - id: keyframe_data
        type: morph_keyframe_data
        repeat: expr
        repeat-expr: _parent.morph_count
  morph_keyframe_data:
    seq:
      - id: morph0
        type: u1
      - id: morph1
        type: u1
      - id: weight
        type: u1
  float_coordinate:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
  coordinate:
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
  rotation:
    seq:
      - id: x
        type: u2
      - id: y
        type: u2
      - id: z
        type: u2
  joint_translation:
    seq:
      - id: keyframe_count
        type: u4
      - id: keyframes
        type: u2
        repeat: expr
        repeat-expr: keyframe_count
      - id: coordinates
        type: coordinate
        repeat: expr
        repeat-expr: keyframe_count
  joint_rotation:
    seq:
      - id: keyframe_count
        type: u4
      - id: keyframes
        type: u2
        repeat: expr
        repeat-expr: keyframe_count
      - id: rotations
        type: rotation
        repeat: expr
        repeat-expr: keyframe_count