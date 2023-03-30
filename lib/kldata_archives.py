from lib.util.read_bytes import s32le, u32le
from lib.chr import CHR_IDs
import os

vision = -1

# Base class
class Archive:
    buffer: bytes = None # Data buffer
    buffer_offset: int = 0 # Offset of this archive in the buffer
    size: int = -1 # Total size of archive (including offsets in header)
    has_size: bool = False # Archive size is included after offset list
    name: str = None # Name of archive
    parent = None # Parent archive
    index: int = -1 # Index in parent archive
    archives: list[tuple[object, str]] = None # [(class, name)]
    filenames: list[str] = None # Names for each file in the archives
    expected_count: int = -1

    def __init__(self, buffer: bytes, buffer_offset: int, size: int = -1, name: str = None, parent = None, index: int = -1, unpacking: bool = True):
        self.buffer = buffer
        self.buffer_offset = buffer_offset
        self.size = size
        self.name = name
        self.parent = parent
        self.index = index
        if unpacking:
            self.setup_archive()
    
    def setup_archive(self):
        return

    def get_file_count(self) -> int:
        return s32le(self.buffer, self.buffer_offset)
    
    def get_file_offset(self, index: int) -> int:
        return self.buffer_offset + s32le(self.buffer, self.buffer_offset + 4 + index * 4)
    
    def get_file_size(self, index: int) -> int:
        file_count = self.get_file_count()
        file_offset = self.get_file_offset(index)
        if index + 1 < file_count or self.has_size:
            file_size = self.get_file_offset(index + 1) - file_offset
        else:
            file_size = self.buffer_offset + self.size - file_offset
        return file_size

    def read_file(self, index: int) -> bytes:
        file_count = self.get_file_count()
        if index + 1 > file_count:
            raise "Index out of range"
        file_offset = self.get_file_offset(index)
        file_size = self.get_file_size(index)
        
        return self.buffer[file_offset:file_offset + file_size]
    
    def read_files(self) -> list[bytes]:
        files = []
        for i in range(self.get_file_count()):
            files.append(self.read_file(i))
        return files
    
    def write_files(self, output_dir: str):
        if not os.access(output_dir, os.R_OK):
            os.mkdir(output_dir)
        file_count = self.get_file_count()
        if file_count == -1:
            return
        for i in range(file_count):
            if self.archives != None and self.archives[i] != None:
                archive = self.archives[i]
                name = archive[1]
                file_offset = self.get_file_offset(i)
                file_size = self.get_file_size(i)
                arc: Archive = archive[0](self.buffer, file_offset, file_size, name, parent=self, index=i)
                if file_size == 0 and self.expected_count != -1:
                    continue
                arc.write_files(f"{output_dir}/{i}{'_' + name if name != None else ''}")
            else:
                filename = self.filenames[i] if self.filenames != None and self.filenames[i] != None else f"unk.dat"
                file_path = f"{output_dir}/{i}_{filename}"
                file = self.read_file(i)
                if len(file) == 0 and self.expected_count != -1:
                    continue
                with open(file_path, "wb") as f:
                    f.write(file)

class PreloadArchive(Archive):
    def setup_archive(self):
        if self.index != -1:
            global vision
            vision = self.index // 2
            self.name = f"vision{str(vision).zfill(2)}_preload"
        self.size = self.get_file_offset(7) - self.buffer_offset + 0x10
        self.archives = [None for _ in range(self.get_file_count())]
        self.archives[0] = (Archive, "nakano")
        self.archives[1] = (Archive, "okano")
        self.archives[2] = (HoshinoPreloadArchive, "hoshino")
        self.archives[3] = (Archive, "harada")
        self.archives[4] = (AbePreloadArchive, "abe")
        self.archives[5] = (Archive, "hato")
        self.archives[6] = (Archive, "take")
        self.archives[7] = (Archive, "kazuya")

class RootArchive(Archive):
    def setup_archive(self):
        if self.index != -1:
            global vision
            vision = self.index // 2
            self.name = f"vision{str(vision).zfill(2)}_root"
        self.size = self.get_file_offset(7) - self.buffer_offset + 0x10
        self.archives = [None for _ in range(self.get_file_count())]
        self.archives[0] = (NakanoArchive, "nakano")
        self.archives[1] = (OkanoArchive, "okano")
        self.archives[2] = (HoshinoArchive, "hoshino")
        self.archives[3] = (HaradaArchive, "harada")
        self.archives[4] = (AbeArchive, "abe")
        self.archives[5] = (Archive, "hato")
        self.archives[6] = (Archive, "take")
        self.archives[7] = (Archive, "kazuya")

class SpritesArchive(Archive):
    def setup_archive(self):
        self.archives = [None for _ in range(self.get_file_count())]
        self.archives[0] = (NakanoSpritesArchive, "nakano")
        self.archives[1] = (Archive, "okano")
        self.archives[2] = (Archive, "hoshino")
        self.archives[3] = (Archive, "harada")
        self.archives[4] = (Archive, "abe")
        self.archives[5] = (Archive, "hato")
        self.archives[6] = (Archive, "take")
        self.filenames = [None for _ in range(self.get_file_count())]
        self.filenames[7] = "kazuya_sprites.gms"
        self.size = self.get_file_offset(7) + u32le(self.buffer, self.get_file_offset(7) + 0x08) - self.buffer_offset

