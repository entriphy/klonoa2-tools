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
        if: archive_count != 5
        pos: start_offset + 4
        type: archive
        repeat: expr
        repeat-expr: archive_count
      pal_archives:
        if: archive_count == 5
        pos: start_offset
        type: pal_archive
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
  pal_archive_list:
    params:
      - id: start_offset
        type: u4
      - id: i
        type: u4
    instances:
      kldata:
        pos: start_offset + _parent.archive_offsets[i]
        type: pointers(start_offset + _parent.archive_offsets[i])
  pal_archive:
    seq:
      - id: pal_kldata_count
        type: u4
      - id: archive_offsets
        type: u4
        repeat: expr
        repeat-expr: pal_kldata_count
    instances:
      kldata_list:
        type: pal_archive_list(_parent.start_offset, _index)
        repeat: expr
        repeat-expr: pal_kldata_count