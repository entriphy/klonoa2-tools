# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Klfz(KaitaiStruct):
    def __init__(self, input_klfx, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self.input_klfx = input_klfx
        self._read()

    def _read(self):
        self.header = Klfz.Header(self._io, self, self._root)
        self.parts = [None] * (self.header.part_count)
        for i in range(self.header.part_count):
            self.parts[i] = Klfz.Part(self.input_klfx, self._io, self, self._root)


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(2)
            if not self.magic == b"\x46\x5A":
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x5A", self.magic, self._io, u"/types/header/seq/0")
            self.part_count = self._io.read_u2le()
            self.magic2 = self._io.read_bytes(4)
            if not self.magic2 == b"\x80\x00\x40\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x80\x00\x40\x00", self.magic2, self._io, u"/types/header/seq/2")
            self.scale = self._io.read_f4le()
            self.reserved = self._io.read_bytes(4)
            if not self.reserved == b"\x00\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00", self.reserved, self._io, u"/types/header/seq/4")


    class Part(KaitaiStruct):
        def __init__(self, klfxx, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.klfxx = klfxx
            self._read()

        def _read(self):
            self.part_number = self._io.read_u2le()
            self.data_size = self._io.read_u2le()
            self.vertex_count = self._io.read_u2le()
            self.normal_count = self._io.read_u2le()
            self.vertices_offset = self._io.read_u4le()
            self.normals_offset = self._io.read_u4le()
            self.reserved = self._io.read_bytes(16)

        @property
        def subparts(self):
            if hasattr(self, '_m_subparts'):
                return self._m_subparts if hasattr(self, '_m_subparts') else None

            self._m_subparts = [None] * (self.klfxx.parts[self.part_number].subpart_count)
            for i in range(self.klfxx.parts[self.part_number].subpart_count):
                self._m_subparts[i] = Klfz.Subpart(i, self.klfxx, self._io, self, self._root)

            return self._m_subparts if hasattr(self, '_m_subparts') else None


    class Subpart(KaitaiStruct):
        def __init__(self, i, klfxx, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.i = i
            self.klfxx = klfxx
            self._read()

        def _read(self):
            pass

        @property
        def prev_normals(self):
            if hasattr(self, '_m_prev_normals'):
                return self._m_prev_normals if hasattr(self, '_m_prev_normals') else None

            self._m_prev_normals = (self._parent.normals_offset if self.i == 0 else self._parent.subparts[(self.i - 1)].res_normals)
            return self._m_prev_normals if hasattr(self, '_m_prev_normals') else None

        @property
        def res_normals(self):
            if hasattr(self, '_m_res_normals'):
                return self._m_res_normals if hasattr(self, '_m_res_normals') else None

            self._m_res_normals = ((self.prev_normals + (self.klfxx.parts[self._parent.part_number].subparts[self.i].normal_count * 6)) + ((16 - ((self.klfxx.parts[self._parent.part_number].subparts[self.i].normal_count * 6) % 16)) if ((self.klfxx.parts[self._parent.part_number].subparts[self.i].normal_count * 6) % 16) != 0 else 0))
            return self._m_res_normals if hasattr(self, '_m_res_normals') else None

        @property
        def vertices(self):
            if hasattr(self, '_m_vertices'):
                return self._m_vertices if hasattr(self, '_m_vertices') else None

            _pos = self._io.pos()
            self._io.seek(self.prev_vertices)
            self._m_vertices = [None] * (self.klfxx.parts[self._parent.part_number].subparts[self.i].vertex_count)
            for i in range(self.klfxx.parts[self._parent.part_number].subparts[self.i].vertex_count):
                self._m_vertices[i] = Klfz.Coordinate(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_vertices if hasattr(self, '_m_vertices') else None

        @property
        def res_vertices(self):
            if hasattr(self, '_m_res_vertices'):
                return self._m_res_vertices if hasattr(self, '_m_res_vertices') else None

            self._m_res_vertices = ((self.prev_vertices + (self.klfxx.parts[self._parent.part_number].subparts[self.i].vertex_count * 6)) + ((16 - ((self.klfxx.parts[self._parent.part_number].subparts[self.i].vertex_count * 6) % 16)) if ((self.klfxx.parts[self._parent.part_number].subparts[self.i].vertex_count * 6) % 16) != 0 else 0))
            return self._m_res_vertices if hasattr(self, '_m_res_vertices') else None

        @property
        def prev_vertices(self):
            if hasattr(self, '_m_prev_vertices'):
                return self._m_prev_vertices if hasattr(self, '_m_prev_vertices') else None

            self._m_prev_vertices = (self._parent.vertices_offset if self.i == 0 else self._parent.subparts[(self.i - 1)].res_vertices)
            return self._m_prev_vertices if hasattr(self, '_m_prev_vertices') else None

        @property
        def normals(self):
            if hasattr(self, '_m_normals'):
                return self._m_normals if hasattr(self, '_m_normals') else None

            _pos = self._io.pos()
            self._io.seek(self.prev_normals)
            self._m_normals = [None] * (self.klfxx.parts[self._parent.part_number].subparts[self.i].normal_count)
            for i in range(self.klfxx.parts[self._parent.part_number].subparts[self.i].normal_count):
                self._m_normals[i] = Klfz.Coordinate(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_normals if hasattr(self, '_m_normals') else None


    class Coordinate(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()



