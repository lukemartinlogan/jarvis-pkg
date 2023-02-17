from .jpkg_manifest_manager import JpkgManifestManager
from .version import Version
import copy


class PackageQuery:
    def __init__(self, text=None,
                 repo=None,
                 cls=None,
                 name=None,
                 installer=None):
        self.manifest = JpkgManifestManager.get_instance()
        self.repo = repo
        self.name = name
        self.cls = cls
        self.installer = installer
        if text is not None and len(text):
            toks = text.split('.')
            if len(toks) == 1:
                self.cls = self.manifest.get_class(text)
                if self.cls != text:
                    self.name = text
            elif len(toks) == 2:
                self.cls = toks[0]
                self.name = toks[1]
            elif len(toks) == 3:
                self.repo = toks[0]
                self.cls = toks[1]
                self.name = toks[2]
            else:
                raise Exception("Invalid text to package query")
        self.variants = {}      # a dict of keys -> variant options
        self.versions = []      # a list of Version ranges
        self.dependencies = {}  # a dict of PackageQuery
        self.is_null = (text is None
                        and repo is None
                        and cls is None
                        and name is None
                        and installer is None)

    def intersect_version_range(self, min, max):
        self.versions.append((min, max))

    def set_version(self, version):
        self.versions.append((version, version))

    def intersect(self, other):
        new_query = copy.deepcopy(self)
        # Namespace
        if other.repo is not None:
            if self.repo is None or other.repo == self.repo:
                new_query.repo = other.repo
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
                if isect.is_null:
                    return PackageQuery()
                else:
                    new_query.dependencies[key] = isect
        # Versions
        new_query.versions += other.versions
        if not new_query._verify_version_range():
            return PackageQuery()
        # Mark as non-null
        new_query.is_null = False
        return new_query

    def _verify_version_range(self):
        """
        Check whether the version range is empty set

        :return: True if not empty
        """
        if len(self.versions) == 0:
            return True
        min_max = max(self.versions, key=lambda x: x[0])
        max_min = min(self.versions, key=lambda x: x[1])
        return min_max <= max_min

    def matches(self, query):
        """
        Check whether or not two queries are intersectable

        :param query:
        :return:
        """
        return not self.intersect(query).is_null

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def to_string(self):
        return f"{self.repo}.{self.cls}.{self.name}/{self.installer}"
