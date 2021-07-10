# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class KlfaAlt(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.joint_count = self._io.read_u2le()
        self.keyframe_count = self._io.read_u2le()
        self.rotation_count = self._io.read_u2le()
        self.translation_count = self._io.read_u2le()
        self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 0, False)).decode(u"ASCII")
        self.stuff = self._io.read_bytes(16)
        self.joint_targets = self._io.read_u8le()
        self.more_stuff = self._io.read_bytes(8)
        self.initial_pos = KlfaAlt.FloatCoordinate(self._io, self, self._root)
        self.scale = self._io.read_f4le()
        self.rotation_offset = self._io.read_u4le()
        self.translation_offset = self._io.read_u4le()
        self.reserved = self._io.read_bytes(4)
        self.transition_in = self._io.read_u2le()
        self.transition_out = self._io.read_u2le()
        self.this_stuff_doesnt_get_read_by_the_game_lol = self._io.read_bytes(12)

    class JointTranslation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.keyframe_count = self._io.read_u2le()
            self.keyframes = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.keyframes[i] = self._io.read_u2le()

            self.keyframe_total = self._io.read_u2le()
            self.coordinates = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.coordinates[i] = KlfaAlt.Coordinate(self._io, self, self._root)



    class FrameTranslation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.joint_translations = [None] * (self._parent.translation_count)
            for i in range(self._parent.translation_count):
                self.joint_translations[i] = KlfaAlt.Coordinate(self._io, self, self._root)



    class JointRotation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.keyframe_count = self._io.read_u2le()
            self.keyframes = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.keyframes[i] = self._io.read_u2le()

            self.keyframe_total = self._io.read_u2le()
            self.rotations = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.rotations[i] = KlfaAlt.Rotation(self._io, self, self._root)



    class Rotation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_u2le()
            self.y = self._io.read_u2le()
            self.z = self._io.read_u2le()


    class FloatCoordinate(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()


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


    class FrameRotation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.joint_rotations = [None] * (self._parent.rotation_count)
            for i in range(self._parent.rotation_count):
                self.joint_rotations[i] = KlfaAlt.Rotation(self._io, self, self._root)



    @property
    def rotations(self):
        if hasattr(self, '_m_rotations'):
            return self._m_rotations if hasattr(self, '_m_rotations') else None

        _pos = self._io.pos()
        self._io.seek(self.rotation_offset)
        self._m_rotations = [None] * (self.keyframe_count)
        for i in range(self.keyframe_count):
            self._m_rotations[i] = KlfaAlt.FrameRotation(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_rotations if hasattr(self, '_m_rotations') else None

    @property
    def translations(self):
        if hasattr(self, '_m_translations'):
            return self._m_translations if hasattr(self, '_m_translations') else None

        _pos = self._io.pos()
        self._io.seek(self.translation_offset)
        self._m_translations = [None] * (self.keyframe_count)
        for i in range(self.keyframe_count):
            self._m_translations[i] = KlfaAlt.FrameTranslation(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_translations if hasattr(self, '_m_translations') else None


