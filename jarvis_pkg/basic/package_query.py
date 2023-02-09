from .jpkg_manifest_manager import JpkgManifestManager
import copy


class PackageQuery:
    def __init__(self, namespace=None, name=None, cls=None):
        self.manifest = JpkgManifestManager.get_instance()
        self.namespace = namespace
        self.name = name
        self.cls = cls
        self.variants = {}      # a dict of keys -> variant options
        self.versions = []      # a list of Version ranges
        self.dependencies = {}  # a dict of PackageQuery
        if namespace is None and name is None and cls is None:
            self.is_null = True
        else:
            self.is_null = False

    def intersect_version_range(self, min, max):
        self.versions.append((min, max))

    def intersect(self, other):
        new_query = copy.deepcopy(self)
        # Namespace
        if other.namespace is not None:
            if self.namespace is None or other.namespace == self.namespace:
                new_query.namespace = other.namespace
            else:
                return PackageQuery()
        # Class
        if other.cls is not None:
            if self.cls is None or other.cls == self.cls:
                new_query.cls = other.cls
            else:
                return PackageQuery()
        # Name
        if other.name is not None:
            if self.name is None or other.name == self.name:
                new_query.name = other.name
            else:
                return PackageQuery()
        # Variants
        for key, val in other.variants.items():
            if key not in self.variants or self.variants[key] == val:
                new_query.variants[key] = val
            else:
                return PackageQuery()
        # Dependencies
        for key, val in other.dependencies.items():
            if key not in self.dependencies:
                new_query.dependencies[key] = val
            else:
                my_dep_query = self.dependencies[key]
                other_dep_query = other.dependencies[key]
                isect = my_dep_query.intersect(other_dep_query)
                if isect.is_null():
                    return PackageQuery()
                else:
                    new_query.dependencies[key] = isect
        # Versions
        new_query.versions += other.versions
        # Mark as non-null
        new_query.is_null = False
