# KLDATA Hierarchy

## Notes
* File types
  * File: Normal file
  * Directory: Contains pointers that lead to other files
  * Archive: "Root directories" that are defined in `HEADPACK.BIN`
* Archives 0 and 1 are empty.
* Every even archive is a "preload archive", and every odd archive is a "data archive".
  * Ex. For Sea of Tears, the game loads archive 2 (preload archive), transfers that data to VRAM/IOP RAM/elsewhere, and then loads archive 3 (data archive), thus removing archive 2 from main RAM.
* GIM files are texture files with the magic header `GIM`
* `n`: Variable number of files/directories
* `x-y`: Range of files/directories
* `L`: Last file in directory
* `[null]`: Empty data


## Preload archive
```
0 - could be [null] if the archive is used for a cutscene (ex. archive 6)
  0 - Textures for basic vision stuff (ex. vision title, "VISION START/CLEAR", Momett Doll indicator, etc)
1 - [null]
2 - Soundbank data
  0 - PS2 HD (header) file
  1 - PS2 BD (data) file
  2 - Indices for specific sound effects in the soundbank? (ex. lightning sound effects for Sea of Tears)
3 - [null]
4 - 
  0 -
    0 - Mainly particle textures (ex. water droplets/splashes, fire, lightning, dream stone pickup, etc)
      n - GIM files
    1 - Indices? (# of indices is equivalent to the # of GIM files; 0'ing this messes up the particles in-game)
  1 - 
    0 - Reflection textures
      n - GIM files
    1 - ? (probably indices)
5 - [null]
6 - [null]
7 - [null]
```

## Data archive
```
0 - 
  0 - Level data
    0 - ?
    n - Level section
      0 - Textures (compressed)
      1 - Geometry (compressed)
      2 - Positioning for camera, objects, lights, etc.
      3 - Collision data? (compressed)
      4 - Camera/path data?
      5 - Light data
  1 - Models
    n - Model
      n - LODs or alternate models (ex. Inflated model for enemies)
        0 - Geometry (vertices, normals, vertex weights, joint influences, UVs, tristrips)
        1 - Texture(s) (usually null for LODs--in this case, use the texture from the first alt model in the directory)
          n - Texture(s) (some may be null)
        2 - Morphs/blendshapes/shape keys/whatever you wanna call them (may be null)
          n - Morphs (some may be null)
        3 - Bone and animation data
          0 - Bone data (bone hierarchy, global and local joint translations)
          n - Animations
        4 - Model name (3 bytes)
    L - ? (has a bunch of float values)
  2 -
    n - ? (varied files; some are video files for some animations [ex. for water and fire], others I'm not too sure about)
1 -
  0 - Texture for green dream stone
  1 - Texture for blue dream stone
  2 - Green dream stone geometry (same format as level geometry)
  3 - Blue green stone geometry
  n - ? (A bunch of other files, may include skybox stuff)
2 -
  n
    n - [null]/?
3 -
  0 - ?
    if 0 is not null:
      0 - ?
      1 - ?
      2-17 - [null] (may need confirmation)
      18 - 
        0-3 - Cutscene data or null
    else:
      0-18: [null]
  1 - Dialogue box texture
  2 - 
    n -
      if 0 is not null:
        0 - Skybox texture?
        1-2 - [null]
      else:
        0-2: [null]
  3 -
    n - ?
  4 - ?
  5 - Font texture
4 - ?
5 - [null]
6 - [null]
7 - [null]
```
