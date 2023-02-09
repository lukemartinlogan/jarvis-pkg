from .package_query import PackageQuery
from jarvis_pkg.util.system_info import SystemInfo
from abc import ABC, abstractmethod


class Package(ABC):
    def __init__(self):
        super().__init__()
        self.name = None
        self.cls = None
        self.all_versions = []
        self.all_variants = {}
        self.all_dependencies = []
        self.phases = []
        self.variants_ = None
        self.dependencies_ = None
        self.version_ = None
        self.uuid_ = None
        self.is_installed = False
        self.define_versions()
        self.define_variants()
        self.define_dependencies()

    @abstractmethod
    def define_versions(self):
        pass

    @abstractmethod
    def define_variants(self):
        pass

    @abstractmethod
    def define_dependencies(self):
        pass

    @abstractmethod
    def get_dependencies(self, spec):
        """
        Get dependencies depending on the installation specification.

        :param spec: the set of solidified packages
        :return: list of dependency package queries
        """
        pass

    def from_query(self, pkg_query):
        """
        Select package version and variants based on pkg_query

        :param pkg_query:
        :return:
        """
        # Solidify version
        self.all_versions.sort(reverse=True)
        for version in self.all_versions:
            if self._version_in_range(version, pkg_query.versions):
                self.version_ = version
        if self.version_ is None:
            return None
        # Solidify variants
        self.variants_ = self.all_variants.copy()
        for key, val in pkg_query.variants.items():
            if key in self.variants_:
                self.variants_[key] = val
            else:
                return None
        # Make uuid
        self.make_uuid()
        return self

    def _version_in_range(self, version, ranges):
        for rng in ranges:
            if rng[0] >= version or version >= rng[1]:
                return False
        return True

    def make_uuid(self):
        variants = hash(str(self.variants_))
        version = hash(self.version_)
        dependencies = hash(self.dependencies_)
        sysinfo = hash(SystemInfo.get_instance())
        self.uuid_ = hash(variants ^ version ^ dependencies ^ sysinfo)
        return self
