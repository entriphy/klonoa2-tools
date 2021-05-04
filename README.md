# Klonoa 2: Lunatea's Veil (PS2) Stuff
Klonoa 2 tools, docs, and other stuff.

This repository uses [Kaitai Struct](https://kaitai.io) to parse binary formats. To test and compile them to Python, use the [Kaitai Web IDE](https://ide.kaitai.io) or [download the compiler](https://kaitai.io/#download). 
* Pre-compiled parsers are provided in this repository.

## Reverse Engineering To-Do List
- [x] KLDATA.BIN Archive Extraction
    * Might need some verification that it works correctly
- [ ] Models
    - [x] Mesh
    - [x] Textures
        * Klonoa's model requires a manual texture fix when extracted, but other than that, it works 95% of the time
    - [x] UVs
        * UVs have noticeable bleeding in some models, but it isn't too noticable in other models
    - [ ] Rig/Bones
    - [ ] Animations
- [ ] Visions (Stages)
    - [ ] Layout/Geometry
    - [ ] Textures
    - [ ] Animations (.vtipu/.ipu files)
    - [ ] ...basically everything else
- [ ] Sounds
    - [x] Voice Files (PPT)
    - [ ] Music (BGM)
        * QuickBMS can do this
    - [x] Sound Effects (Soundbanks)

