class Version:
    def __init__(self, version_string):
        self.version_string = version_string
        self.raw_version_tuple,self.version_tuple = Version._VersionStringToTuple(version_string)

    @staticmethod
    def _VersionStringToTuple(version_string):
        version_tuple = version_string.split('.')
        if len(version_tuple) == 0:
            raise 1
        if len(version_tuple) > 3:
            raise 2
        if version_tuple[0][0] == 'v':
            version_tuple[0] = version_tuple[0][1:]
        raw_version_tuple = [int(minor) for minor in version_tuple]
        version_tuple += [0]*(3 - len(version_tuple))
        return raw_version_tuple,version_tuple

    def Matches(self, v):
        for i in range(3):
            if len(self.raw_version_tuple) > i:
                if self.raw_version_tuple[i] != v.version_tuple[i]:
                    return False
        return True

    def __gt__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.raw_version_tuple[i] < v2.raw_version_tuple[i]:
                return False
            if self.raw_version_tuple[i] > v2.raw_version_tuple[i]:
                return True
        return len(self) > len(v2)

    def __lt__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.raw_version_tuple[i] < v2.raw_version_tuple[i]:
                return True
            if self.raw_version_tuple[i] > v2.raw_version_tuple[i]:
                return False
        return len(self) < len(v2)

    def __ge__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.raw_version_tuple[i] < v2.raw_version_tuple[i]:
                return False
            if self.raw_version_tuple[i] > v2.raw_version_tuple[i]:
                return True
        return len(self) >= len(v2)

    def __le__(self, v2):
        cnt = min((len(self), len(v2)))
        for i in range(cnt):
            if self.raw_version_tuple[i] < v2.raw_version_tuple[i]:
                return True
            if self.raw_version_tuple[i] > v2.raw_version_tuple[i]:
                return False
        return len(self) <= len(v2)

    def __eq__(self, v2):
        if len(self) != len(v2):
            return False
        return all([self.raw_version_tuple[i] == v2.raw_version_tuple[i] for i in range(len(self))])

    def __str__(self):
        return self.version_string

    def __repr__(self):
        return self.version_string

    def __len__(self):
        return len(self.raw_version_tuple)