class NakanoSpritesArchive(Archive):
    def setup_archive(self):
        self.filenames = ["idk.dat", "now_loading.gms"]

class HoshinoPreloadArchive(Archive):
    has_size = True
    
    def setup_archive(self):
        self.filenames = ["jam_bank_header.hd", "jam_bank_data.bd", "jam_bank.idx"]

class AbePreloadArchive(Archive):
    def setup_archive(self):
        self.archives = [(AbeGimPreloadArchive, f"gims{i}") for i in range(self.get_file_count())]

class AbeGimPreloadArchive(Archive):
    def setup_archive(self):
        self.archives = [None, (AbeGimPackPreloadArchive, "gims")]
        self.filenames = ["gims.idx", None]

class AbeGimPackPreloadArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"gim{i}.gim" for i in range(self.get_file_count())]

class NakanoArchive(Archive):
    def setup_archive(self):
        if self.get_file_count() != -1:
            self.archives = [None for _ in range(self.get_file_count())]
            self.archives[0] = (NakanoMapsArchive, "maps")
            self.archives[1] = (NakanoChrsArchive, "chr")
            self.archives[2] = (NakanoGimArchive, "gim")

class NakanoMapsArchive(Archive):
    def setup_archive(self):
        file_count = self.get_file_count()
        self.filenames = [f"st{str(vision).zfill(2)}.rcn"] + [None for _ in range(1, file_count)]
        self.archives = [None for _ in range(file_count)]
        for i in range(1, file_count):
            self.archives[i] = (NakanoMapArchive, f"map{hex(vision)[2:].zfill(2)}{hex(i-1)[2:].zfill(2)}")

class NakanoMapArchive(Archive):
    def setup_archive(self):
        map_str = f"{hex(vision)[2:].zfill(2)}{hex(self.index-1)[2:].zfill(2)}"
        self.filenames = [f"map{map_str}.gms.nc", f"map{map_str}.vpm.nc", f"map{map_str}.rt", f"map{map_str}.hmp.nc", f"cam{map_str}.kcm", f"lgt{map_str}.dat"]

class NakanoChrsArchive(Archive):
    expected_count = 937

    def setup_archive(self):
        self.archives = [(NakanoChrLodArchive, CHR_IDs(i).name) for i in range(self.get_file_count() - 1)] + [None]

class NakanoChrLodArchive(Archive):
    def setup_archive(self):
        self.archives = [(NakanoChrArchive, self.name + ["l", "m", "s", "f"][i]) for i in range(self.get_file_count())]

class NakanoChrArchive(Archive):
    def setup_archive(self):
        self.archives = [None, (NakanoChrGmsArchive, "gms"), (NakanoChrFzArchive, "fz"), (NakanoChrActArchive, "act"), None]
        self.filenames = ["model.fx", None, None, None, "info.dat"]

class NakanoChrGmsArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"gms{i}.gms" for i in range(self.get_file_count())]

class NakanoChrFzArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"fz{i}.fz" for i in range(self.get_file_count())]

class NakanoChrActArchive(Archive):
    expected_count = 0

    def setup_archive(self):
        self.filenames = ["inf.dat"] + [f"{self.get_act_name(i)}.act" for i in range(1, self.get_file_count())]
    
    def get_act_name(self, index: int) -> str:
        offset = self.get_file_offset(index)
        name = self.buffer[offset + 8:offset + 16].split(b"\x00")[0].decode("ascii")
        return name

class NakanoGimArchive(Archive):
    def setup_archive(self):
        self.filenames = []
        match vision:
            case 0x01:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "spray0100.sdt",
                    "spray0102.sdt",
                    "wave0100.wdt",
                    "wave0101.wdt",
                    "wave0102.wdt",
                    "wave0103.wdt",
                    "wave0104.wdt",
                    "wave0106.wdt",
                    "dummy.dat",
                    "keyfrm01_e_5.bin",
                    "ipu2.vtipu"
                ]
            case 0x02:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 0x04:
                self.filenames = [
                    "ea_gon00.hmp",
                    "map0413.hmp",
                    "map0414.hmp",
                    "map0415.hmp",
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu"
                ]
            case 0x05:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu",
                    "dummy.dat",
                    "keyfrm05_e_3.bin"
                ]
            case 0x06:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu"
                ]
            case 0x07:
                self.filenames = [
                    "unk.hmp",
                    "unk.hmp",
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu"
                ]
            case 0x08:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                ]
            case 0x09:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu",
                    "ipu3.vtipu"
                ]
            case 10:
                self.filenames = [
                    "ipu0.vtipu",
                ]
            case 11:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu",
                    "ipu3.vtipu",
                    "ipu4.vtipu",
                    "ipu5.vtipu",
                    "ipu6.vtipu",
                    "ipu7.vtipu"
                ]
            case 12:
                self.filenames = [
                    "hanmer.hmp"
                    "ipu0.vtipu",
                    "ipu1.vtipu"
                ]
            case 13:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "wave1300.wdt",
                    "wave1301.wdt",
                    "wave1302.wdt",
                    "wave1303.wdt",
                    "wave1304.wdt",
                    "wave1305.wdt",
                    "ipu2.vtipu",
                    "ipu3.vtipu"
                ]
            case 14:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu",
                    "ipu3.vtipu"
                ]
            case 15:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu",
                    "wave1508.wdt",
                    "ipu3.vtipu",
                    "wave1502.wdt" # yes, 02 comes after 08 lmao
                ]
            case 16:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 17:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu"
                ]
            case 18:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 19:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 22:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 23:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 26:
                self.filenames = [
                    "ipu0.vtipu",
                    "unk.hmp"
                ]
            case 30:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 34:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu"
                ]
            case 39:
                self.filenames = [
                    "ipu0.vtipu"
                ]
            case 40:
                self.filenames = [
                    "ipu0.vtipu",
                    "ipu1.vtipu",
                    "ipu2.vtipu"
                ]
        self.filenames.append("dummy.dat")

