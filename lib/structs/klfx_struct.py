# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Klfx(KaitaiStruct):

    class GsPsm(Enum):
        psmct32 = 0
        psmct24 = 1
        psmct16 = 2
        psmct16s = 10
        psmt8 = 19
        psmt4 = 20
        psmt8h = 27
        psmt4hl = 36
        psmt4hh = 44
        psmz32 = 48
        psmz24 = 49
        psmz16 = 50
        psmz16s = 58
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header = Klfx.Header(self._io, self, self._root)
        self.parts = []
        for i in range(self.header.part_count):
            self.parts.append(Klfx.Part(self._io, self, self._root))


    class Weight(KaitaiStruct):
        """Since these vertex weights do not always add up to 255 (0xFF), it is 
        recommended to divide the weights by the sum of all the weights.
        """
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
        """The origin point for UVs is at the top left of the image.
        
        Currently, it is recommended to make a 1024x1024 image for the texture 
        (even if the texture is not actually that big, but it's just to ensure
        everything fits in) and divide the UVs by 16384.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_u4le()
            self.v = self._io.read_u4le()


    class Tristrip(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start = Klfx.Index(self._io, self, self._root)
            self.indices = []
            for i in range((self.start.flag - 1)):
                self.indices.append(Klfx.Index(self._io, self, self._root))



    class GsregTex0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tbp0 = self._io.read_bits_int_le(14)
            self.tbw = self._io.read_bits_int_le(6)
            self.psm = KaitaiStream.resolve_enum(Klfx.GsPsm, self._io.read_bits_int_le(6))
            self.tw = self._io.read_bits_int_le(4)
            self.th = self._io.read_bits_int_le(4)
            self.tcc = self._io.read_bits_int_le(1) != 0
            self.tfx = self._io.read_bits_int_le(2)
            self.cbp = self._io.read_bits_int_le(14)
            self.cpsm = KaitaiStream.resolve_enum(Klfx.GsPsm, self._io.read_bits_int_le(4))
            self.csm = self._io.read_bits_int_le(1) != 0
            self.csa = self._io.read_bits_int_le(5)
            self.cld = self._io.read_bits_int_le(3)


    class TristripGroup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tristrips = []
            i = 0
            while True:
                _ = Klfx.Tristrip(self._io, self, self._root)
                self.tristrips.append(_)
                if _.indices[(_.start.flag - 2)].flag == -1:
                    break
                i += 1


    class Coordinate(KaitaiStruct):
        """The coordinates are Y-UP, but remember: Y and Z are inverted!
        """
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
            if not self.reserved == b"\x00\x00\x00\x00":
                raise kaitaistruct.ValidationNotEqualError(b"\x00\x00\x00\x00", self.reserved, self._io, u"/types/header/seq/4")


    class Part(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enable = self._io.read_u2le()
            self.some_number = self._io.read_u2le()
            self.tristrip_count = self._io.read_u2le()
            self.tristrip_group_count = self._io.read_u2le()
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
            self.tex0 = Klfx.GsregTex0(self._io, self, self._root)

        @property
        def vertices(self):
            if hasattr(self, '_m_vertices'):
                return self._m_vertices

            _pos = self._io.pos()
            self._io.seek(self.vertices_offset)
            self._m_vertices = []
            for i in range((self.vertex_count if self.subpart_count == 0 else 0)):
                self._m_vertices.append(Klfx.Coordinate(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)

        @property
        def uvs(self):
            if hasattr(self, '_m_uvs'):
                return self._m_uvs

            _pos = self._io.pos()
            self._io.seek(self.uvs_offset)
            self._m_uvs = []
            for i in range(self.uv_count):
                self._m_uvs.append(Klfx.Uv(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_uvs', None)

        @property
        def tristrip_groups(self):
            if hasattr(self, '_m_tristrip_groups'):
                return self._m_tristrip_groups

            _pos = self._io.pos()
            self._io.seek(self.indices_offset)
            self._m_tristrip_groups = []
            for i in range(self.tristrip_group_count):
                self._m_tristrip_groups.append(Klfx.TristripGroup(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_tristrip_groups', None)

        @property
        def subparts(self):
            """All parts that have a joint influence have at least 1 subpart.
            Parts that need to have more than 4 joint influences will have more
            than 1 subpart.
            Some parts may not even have subparts/joint influences, hence why 
            there are instances for vertices and normals in the part type.
            
            The start of a subpart's vertices/normals must be 16-byte aligned.
            This is very important for parts with more than 1 subpart, since subparts
            do not define a vertices/normals offset for that specific subpart.
            See the "prev_(vertices/normals)" and "res_(vertices/normals)" instances
            in the subpart type to see how this is handled.
            (Kaitai is very finnicky when doing that type of stuff, but it works :P)
            """
            if hasattr(self, '_m_subparts'):
                return self._m_subparts

            _pos = self._io.pos()
            self._io.seek(self.subparts_offset)
            self._m_subparts = []
            for i in range(self.subpart_count):
                self._m_subparts.append(Klfx.Subpart(i, self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_subparts', None)

        @property
        def normals(self):
            if hasattr(self, '_m_normals'):
                return self._m_normals

            _pos = self._io.pos()
            self._io.seek(self.normals_offset)
            self._m_normals = []
            for i in range((self.normal_count if self.subpart_count == 0 else 0)):
                self._m_normals.append(Klfx.Coordinate(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_normals', None)


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
                return self._m_weights

            _pos = self._io.pos()
            self._io.seek(self.weights_offset)
            self._m_weights = []
            for i in range(self.vertex_count):
                self._m_weights.append(Klfx.Weight(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_weights', None)

        @property
        def prev_normals(self):
            if hasattr(self, '_m_prev_normals'):
                return self._m_prev_normals

            self._m_prev_normals = (self._parent.normals_offset if self.i == 0 else self._parent.subparts[(self.i - 1)].res_normals)
            return getattr(self, '_m_prev_normals', None)

        @property
        def res_normals(self):
            if hasattr(self, '_m_res_normals'):
                return self._m_res_normals

            self._m_res_normals = ((self.prev_normals + (self._parent.subparts[self.i].normal_count * 6)) + ((16 - ((self._parent.subparts[self.i].normal_count * 6) % 16)) if ((self._parent.subparts[self.i].normal_count * 6) % 16) != 0 else 0))
            return getattr(self, '_m_res_normals', None)

        @property
        def vertices(self):
            """Vertices must be multiplied by the scale value in the header of the
            model.
            """
            if hasattr(self, '_m_vertices'):
                return self._m_vertices

            _pos = self._io.pos()
            self._io.seek(self.prev_vertices)
            self._m_vertices = []
            for i in range(self.vertex_count):
                self._m_vertices.append(Klfx.Coordinate(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_vertices', None)

        @property
        def res_vertices(self):
            if hasattr(self, '_m_res_vertices'):
                return self._m_res_vertices

            self._m_res_vertices = ((self.prev_vertices + (self._parent.subparts[self.i].vertex_count * 6)) + ((16 - ((self._parent.subparts[self.i].vertex_count * 6) % 16)) if ((self._parent.subparts[self.i].vertex_count * 6) % 16) != 0 else 0))
            return getattr(self, '_m_res_vertices', None)

        @property
        def prev_vertices(self):
            if hasattr(self, '_m_prev_vertices'):
                return self._m_prev_vertices

            self._m_prev_vertices = (self._parent.vertices_offset if self.i == 0 else self._parent.subparts[(self.i - 1)].res_vertices)
            return getattr(self, '_m_prev_vertices', None)

        @property
        def normals(self):
            """Normals must be divided by 0x1000 (4096).
            """
            if hasattr(self, '_m_normals'):
                return self._m_normals

            _pos = self._io.pos()
            self._io.seek(self.prev_normals)
            self._m_normals = []
            for i in range(self.normal_count):
                self._m_normals.append(Klfx.Coordinate(self._io, self, self._root))

            self._io.seek(_pos)
            return getattr(self, '_m_normals', None)


    class Joints(KaitaiStruct):
        """Joint influences that have a value of 0xFFFF (65535) are essentially "N/A".
        """
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


    class Index(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex = self._io.read_u2le()
            self.uv = self._io.read_u2le()
            self.normal = self._io.read_u2le()
            self.flag = self._io.read_s2le()



