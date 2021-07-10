meta:
  id: klfa_alt
  endian: le
seq:
  - id: joint_count
    type: u2
  - id: keyframe_count
    type: u2
  - id: rotation_count
    type: u2
  - id: translation_count
    type: u2
  - id: name
    type: str
    terminator: 0
    size: 8
    encoding: ASCII
  - id: stuff
    size: 0x10
  - id: joint_targets
    type: u8
  - id: more_stuff
    size: 0x08
  - id: initial_pos
    type: float_coordinate
  - id: scale
    type: f4
  - id: rotation_offset
    type: u4
  - id: translation_offset
    type: u4
  - id: reserved
    size: 4
  - id: transition_in
    type: u2
  - id: transition_out
    type: u2
  - id: this_stuff_doesnt_get_read_by_the_game_lol
    size: 0x0C
instances:
  rotations:
    pos: rotation_offset
    type: frame_rotation
    repeat: expr
    repeat-expr: keyframe_count
  translations:
    pos: translation_offset
    type: frame_translation
    repeat: expr
    repeat-expr: keyframe_count
types:
  frame_rotation:
    seq:
      - id: joint_rotations
        type: rotation
        repeat: expr
        repeat-expr: _parent.rotation_count
  frame_translation:
    seq:
      - id: joint_translations
        type: coordinate
        repeat: expr
        repeat-expr: _parent.translation_count
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
        type: u2
      - id: keyframes
        type: u2
        repeat: expr
        repeat-expr: keyframe_count
      - id: keyframe_total
        type: u2
      - id: coordinates
        type: coordinate
        repeat: expr
        repeat-expr: keyframe_count
  joint_rotation:
    seq:
      - id: keyframe_count
        type: u2
      - id: keyframes
        type: u2
        repeat: expr
        repeat-expr: keyframe_count
      - id: keyframe_total
        type: u2
      - id: rotations
        type: rotation
        repeat: expr
        repeat-expr: keyframe_count