class OkanoArchive(Archive):
    def setup_archive(self):
        self.filenames = [
            "dreamstone.gms",
            "l_dreamstone.gms",
            "dreamstone.vpm",
            "l_dreamstone.vpm",
            "myubo1.5.hmp",
            "Gmoo.hmp",
            "hako3.hmp",
            "yuka01.hmp",
            "yuka02.hmp",
            "doram.hmp",
            "okuidoyuka.hmp",
            "map0636.hmp",
            "map0635.hmp",
            "oku5m.hmp",
            "planehit.hmp",
            "kaiten_b.hmp",
            "map0631.hmp",
            "map0636.rt",
            "map0635.rt",
            "oku5m.rt",
            "planert.rt",
            "kanran.rt",
            "map0631.rt",
            f"zakid{str(vision).zfill(2)}.dat"
        ]

        sectors = (self.get_file_count() - 24) // 3
        for i in range(sectors):
            self.filenames.append(f"zak{str(vision).zfill(2)}{hex(i)[2:].zfill(2)}.dat")
            self.filenames.append(f"itm{str(vision).zfill(2)}{hex(i)[2:].zfill(2)}.dat")
            self.filenames.append(f"zako{str(vision).zfill(2)}{hex(i)[2:].zfill(2)}.rt")

class HoshinoArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"ev{str(vision).zfill(2)}{hex(i)[2:].zfill(2)}.data" for i in range(self.get_file_count())]

class HaradaArchive(Archive):
    def setup_archive(self):
        self.archives = [(HaradaDatasArchive, "dat"), None, (HaradaBackgroundTexturesArchiveArchive, "bgtex"), (HaradaConfigsArchive, "config"), None, None]
        self.filenames = [None, "dialogue_box.gms", None, None, f"ptse{str(vision).zfill(2)}.bin", "dialogue_text.gms"]

class HaradaPuppetArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"pt{i}.ppt" for i in range(self.get_file_count())]

class HaradaBackgroundTexturesArchiveArchive(Archive): # lol
    def setup_archive(self):
        self.archives = [(HaradaBackgroundTexturesArchive, f"bgs{i}") if self.get_file_size(i) != 0x10 else None for i in range(self.get_file_count())]

class HaradaBackgroundTexturesArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"bg{i}.gms" for i in range(self.get_file_count())]

class HaradaConfigsArchive(Archive):
    def setup_archive(self):
        self.filenames = [f"map{str(vision).zfill(2)}{hex(i)[2:].zfill(2)}.mvc" for i in range(self.get_file_count())]

class HaradaDatasArchive(Archive):
    def setup_archive(self):
        self.archives = [(HaradaDataArchive, f"dat{hex(i)[2:].zfill(2)}") for i in range(self.get_file_count())]

class HaradaDataArchive(Archive):
    def setup_archive(self):
        self.filenames = [
            "bg0.vpm",
            "bg1.vpm",
            "bg2.vpm",
            "bg3.vpm",
            "bg4.vpm",
            "bg5.vpm",
            "bg0.anm",
            "bg1.anm",
            "bg2.anm",
            "bg3.anm",
            "bg4.anm",
            "bg5.anm",
            "flat_mir.vpm",
            "curve_mir.vpm",
            "unk.vpa",
            "unk.vpo",
            "mtex.vpm",
            "mini_ppt.dat",
            f"hrp{str(vision).zfill(2)}{hex(self.index)[2:].zfill(2)}.fhm",
            "m1100a.vpm",
            "m1100b.vpm"
        ]

        self.archives = [None for i in range(self.get_file_count())]
        if self.get_file_size(18) != 0x10:
            self.archives[18] = (HaradaPuppetArchive, f"hrp{str(vision).zfill(2)}{hex(self.index)[2:].zfill(2)}")

class AbeArchive(Archive):
    expected_count = 120