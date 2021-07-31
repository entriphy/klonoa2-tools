meta:
  id: klfa_alt
  endian: le
doc: |
  This format is slightly different than the normal klfa format.
  Rather than using keyframe values, translations and rotations are
  defined for each frame.
  
  Translations are only defined for certain joints. See the "targets" property
  for more info.
  
  - animation
    - rotations
      - frame0
        - joint0
        - joint1
        - joint2
        - ...
      - frame1
        - joint0
        - joint1
        - joint2
        - ...
      - ...
    - translations
      - frame0
        - joint0
        - joint1
        - joint2
        - ...
      - frame1
        - joint0
        - ...
      - ...
    
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
    doc: |
      This is a bit mask that defines which joints are affected by translations.
      Ex. if bit 0 and 3 are 1, then the animation will have translation keyframes
      for joint0 and joint3 (and in this scenario, translation_count should
      equal 2). All the other joints simply do not have translations.
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
    doc: |
      Not sure if transition_out gets read by the game, but I'm just assuming
      what it is based on the fact that it's after transition_in.
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
    doc: |
      The coordinates are Y-UP, but remember: Y and Z are inverted!
    seq:
      - id: x
        type: s2
      - id: y
        type: s2
      - id: z
        type: s2
  rotation:
    doc: |
      To get an euler angle, divide an axis by 0xFFFF (65535) and multiply it
      by 365.
      Y and Z are also inverted for this.
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