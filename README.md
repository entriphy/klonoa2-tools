# Klonoa 2: Lunatea's Veil (PS2) Stuff
Klonoa 2 tools, docs, and other stuff.

This repository uses [Kaitai Struct](https://kaitai.io) to parse binary formats. To test and compile them to Python, use the [Kaitai Web IDE](https://ide.kaitai.io) or [download the compiler](https://kaitai.io/#download). 
* Pre-compiled parsers are provided in this repository.

## Reverse Engineering To-Do List
- [x] KLDATA.BIN Archive Extraction
    * The current method "sniffs" for offsets to check if a file is an archive/folder, which can be seen in the __is_archive function in [kldata_archive.py](https://github.com/evilarceus/klonoa2-tools/blob/4459276f73eb75132bfd6693ecd10e9d508b5dc2/lib/kldata_archive.py#L8). This will most likely be replaced with a proper hierarchy scanner in the future.
- [x] Models
    - [x] Mesh
    - [x] Textures
        * Klonoa's model requires a manual texture fix when extracted, but other than that, it works 95% of the time
    - [x] UVs
        * UVs are nearly perfect when using glTF files in Blender because it supports nearest mipmapping. Using .obj files or linear mipmapping causes noticable bleeding in some models.
    - [x] Rig/Bones
    - [x] Animations
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

## File types
File type names are arbitrary unless it is a standard PS2 format.
- `klf[abxyz]`: Model data
    - `klfa`: Animation data (keyframes, translations, rotations, name [8 bytes])
    - `klfb`: Bone/joint data (local positions, global/world positions, parent joints)
    - `klfx`: Mesh data (vertices, normals, UVs, weights, joint influences, indices, mesh parts)
    - `klfy`: Texture data (pixels, palettes)
    - `klfz`: Morph data (target, vertices, normals)
- `klname`: Model name (3 bytes)
- `hd`: PS2 soundbank header
- `bd`: PS2 soundbank data
- `vtipu`: Similar to PS2 .ipu (movie) file, used for stuff like water animations
- `gim`: Texture data
- `ppt`: Cutscene voice stored as Playstation 4-bit ADPCM (mono, 22050 Hz, 16bps)
- `kl0`: 16 bytes of `0x00`
- `klnull`: Starts with `null` string, 16 bytes long
- `klpad`: 4 bytes of `0xFF`, 12 bytes of `0x00`
