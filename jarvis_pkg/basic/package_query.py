from .jpkg_manifest_manager import JpkgManifestManager
from .version import Version
import copy


class PackageQuery:
    def __init__(self, text=None):
        self.manifest = JpkgManifestManager.get_instance()
        self.text = text
        self.repo = None
        self.name = None
        self.cls = None
        self.variants = {}      # a dict of keys -> variant options
        self.versions = []      # a list of Version ranges
        self.dependencies = {}  # a dict of PackageQuery
        self.is_null = True

        if text is not None:
            self._parse_query_text(text)
            self.is_null = False
        else:
            self.is_null = True

    def intersect_version_range(self, min, max):
        self.versions.append((min, max))

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
        return str(self.text)

    def __repr__(self):
        return str(self.text)
