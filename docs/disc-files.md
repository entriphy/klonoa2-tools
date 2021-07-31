# Disc Files

This page lists the structure of the main data files on the disc.

*Thanks to vervalkon for general information about the structure of `HEADPACK.BIN` and `KLDATA.BIN`!*

## HEADPACK.BIN
*A Kaitai Struct parser for `HEADPACK.BIN` is included in `lib/structs/ks`.*

`HEADPACK.BIN` is an index file that defines where archives/files are located in the other data files. All values in this file are represented as 4-byte unsigned integers.<br>
The first value in the file is `0x03`, which represents the 3 data files on the disc: `KLDATA.BIN`, `BGMPACK.BIN`, and `PPTPACK.BIN`.
The 3 pointers after that represent the locations in `HEADPACK.BIN` that describes the number of files/archives in the respective data file and (sector offset, size) pair for each item. *(1 DVD sector = 2048 bytes)*

For example:
- The pointer for `KLDATA.BIN`  is `0x20`. 
- The value at `0x20` (`0xC8`/200) represents the number of archives in `KLDATA.BIN`.
- The values after the archive count are (sector offset, size) pairs for each archive.
  - Ex. The pair `0x12a, 0x1b8` means the archive is located at byte offset `0x95000` in `KLDATA.BIN` and has a size of `0xdc000` bytes. *(Remember to multiply sector values by 2048!)*

**NOTE:** There is a third value in the `BGMPACK.BIN` (sector offset, size) pairs that is supposed to correspond to a `BGM00X.AC3` file. The `BGMPACK.BIN` structure has not been reversed yet.<br>
**NOTE:** In the PAL version of the game, there are 5 sets of sector pointers for `KLDATA.BIN` because there are 5 `KLDATA.BIN` files.

## KLDATA.BIN
`KLDATA.BIN` is the main data file, which contains pretty much all the main assets for the game. <br>
The PAL version contains 5 `KLDATA.BIN` files, each one corresponding to a different language. 
All of them are the exact same except for dialogue text and textures with text (ex. "Vision Start", vision names, etc).
| **Filename** | **Language** |
|--------------|--------------|
| KLDATA1.BIN  | English      |
| KLDATA2.BIN  | French       |
| KLDATA3.BIN  | Spanish      |
| KLDATA4.BIN  | German       |
| KLDATA5.BIN  | Italian      |

The first value of an archive (defined by the sector pointers in `HEADPACK.BIN`) is the number of files. The pointers after that value may lead to either a directory or a file, and the pointers in a directory may lead to another directory and those may... you get the point.
The issue here is that there is no precise way to tell if a pointer leads to a file or a directory. 
This most likely means that the game knows how to navigate the archive hierarchy and that the hierarchy has a consistent structure.
Note that a proper hierarchy scanner has not been implemented yet and the scripts in this repository still "sniff" the first few rows of bytes to detect if something is a directory or a file.

**NOTE:** Some files, such as models and textures, are duplicated for each vision. This is done to improve loading speed.

## BGMPACK.BIN
<TODO; not reversed yet>

## PPTPACK.BIN
`PPTPACK.BIN` contains all voice files used in cutscenes. All files are stored as Playstation 4-bit ADPCM with 1 channel (mono) at 22050 Hz.
This data can be used as waveform data in a VAG file, and VAG files can be played using the [vgmstream plugin](https://github.com/vgmstream/vgmstream) for foobar2000/WinAmp.
More info about the VAG format can be found [here (psdevwiki.com)](https://www.psdevwiki.com/ps3/Multimedia_Formats_and_Tools#VAG).
An example of a PPT-to-VAG converter can be found in `lib/filetypes/ppt.py`.

This does **not** contain sound effects; those are located in `KLDATA.BIN` as soundbanks (.hd, .bd).
