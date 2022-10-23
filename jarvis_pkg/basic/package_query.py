from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.basic.exception import Error, ErrorCode


class PackageQuery:
    def __init__(self):
        self.pkg_id = None
        self._versions = []
        self._variants = {}
        self._dependencies = {}
        self._parent = None
        self._or = []

    def get_class(self):
        return self._or[0].pkg_id.cls

    def get_names(self):
        if self._or is None:
            return [self.pkg_id.name]
        return [pkg_query.pkg_id.name for pkg_query in self._or]

    def intersect(self, other):
        pass
