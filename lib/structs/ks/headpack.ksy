meta:
  id: headpack
  endian: le
seq:
  - id: bin_count
    type: u4
  - id: kldata_offset
    type: u4
  - id: bgmpack_offset
    type: u4
  - id: pptpack_offset
    type: u4
  - id: headpack_size
    type: u4
instances:
  kldata:
    pos: kldata_offset
    type: pointers(kldata_offset)
  bgmpack:
    pos: bgmpack_offset
    type: pointers(bgmpack_offset)
  pptpack:
    pos: pptpack_offset
    type: pointers(pptpack_offset)
types:
  pointers:
    params:
      - id: start_offset
        type: u4
    seq:
      - id: archive_count
        type: u4
    instances:
      archives:
        pos: start_offset + 4
        type: archive
        repeat: expr
        repeat-expr: archive_count
  archive:
    seq:
      - id: sector_offset
        type: u4
      - id: sectors
        type: u4
    instances:
      offset:
        value: sector_offset * 2048
      size:
        value: sectors * 2048