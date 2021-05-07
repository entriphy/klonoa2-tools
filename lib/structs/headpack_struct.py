# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Headpack(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.bin_count = self._io.read_u4le()
        self.kldata_offset = self._io.read_u4le()
        self.bgmpack_offset = self._io.read_u4le()
        self.pptpack_offset = self._io.read_u4le()
        self.headpack_size = self._io.read_u4le()

    class Pointers(KaitaiStruct):
        def __init__(self, start_offset, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.start_offset = start_offset
            self._read()

        def _read(self):
            self.archive_count = self._io.read_u4le()

        @property
        def archives(self):
            if hasattr(self, '_m_archives'):
                return self._m_archives if hasattr(self, '_m_archives') else None

            if self.archive_count != 5:
                _pos = self._io.pos()
                self._io.seek((self.start_offset + 4))
                self._m_archives = [None] * (self.archive_count)
                for i in range(self.archive_count):
                    self._m_archives[i] = Headpack.Archive(self._io, self, self._root)

                self._io.seek(_pos)

            return self._m_archives if hasattr(self, '_m_archives') else None

        @property
        def pal_archives(self):
            if hasattr(self, '_m_pal_archives'):
                return self._m_pal_archives if hasattr(self, '_m_pal_archives') else None

            if self.archive_count == 5:
                _pos = self._io.pos()
                self._io.seek(self.start_offset)
                self._m_pal_archives = Headpack.PalArchive(self._io, self, self._root)
                self._io.seek(_pos)

            return self._m_pal_archives if hasattr(self, '_m_pal_archives') else None


    class Archive(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sector_offset = self._io.read_u4le()
            self.sectors = self._io.read_u4le()

        @property
        def offset(self):
            if hasattr(self, '_m_offset'):
                return self._m_offset if hasattr(self, '_m_offset') else None

            self._m_offset = (self.sector_offset * 2048)
            return self._m_offset if hasattr(self, '_m_offset') else None

        @property
        def size(self):
            if hasattr(self, '_m_size'):
                return self._m_size if hasattr(self, '_m_size') else None

            self._m_size = (self.sectors * 2048)
            return self._m_size if hasattr(self, '_m_size') else None


    class PalArchiveList(KaitaiStruct):
        def __init__(self, start_offset, i, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.start_offset = start_offset
            self.i = i
            self._read()

        def _read(self):
            pass

        @property
        def kldata(self):
            if hasattr(self, '_m_kldata'):
                return self._m_kldata if hasattr(self, '_m_kldata') else None

            _pos = self._io.pos()
            self._io.seek((self.start_offset + self._parent.archive_offsets[self.i]))
            self._m_kldata = Headpack.Pointers((self.start_offset + self._parent.archive_offsets[self.i]), self._io, self, self._root)
            self._io.seek(_pos)
            return self._m_kldata if hasattr(self, '_m_kldata') else None


    class PalArchive(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pal_kldata_count = self._io.read_u4le()
            self.archive_offsets = [None] * (self.pal_kldata_count)
            for i in range(self.pal_kldata_count):
                self.archive_offsets[i] = self._io.read_u4le()


        @property
        def kldata_list(self):
            if hasattr(self, '_m_kldata_list'):
                return self._m_kldata_list if hasattr(self, '_m_kldata_list') else None

            self._m_kldata_list = [None] * (self.pal_kldata_count)
            for i in range(self.pal_kldata_count):
                self._m_kldata_list[i] = Headpack.PalArchiveList(self._parent.start_offset, i, self._io, self, self._root)

            return self._m_kldata_list if hasattr(self, '_m_kldata_list') else None


    @property
    def kldata(self):
        if hasattr(self, '_m_kldata'):
            return self._m_kldata if hasattr(self, '_m_kldata') else None

        _pos = self._io.pos()
        self._io.seek(self.kldata_offset)
        self._m_kldata = Headpack.Pointers(self.kldata_offset, self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_kldata if hasattr(self, '_m_kldata') else None

    @property
    def bgmpack(self):
        if hasattr(self, '_m_bgmpack'):
            return self._m_bgmpack if hasattr(self, '_m_bgmpack') else None

        _pos = self._io.pos()
        self._io.seek(self.bgmpack_offset)
        self._m_bgmpack = Headpack.Pointers(self.bgmpack_offset, self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_bgmpack if hasattr(self, '_m_bgmpack') else None

    @property
    def pptpack(self):
        if hasattr(self, '_m_pptpack'):
            return self._m_pptpack if hasattr(self, '_m_pptpack') else None

        _pos = self._io.pos()
        self._io.seek(self.pptpack_offset)
        self._m_pptpack = Headpack.Pointers(self.pptpack_offset, self._io, self, self._root)
        self._io.seek(_pos)
        return self._m_pptpack if hasattr(self, '_m_pptpack') else None


