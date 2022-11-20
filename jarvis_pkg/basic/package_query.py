from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.basic.exception import Error, ErrorCode


class PackageQuery:
    def __init__(self):
        self.pkg_id = PackageId(None, None, None)
        self.versions_ = set()
        self.variants_ = {}
        self.dependencies_ = {}
        self.parent_ = None
        self.null_ = False
        self.or_ = []

    def update_query(self, other):
        isect = self.intersect(other)
        self.copy_query(isect)

    def copy_query(self, other):
        self.pkg_id = other.pkg_id
        self.versions_ = other.versions_
        self.variants_ = other.variants_
        self.dependencies_ = other.dependencies_
        self.parent_ = other.parent_
        self.null_ = other.null_
        self.or_ = other.or_

    def get_class(self):
        if self.is_complex():
            return self.or_[0].pkg_id.cls
        else:
            return self.pkg_id.cls

    def get_names(self):
        if not self.is_complex():
            return [self.pkg_id.name]
        return [pkg_query.pkg_id.name for pkg_query in self.or_]

    def set_variant(self, key, value):
        self.variants_[key] = value

    def intersect_version_range(self, min, max):
        self.versions_ = set(v for v in self.versions_ if min <= v <= max)

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
        if len(other.versions_) == 0 or len(new_query.versions_) == 0:
            new_query.versions_.update(self.versions_)
            new_query.versions_.update(other.versions_)
        else:
            new_query.versions_ = self.versions_.intersection(other.versions_)
        if len(new_query.versions_) == 0:
            raise Error(ErrorCode.VERSIONS_CANT_BE_MERGED).format()

    def _intersect_variants(self, new_query, other):
        for key, value in other.variants_.items():
            my_value = self.variants_[key]
            if type(value) != type(my_value):
                return self.null()
            if isinstance(value, set):
                new_query.variants_[key] = value.intersection(value, my_value)
            elif value == my_value:
                new_query.variants_[key] = my_value
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
            for other_pkg_query in other.or_:
                for my_pkg_query in self.or_:
                    isect = my_pkg_query.simple_intersect(other_pkg_query)
                    if not isect.is_null():
                        new_query.or_.append(isect)
        elif not other.is_complex() and self.is_complex():
            for my_pkg_query in self.or_:
                isect = my_pkg_query.simple_intersect(other)
                if not isect.is_null():
                    new_query.or_.append(isect)
        elif other.is_complex() and not self.is_complex():
            for my_pkg_query in other.or_:
                isect = my_pkg_query.simple_intersect(other)
                if not isect.is_null():
                    new_query.or_.append(isect)
        else:
            return self.simple_intersect(other)

    def is_null(self):
        return self.null_

    def is_simple(self):
        return len(self.or_) == 0

    def is_complex(self):
        return len(self.or_) > 0

    def null(self):
        null_query = PackageQuery()
        null_query.null_ = True
        return null_query

    def to_string(self):
        return f"{self.pkg_id}\n{self.variants_}\n{self.versions_}"

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()
