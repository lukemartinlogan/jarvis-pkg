from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.basic.exception import Error, ErrorCode


class PackageQuery:
    def __init__(self):
        self.pkg_id = PackageId(None, None, None)
        self._versions = set()
        self._variants = {}
        self._dependencies = {}
        self._parent = None
        self._null = False
        self._or = []

    def update_query(self, other):
        isect = self.intersect(other)
        self.pkg_id = isect.pkg_id
        self._versions = isect._versions
        self._variants = isect._variants
        self._dependencies = isect._dependencies
        self._parent = isect._parent
        self._null = isect._null
        self._or = isect._or

    def get_class(self):
        if self.is_complex():
            return self._or[0].pkg_id.cls
        else:
            return self.pkg_id.cls

    def get_names(self):
        if not self.is_complex():
            return [self.pkg_id.name]
        return [pkg_query.pkg_id.name for pkg_query in self._or]

    def set_variant(self, key, value):
        self._variants[key] = value

    def intersect_version_range(self, min, max):
        self._versions = set(v for v in self._versions if min <= v <= max)

    @staticmethod
    def set_id_part(my_name, other_name):
        if my_name is None:
            return other_name
        elif other_name is None:
            return my_name
        elif my_name == other_name:
            return my_name
        else:
            raise Error(ErrorCode.PKG_IDS_DO_NOT_MATCH).format(my_name,
                                                               other_name)

    def _intersect_pkg_id(self, new_query, other):
        new_pkg_id = PackageId(
            self.set_id_part(self.pkg_id.namespace, other.pkg_id.namespace),
            self.set_id_part(self.pkg_id.cls, other.pkg_id.cls),
            self.set_id_part(self.pkg_id.name, other.pkg_id.name))
        new_query.pkg_id = new_pkg_id

    def _intersect_versions(self, new_query, other):
        if len(other._versions) == 0 or len(new_query._versions) == 0:
            new_query._versions.update(self._versions)
            new_query._versions.update(other._versions)
        else:
            new_query._versions = self._versions.intersection(other._versions)
        if len(new_query._versions) == 0:
            raise Error(ErrorCode.VERSIONS_CANT_BE_MERGED).format()

    def _intersect_variants(self, new_query, other):
        for key, value in other._variants.items():
            my_value = self._variants[key]
            if type(value) != type(my_value):
                return self.null()
            if isinstance(value, set):
                new_query._variants[key] = value.intersection(value, my_value)
            elif value == my_value:
                new_query._variants[key] = my_value
            else:
                raise Error(ErrorCode.VARIANTS_INCOMPATIBLE).format()

    def simple_intersect(self, other):
        new_query = PackageQuery()
        if not self.is_simple() or not other.is_simple():
            raise Error(ErrorCode.INTERSECT_COMPLEX_QUERIES).format()
        try:
            self._intersect_pkg_id(new_query, other)
            self._intersect_versions(new_query, other)
            self._intersect_variants(new_query, other)
            return new_query
        except Error as e:
            return self.null()

    def intersect(self, other):
        new_query = PackageQuery()
        if other.is_complex() and self.is_complex():
            for other_pkg_query in other._or:
                for my_pkg_query in self._or:
                    isect = my_pkg_query.simple_intersect(other_pkg_query)
                    if not isect.is_null():
                        new_query._or.append(isect)
        elif not other.is_complex() and self.is_complex():
            for my_pkg_query in self._or:
                isect = my_pkg_query.simple_intersect(other)
                if not isect.is_null():
                    new_query._or.append(isect)
        elif other.is_complex() and not self.is_complex():
            for my_pkg_query in other._or:
                isect = my_pkg_query.simple_intersect(other)
                if not isect.is_null():
                    new_query._or.append(isect)
        else:
            return self.simple_intersect(other)

    def is_null(self):
        return self._null

    def is_simple(self):
        return len(self._or) == 0

    def is_complex(self):
        return len(self._or) > 0

    def null(self):
        null_query = PackageQuery()
        null_query._null = True
        return null_query

    def to_string(self):
        return f"{self.pkg_id}\n{self._variants}\n{self._versions}"

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()
