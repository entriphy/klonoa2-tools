# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Klfx(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Klfx.Header(self._io, self, self._root)
        self.parts = [None] * (self.header.part_count)
        for i in range(self.header.part_count):
            self.parts[i] = Klfx.Part(self._io, self, self._root)


    class Weight(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a = self._io.read_u1()
            self.b = self._io.read_u1()
            self.c = self._io.read_u1()
            self.d = self._io.read_u1()


    class Uv(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_u4le()
            self.v = self._io.read_u4le()


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


    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magic = self._io.read_bytes(2)
            if not self.magic == b"\x46\x58":
                raise kaitaistruct.ValidationNotEqualError(b"\x46\x58", self.magic, self._io, u"/types/header/seq/0")
            self.part_count = self._io.read_u2le()
            self.magic2 = self._io.read_bytes(4)
            if not self.magic2 == b"\x80\x00\x40\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x80\x00\x40\x00", self.magic2, self._io, u"/types/header/seq/2")
            self.scale = self._io.read_f4le()
            self.reserved = self._io.read_bytes(4)


    class Part(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.part_thing = self._io.read_bytes(2)
            self.some_number = self._io.read_u2le()
            self.triangle_strip_count = self._io.read_u2le()
            self.indices_part_count = self._io.read_u2le()
            self.uv_count = self._io.read_u2le()
            self.subpart_count = self._io.read_u2le()
            self.vertex_count = self._io.read_u2le()
            self.normal_count = self._io.read_u2le()
            self.indices_offset = self._io.read_u4le()
            self.uvs_offset = self._io.read_u4le()
            self.vertices_offset = self._io.read_u4le()
            self.normals_offset = self._io.read_u4le()
            self.subparts_offset = self._io.read_u4le()
            self.reserved = self._io.read_u4le()
            self.uv_thing = self._io.read_bytes(6)
            self.part_end = self._io.read_bytes(2)

        @property
        def subparts(self):
            if hasattr(self, '_m_subparts'):
                return self._m_subparts if hasattr(self, '_m_subparts') else None

            _pos = self._io.pos()
            self._io.seek(self.subparts_offset)
            self._m_subparts = [None] * (self.subpart_count)
            for i in range(self.subpart_count):
                self._m_subparts[i] = Klfx.Subpart(i, self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_subparts if hasattr(self, '_m_subparts') else None

        @property
        def uvs(self):
            if hasattr(self, '_m_uvs'):
                return self._m_uvs if hasattr(self, '_m_uvs') else None

            _pos = self._io.pos()
            self._io.seek(self.uvs_offset)
            self._m_uvs = [None] * (self.uv_count)
            for i in range(self.uv_count):
                self._m_uvs[i] = Klfx.Uv(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_uvs if hasattr(self, '_m_uvs') else None


    class Subpart(KaitaiStruct):
        def __init__(self, i, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.i = i
            self._read()

        def _read(self):
            self.joints = Klfx.Joints(self._io, self, self._root)
            self.vertex_count = self._io.read_u2le()
            self.normal_count = self._io.read_u2le()
            self.some_numbers = self._io.read_bytes(4)
            self.reserved = self._io.read_bytes(4)
            self.weights_offset = self._io.read_u4le()
            self.some_other_numbers = self._io.read_bytes(8)

        @property
        def weights(self):
            if hasattr(self, '_m_weights'):
                return self._m_weights if hasattr(self, '_m_weights') else None

            _pos = self._io.pos()
            self._io.seek(self.weights_offset)
            self._m_weights = [None] * (self.vertex_count)
            for i in range(self.vertex_count):
                self._m_weights[i] = Klfx.Weight(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_weights if hasattr(self, '_m_weights') else None

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

            self._m_res_normals = ((self.prev_normals + (self._parent.subparts[self.i].normal_count * 6)) + ((16 - ((self._parent.subparts[self.i].normal_count * 6) % 16)) if ((self._parent.subparts[self.i].normal_count * 6) % 16) != 0 else 0))
            return self._m_res_normals if hasattr(self, '_m_res_normals') else None

        @property
        def vertices(self):
            if hasattr(self, '_m_vertices'):
                return self._m_vertices if hasattr(self, '_m_vertices') else None

            _pos = self._io.pos()
            self._io.seek(self.prev_vertices)
            self._m_vertices = [None] * (self.vertex_count)
            for i in range(self.vertex_count):
                self._m_vertices[i] = Klfx.Coordinate(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_vertices if hasattr(self, '_m_vertices') else None

        @property
        def res_vertices(self):
            if hasattr(self, '_m_res_vertices'):
                return self._m_res_vertices if hasattr(self, '_m_res_vertices') else None

            self._m_res_vertices = ((self.prev_vertices + (self._parent.subparts[self.i].vertex_count * 6)) + ((16 - ((self._parent.subparts[self.i].vertex_count * 6) % 16)) if ((self._parent.subparts[self.i].vertex_count * 6) % 16) != 0 else 0))
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
            self._m_normals = [None] * (self.normal_count)
            for i in range(self.normal_count):
                self._m_normals[i] = Klfx.Coordinate(self._io, self, self._root)

            self._io.seek(_pos)
            return self._m_normals if hasattr(self, '_m_normals') else None


    class Joints(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a = self._io.read_u2le()
            self.b = self._io.read_u2le()
            self.c = self._io.read_u2le()
            self.d = self._io.read_u2le()



