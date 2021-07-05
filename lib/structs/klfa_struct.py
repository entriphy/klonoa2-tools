# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Klfa(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.joint_count = self._io.read_u2le()
        self.keyframe_count = self._io.read_u2le()
        self.more_joint_counts = self._io.read_bytes(4)
        self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 0, False)).decode(u"ASCII")
        self.stuff = self._io.read_bytes(8)
        self.data_offset = self._io.read_u4le()
        self.more_stuff = self._io.read_bytes((((6 + self.data_offset) - 32) + 6))
        self.initial_pos = Klfa.FloatCoordinate(self._io, self, self._root)
        self.scale = self._io.read_f4le()
        self.joint_translations = [None] * (self.joint_count)
        for i in range(self.joint_count):
            self.joint_translations[i] = Klfa.JointTranslation(self._io, self, self._root)

        self.joint_rotations = [None] * (self.joint_count)
        for i in range(self.joint_count):
            self.joint_rotations[i] = Klfa.JointRotation(self._io, self, self._root)


    class JointTranslation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.keyframe_count = self._io.read_u4le()
            self.keyframes = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.keyframes[i] = self._io.read_u2le()

            self.coordinates = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.coordinates[i] = Klfa.Coordinate(self._io, self, self._root)



    class JointRotation(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.keyframe_count = self._io.read_u4le()
            self.keyframes = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.keyframes[i] = self._io.read_u2le()

            self.rotations = [None] * (self.keyframe_count)
            for i in range(self.keyframe_count):
                self.rotations[i] = Klfa.Rotation(self._io, self, self._root)



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



