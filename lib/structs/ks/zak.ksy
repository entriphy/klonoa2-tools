meta:
  id: zak
  file-extension: zak
  endian: le
seq:
  - id: size
    type: u2
  - id: sizes
    type: u2
    repeat: expr
    repeat-expr: size
  - id: idk
    type: u2
    repeat: expr
    repeat-expr: 4
instances:
  buffer:
    pos: 0x70
    type: enemy_data(sizes)
types:
  fvector:
    seq:
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: w
        type: f4
  enemy_data:
    params:
      - id: sizes
        type: u2[]
    seq:
      - id: walk00
        type: walk00
        repeat: expr
        repeat-expr: sizes[0] / sizeof<walk00>
      - id: walk10
        type: walk10
        repeat: expr
        repeat-expr: sizes[1] / sizeof<walk10>
      - id: fly00
        type: fly00
        repeat: expr
        repeat-expr: sizes[2] / sizeof<fly00>
      - id: fly01
        type: fly01
        repeat: expr
        repeat-expr: sizes[3] / sizeof<fly01>
      - id: jalc00
        type: jalc00
        repeat: expr
        repeat-expr: sizes[4] / sizeof<jalc00>
      - id: falc00
        type: falc00
        repeat: expr
        repeat-expr: sizes[5] / sizeof<falc00>
      - id: walc00
        type: walc00
        repeat: expr
        repeat-expr: sizes[6] / sizeof<walc00>
      - id: walk11
        type: walk11
        repeat: expr
        repeat-expr: sizes[7] / sizeof<walk11>
      - id: fly11
        type: fly11
        repeat: expr
        repeat-expr: sizes[8] / sizeof<fly11>
      - id: hero_root_hani
        type: hero_root_hani
        repeat: expr
        repeat-expr: sizes[9] / sizeof<hero_root_hani>
      - id: shutugen
        type: shutugen
        repeat: expr
        repeat-expr: sizes[10] / sizeof<shutugen>
      - id: bake_para
        type: bake_para
        repeat: expr
        repeat-expr: sizes[11] / sizeof<bake_para>
      - id: walk34
        type: walk34
        repeat: expr
        repeat-expr: sizes[12] / sizeof<walk34>
      - id: shutugen2
        type: shutugen2
        repeat: expr
        repeat-expr: sizes[13] / sizeof<shutugen2>
      - id: jump00
        type: jump00
        repeat: expr
        repeat-expr: sizes[14] / sizeof<jump00>
      - id: gum00
        type: gum00
        repeat: expr
        repeat-expr: sizes[15] / sizeof<gum00>
      - id: wnd00
        type: wnd00
        repeat: expr
        repeat-expr: sizes[16] / sizeof<wnd00>
      - id: wnd10
        type: wnd10
        repeat: expr
        repeat-expr: sizes[17] / sizeof<wnd10>
      - id: gun00
        type: gun00
        repeat: expr
        repeat-expr: sizes[18] / sizeof<gun00>
      - id: grnd00
        type: grnd00
        repeat: expr
        repeat-expr: sizes[19] / sizeof<grnd00>
      - id: cam00
        type: cam00
        repeat: expr
        repeat-expr: sizes[20] / sizeof<cam00>
      - id: cam01
        type: cam01
        repeat: expr
        repeat-expr: sizes[21] / sizeof<cam01>
      - id: cam02
        type: cam02
        repeat: expr
        repeat-expr: sizes[22] / sizeof<cam02>
      - id: snd00
        type: snd00
        repeat: expr
        repeat-expr: sizes[23] / sizeof<snd00>
      - id: walk02
        type: walk02
        repeat: expr
        repeat-expr: sizes[24] / sizeof<walk02>
      - id: walk03
        type: walk03
        repeat: expr
        repeat-expr: sizes[25] / sizeof<walk03>
      - id: walk01
        type: walk01
        repeat: expr
        repeat-expr: sizes[26] / sizeof<walk01>
      - id: fire00
        type: fire00
        repeat: expr
        repeat-expr: sizes[27] / sizeof<fire00>
      - id: fire10
        type: fire10
        repeat: expr
        repeat-expr: sizes[28] / sizeof<fire10>
      - id: sub00
        type: sub00
        repeat: expr
        repeat-expr: sizes[29] / sizeof<sub00>
      - id: swit00
        type: swit00
        repeat: expr
        repeat-expr: sizes[30] / sizeof<swit00>
      - id: swit01
        type: swit01
        repeat: expr
        repeat-expr: sizes[31] / sizeof<swit01>
  walk_common:
    seq:
      - id: walkspd
        type: s4
      - id: jumphigh
        type: s2
      - id: jumptime
        type: s2
      - id: mizo
        type: s2
      - id: target0
        type: s2
      - id: target1
        type: s2
      - id: tachido
        type: s2
  fly_common:
    seq:
      - id: posi
        type: fvector
      - id: time
        type: s4
      - id: wait
        type: s4
      - id: type
        type: s4
      - id: ofsmove
        type: s2
      - id: pad
        type: s2
      - id: lno0
        type: s8
      - id: lno1
        type: s8
  fly_rcommon:
    seq:
      - id: rno
        type: s4
      - id: ofs
        type: s4
      - id: mcn
        type: s4
      - id: dummy
        type: s4
      - id: time
        type: s4
      - id: wait
        type: s4
      - id: type
        type: s4
      - id: ofsmove
        type: s2
      - id: pad
        type: s2
      - id: lno0
        type: s8
      - id: lno1
        type: s8
  zako_born:
    seq:
      - id: dis
        type: s2
      - id: ydis
        type: s2
      - id: bake
        type: s1
      - id: nbake
        type: s1
      - id: look
        type: s1
      - id: hoko
        type: s1
      - id: turnint
        type: s2
      - id: herootno
        type: s2
      - id: heroot
        type: s4
  zako_movetbl:
    seq:
      - id: zgene
        type: zako_born
  zako_walk_common:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: walkpara
        type: walk_common
  zako_fly_common:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: flypara
        type: fly_common
  zako_fly_rcommon:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: flypara
        type: fly_rcommon
  fire_common:
    seq:
      - id: tbl2
        type: s2
      - id: ntbl2
        type: s2
      - id: mcn_w
        type: s4
      - id: m_cnt
        type: s2
      - id: trno
        type: s2
      - id: tmcn
        type: s4
      - id: fwait
        type: s2
      - id: inter
        type: s2
      - id: yv0
        type: s4
      - id: rnd_w
        type: s4
      - id: pad0
        type: s2
      - id: lno0
        type: s1
      - id: lno1
        type: s1
  fire_common2:
    seq:
      - id: tbl2
        type: s2
      - id: ntbl2
        type: s2
      - id: m_cnt
        type: s2
      - id: trno
        type: s2
      - id: tmcn
        type: s4
      - id: time
        type: s2
      - id: inter
        type: s2
      - id: g
        type: f4
      - id: x
        type: f4
      - id: y
        type: f4
      - id: z
        type: f4
      - id: rndw
        type: s4
      - id: rndh
        type: s4
      - id: pad0
        type: s2
      - id: live
        type: s2
      - id: lno0
        type: s1
      - id: lno1
        type: s1
  walk00:
    seq:
      - id: walk
        type: zako_walk_common
  walk10:
    seq:
      - id: walk
        type: zako_walk_common
      - id: lim0
        type: s4
      - id: lim1
        type: s4
      - id: spd0
        type: s4
      - id: spd1
        type: s4
  fly00:
    seq:
      - id: fly
        type: zako_fly_common
  fly01:
    seq:
      - id: fly
        type: zako_fly_rcommon
  jalc00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: pad0
        type: s2
      - id: pad1
        type: s2
      - id: juryoku
        type: f4
      - id: time
        type: s2
      - id: wait
        type: s2
      - id: res0
        type: s2
      - id: width
        type: s2
      - id: posi
        type: fvector
      - id: lno0
        type: s8
      - id: lno1
        type: s8
  falc00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: pad2
        type: s2
      - id: pad3
        type: s2
      - id: time
        type: s2
      - id: wait
        type: s2
      - id: width
        type: s2
      - id: height
        type: s2
      - id: pad0
        type: s2
      - id: pad1
        type: s2
      - id: ypos1
        type: f4
      - id: juryoku
        type: s4
      - id: pad5
        type: s4
      - id: pad6
        type: s4
      - id: posi
        type: fvector
      - id: lno0
        type: s8
      - id: lno1
        type: s8
  walc00:
    seq:
      - id: walk
        type: zako_walk_common
      - id: myrootno
        type: s2
      - id: bakerootno
        type: s2
      - id: myroot
        type: s4
      - id: bakeroot
        type: s4
      - id: test
        type: s2
      - id: testang
        type: s2
  walk11:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: walkspd
        type: s8
      - id: jumphigh
        type: s2
      - id: jumptime
        type: s2
      - id: kabe1
        type: s1
      - id: kabe2
        type: s1
      - id: mizo1
        type: s1
      - id: mizo2
        type: s1
      - id: turnint
        type: s2
      - id: tachido
        type: s2
      - id: hoko
        type: s2
      - id: tbl3
        type: s2
  fly11:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: posi
        type: fvector
      - id: time
        type: s8
      - id: dummy
        type: s8
  hero_root_hani:
    seq:
      - id: root1
        type: s4
      - id: root2
        type: s4
      - id: rootno0
        type: s2
      - id: dummy
        type: s2
      - id: pad2
        type: s4
  shutugen:
    seq:
      - id: heroot
        type: u2
      - id: stat
        type: u2
      - id: myroot
        type: s4
      - id: dis
        type: s2
      - id: ydis
        type: s2
      - id: option
        type: s2
      - id: index
        type: s2
      - id: posi
        type: fvector
      - id: tekipic
        type: s2
      - id: myrootno
        type: s2
      - id: stage
        type: s2
      - id: res0
        type: s2
      - id: res1
        type: s2
      - id: rev
        type: s2
      - id: mode
        type: s2
      - id: reflag
        type: s2
  bake_para:
    seq:
      - id: ba_stat
        type: s2
      - id: ba_option
        type: s2
      - id: ba_def
        type: s2
      - id: ba_herootno
        type: s2
      - id: ba_myrootno
        type: s2
      - id: ba_gimmno
        type: s2
      - id: ba_heroot
        type: s4
      - id: ba_myroot
        type: s4
      - id: pad1
        type: s4
      - id: pad2
        type: s4
      - id: pad3
        type: s4
  walk34:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: tbl
        type: s2
      - id: ntbl
        type: s2
      - id: nage
        type: s2
      - id: wait
        type: s2
      - id: time
        type: s2
      - id: res0
        type: s2
      - id: tbl2
        type: s2
      - id: ntbl2
        type: s2
      - id: res1
        type: s4
      - id: dummy
        type: s4
  shutugen2:
    seq:
      - id: stat
        type: s2
      - id: option
        type: s2
      - id: index
        type: s2
      - id: tekipic
        type: s2
      - id: dummy
        type: s2
      - id: res0
        type: s2
      - id: res1
        type: s2
      - id: pad2
        type: s2
  jump00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: type
        type: s2
      - id: rad
        type: s2
      - id: spd
        type: f4
      - id: pad
        type: s8
  gum00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: mcn1
        type: s4
      - id: ypos1
        type: f4
      - id: wait
        type: s4
      - id: move
        type: s4
      - id: tofs
        type: s4
      - id: stop
        type: s4
      - id: time
        type: s4
      - id: type
        type: s4
      - id: mcn0
        type: s4
      - id: ypos0
        type: f4
      - id: wspd
        type: s4
      - id: dcnt
        type: s4
  wnd00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: posi
        type: fvector
      - id: type
        type: s4
      - id: time
        type: s4
      - id: dummy
        type: s8
  wnd10:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: height
        type: f4
      - id: tg0
        type: s4
      - id: tg1
        type: s4
      - id: pad0
        type: s4
  gun00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: posi
        type: fvector
      - id: type
        type: s2
      - id: rootno
        type: s2
      - id: root
        type: s4
      - id: spd
        type: f4
      - id: time
        type: s2
      - id: pad2
        type: s2
      - id: lno0
        type: s8
      - id: lno1
        type: s8
  grnd00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: pad0
        type: s2
      - id: pad1
        type: s2
      - id: tbl2
        type: s2
      - id: ntbl2
        type: s2
      - id: pad2
        type: s8
  cam00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: posi
        type: fvector
      - id: ang
        type: fvector
      - id: posdiv
        type: fvector
      - id: angdiv
        type: fvector
      - id: ofs
        type: fvector
      - id: mode
        type: s4
      - id: index
        type: s4
      - id: set
        type: s4
      - id: pad2
        type: s4
      - id: retdiv0
        type: f4
      - id: pcodiv
        type: f4
      - id: acodiv
        type: f4
      - id: pad4
        type: f4
  cam01:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: fpos
        type: fvector
      - id: fang
        type: fvector
      - id: fofs
        type: fvector
      - id: tpos
        type: fvector
      - id: tang
        type: fvector
      - id: tofs
        type: fvector
      - id: pdiv
        type: fvector
      - id: adiv
        type: fvector
      - id: fdir
        type: fvector
      - id: tdir
        type: fvector
      - id: retdiv
        type: f4
      - id: mode
        type: s4
      - id: index
        type: s4
      - id: set
        type: s4
      - id: time0
        type: s4
      - id: time1
        type: s4
      - id: time2
        type: s4
      - id: time3
        type: s4
  cam02:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: fpos
        type: fvector
      - id: fang
        type: fvector
      - id: fofs
        type: fvector
      - id: tpos
        type: fvector
      - id: tang
        type: fvector
      - id: tofs
        type: fvector
      - id: pdiv
        type: fvector
      - id: adiv
        type: fvector
      - id: fdir
        type: fvector
      - id: tdir
        type: fvector
      - id: cpos
        type: fvector
      - id: cang
        type: fvector
      - id: cofs
        type: fvector
      - id: cdir
        type: fvector
      - id: retdiv
        type: f4
      - id: mode
        type: s4
      - id: index
        type: s4
      - id: set
        type: s4
      - id: time0
        type: s4
      - id: time1
        type: s4
      - id: time2
        type: s4
      - id: time3
        type: s4
      - id: time4
        type: s4
      - id: time5
        type: s4
      - id: time6
        type: s4
      - id: time7
        type: s4
  snd00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: swid
        type: s4
      - id: kyid
        type: s4
      - id: mode
        type: s4
      - id: inter
        type: s4
      - id: vol
        type: f4
      - id: dat0
        type: s4
      - id: pad0
        type: s8
  walk02:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: f_prm
        type: fire_common
  walk03:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: walkspd
        type: s4
      - id: juryoku
        type: s2
      - id: wait
        type: s2
      - id: jumphigh
        type: s2
      - id: jumptime
        type: s2
      - id: t_ypos
        type: s4
      - id: target0
        type: s2
      - id: target1
        type: s2
      - id: pad0
        type: s4
      - id: fire
        type: fire_common2
  walk01:
    seq:
      - id: walk
        type: walk_common
  fire00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: fire_w0
        type: f4
      - id: fire_w1
        type: f4
      - id: ang_x
        type: f4
      - id: ang_y
        type: f4
      - id: wait
        type: s4
      - id: time
        type: s4
      - id: stop
        type: s4
      - id: pad
        type: s4
  fire10:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: wait
        type: s4
      - id: pad0
        type: s4
      - id: pad1
        type: s4
      - id: pad2
        type: s4
  sub00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: item
        type: s4
      - id: out
        type: s4
      - id: cnt
        type: s4
      - id: type
        type: s4
      - id: o_rno
        type: s4
      - id: o_mcn
        type: s4
      - id: o_yofs
        type: f4
      - id: o_time
        type: s4
      - id: t_rno
        type: s4
      - id: t_yofs
        type: f4
      - id: t_mcn
        type: s4
      - id: t_time
        type: s4
  swit00:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: rdat
        type: s4
      - id: out
        type: s4
      - id: cnt
        type: s4
      - id: x_time
        type: s4
      - id: o_rno
        type: s4
      - id: o_yofs
        type: f4
      - id: o_mcn
        type: s4
      - id: o_time
        type: s4
      - id: t_rno
        type: s4
      - id: t_yofs
        type: f4
      - id: t_mcn
        type: s4
      - id: t_time
        type: s4
  swit01:
    seq:
      - id: movetbl
        type: zako_movetbl
      - id: id
        type: s4
      - id: mode
        type: s4
      - id: wait
        type: s4
      - id: def
        type: s4
      - id: len
        type: f4
      - id: yoff
        type: f4
      - id: ysize
        type: f4
      - id: no
        type: s4
      - id: std
        type: s4
      - id: swid
        type: s4
      - id: snd
        type: s4
      - id: pad
        type: s4