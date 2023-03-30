meta:
  id: gms
  file-extension: gms
  endian: le
  bit-endian: le
seq:
  - id: dmatag
    type: chain_dmatag
  - id: dmatag2
    type: chain_dmatag
    if: dmatag.addr == 0x10 and dmatag.qwc == 1
  - id: vifcode_nop
    type: vifcode
  - id: vifcode_directhl
    type: vifcode
  - id: packets
    type: packet
    repeat: until
    repeat-until: _.tag.eop == true
  - id: texflush
    type: gsreg_texflush
  - id: ret_tag
    type: chain_dmatag
types:
  packet:
    seq:
      - id: tag
        type: giftag
      - id: data
        type: packet_data
        if: tag.eop == false
    instances:
      texture:
        io: data.data._io
        type:
          switch-on: data.bitbltbuf.dpsm
          cases:
            gs_psm::psmt8: u1
            gs_psm::psmt4: b4
        repeat: expr
        repeat-expr: data.giftag_image.nloop * (data.bitbltbuf.dpsm == gs_psm::psmt4 ? 32 : 16)
        if: not tag.eop and data.bitbltbuf.dpsm != gs_psm::psmct32
      palette:
        io: data.data._io
        type: rgba32
        repeat: expr
        repeat-expr: data.giftag_image.nloop * 4
        if: is_palette
      is_palette:
        value: not tag.eop and data.bitbltbuf.dpsm == gs_psm::psmct32
  packet_data:
    seq:
      - id: bitbltbuf
        type: gsreg_bitbltbuf
      - id: trxpos
        type: gsreg_trxpos
      - id: trxreg
        type: gsreg_trxreg
      - id: trxdir
        type: gsreg_trxdir
      - id: giftag_image
        type: giftag
      - id: data
        type: lol
        size: giftag_image.nloop * 16
  lol:
    seq:
      - id: thing
        size: 0
  rgba32:
    seq:
      - id: r
        type: u1
      - id: g
        type: u1
      - id: b
        type: u1
      - id: a
        type: u1
  chain_dmatag:
    seq:
      - id: qwc
        type: b16
      - id: pad
        type: b10
      - id: pce
        type: b2
      - id: id
        type: b3
        enum: dmatag_tag
      - id: irq
        type: b1
      - id: addr
        type: b31
      - id: spr
        type: b1
  vifcode:
    seq:
      - id: immediate
        type: b16
      - id: num
        type: b8
      - id: cmd
        type: b7
        enum: vifcode_command
      - id: stall
        type: b1
  giftag:
    seq:
      - id: nloop
        type: b15
      - id: eop
        type: b1
      - id: pad
        type: b30
      - id: pre
        type: b1
      - id: pad2
        type: b11
      - id: flg
        type: b2
      - id: nreg
        type: b4
      - id: regs
        type: b4
        enum: giftag_regs
        repeat: expr
        repeat-expr: nreg
      - id: regs_pad
        size: 8 - (nreg + 1) / 2
  gsreg_bitbltbuf:
    seq:
      - id: sbp
        type: b14
      - id: pad0
        type: b2
      - id: sbw
        type: b6
      - id: pad1
        type: b2
      - id: spsm
        type: b6
        enum: gs_psm
      - id: pad2
        type: b2
      - id: dbp
        type: b14
      - id: dbw
        type: b6
      - id: pad4
        type: b2
      - id: pad3
        type: b2
      - id: dpsm
        type: b6
        enum: gs_psm
      - id: pad5
        type: b2
      - id: id
        type: u8
  gsreg_trxpos:
    seq:
      - id: ssax
        type: b11
      - id: pad0
        type: b5
      - id: ssay
        type: b11
      - id: pad1
        type: b5
      - id: dsax
        type: b11
      - id: pad2
        type: b5
      - id: dsay
        type: b11
      - id: dir
        type: b2
      - id: pad4
        type: b3
      - id: id
        type: u8
  gsreg_trxreg:
    seq:
      - id: rrw
        type: b12
      - id: pad0
        type: b20
      - id: rrh
        type: b12
      - id: pad1
        type: b20
      - id: id
        type: u8
  gsreg_trxdir:
    seq:
      - id: xdir
        type: b11
      - id: pad0
        type: b32
      - id: pad1
        type: b21
      - id: id
        type: u8
  gsreg_texflush:
    seq:
      - id: pad0
        type: b32
      - id: pad1
        type: b32
      - id: id
        type: u8
enums:
  dmatag_tag:
    0: refe_cnts
    1: cnt
    2: next
    3: ref
    4: refs
    5: call
    6: ret
    7: end
  vifcode_command:
    0: nop
    0x51: directhl
  giftag_regs:
    0: prim
    1: rgbaq
    2: st
    3: uv
    4: xyzf2
    5: xyz2
    6: tex0_1
    7: tex0_2
    8: clamp_1
    9: clamp_2
    10: fog
    11: reserved
    12: xyzf3
    13: xyz3
    14: ad
    15: nop
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