from jarvis_pkg.basic.exception import Error,ErrorCode

class Version:
    def __init__(self, version):
        if isinstance(version, str):
            self.vstring = version
            self.vtuple = Version._vstring_to_tuple(version)
        else:
            self.vstring = version.vstring
            self.vtuple = version.vtuple

    @staticmethod
    def _vstring_to_tuple(vstring):
        if vstring == 'min':
            return [0,0,0]
        if vstring == 'max':
            inf = float('inf')
            return [inf, inf, inf]
        version_tuple = vstring.split('.')
        if len(version_tuple) == 0 or len(version_tuple) > 3:
            raise Exception(f"Invalid version string: {vstring}")
        if version_tuple[0][0] == 'v':
            version_tuple[0] = version_tuple[0][1:]
        vtuple = [int(minor) for minor in version_tuple]
        return vtuple

    def __gt__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.vtuple[i] < v2.vtuple[i]:
                return False
            if self.vtuple[i] > v2.vtuple[i]:
                return True
        return len(self) > len(v2)

    def __lt__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.vtuple[i] < v2.vtuple[i]:
                return True
            if self.vtuple[i] > v2.vtuple[i]:
                return False
        return len(self) < len(v2)

    def __ge__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.vtuple[i] < v2.vtuple[i]:
                return False
            if self.vtuple[i] > v2.vtuple[i]:
                return True
        return len(self) >= len(v2)

    def __le__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.vtuple[i] < v2.vtuple[i]:
                return True
            if self.vtuple[i] > v2.vtuple[i]:
                return False
        return len(self) <= len(v2)

    def __eq__(self, v2):
        if len(self) != len(v2):
            return False
        return all([self.vtuple[i] == v2.vtuple[i] for i in range(len(self))])

    def __str__(self):
        return self.vstring

    def __repr__(self):
        return self.vstring

    def __len__(self):
        if self.vtuple is None:
            return 0
        return len(self.vtuple)

    def __hash__(self):
        return hash(self.vstring)
    