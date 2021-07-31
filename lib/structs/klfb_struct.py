# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if parse_version(kaitaistruct.__version__) < parse_version('0.9'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Klfb(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.count = self._io.read_u4le()
        self.local_joints_offset = self._io.read_u4le()
        self.global_joints_offset = self._io.read_u4le()
        self.parent_joints = [None] * (self.count)
        for i in range(self.count):
            self.parent_joints[i] = self._io.read_u2le()


    class Coordinate(KaitaiStruct):
        """Y and Z axes are inverted.
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.zero = self._io.read_f4le()


    @property
    def local_joints(self):
        if hasattr(self, '_m_local_joints'):
            return self._m_local_joints if hasattr(self, '_m_local_joints') else None

        _pos = self._io.pos()
        self._io.seek(self.local_joints_offset)
        self._m_local_joints = [None] * (self.count)
        for i in range(self.count):
            self._m_local_joints[i] = Klfb.Coordinate(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_local_joints if hasattr(self, '_m_local_joints') else None

    @property
    def global_joints(self):
        if hasattr(self, '_m_global_joints'):
            return self._m_global_joints if hasattr(self, '_m_global_joints') else None

        _pos = self._io.pos()
        self._io.seek(self.global_joints_offset)
        self._m_global_joints = [None] * (self.count)
        for i in range(self.count):
            self._m_global_joints[i] = Klfb.Coordinate(self._io, self, self._root)

        self._io.seek(_pos)
        return self._m_global_joints if hasattr(self, '_m_global_joints') else None


