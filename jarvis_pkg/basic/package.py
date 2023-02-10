from .package_query import PackageQuery
from jarvis_pkg.util.system_info import SystemInfo
from jarvis_pkg.util.naming import to_snake_case
from .jpkg_manifest_manager import JpkgManifestManager
from .version import Version
from abc import ABC, abstractmethod


def install():
    def wrap(method):
        def _jpkg_decor_impl(*args, **kwargs):
            self = args[0]
            self.install_phases.append(method)
        return _jpkg_decor_impl
    return wrap


def uninstall():
    def wrap(method):
        def _jpkg_decor_impl(*args, **kwargs):
            self = args[0]
            self.install_phases.append(method)
        return _jpkg_decor_impl
    return wrap


class Package(ABC):
    def __init__(self, do_full_load):
        super().__init__()
        self.manifest = JpkgManifestManager.get_instance()
        self.name = self._get_name()
        self.cls = None
        self.all_versions = []
        self.all_variants = {}
        self.all_dependencies = []
        self.install_phases = []
        self.uninstall_phases = []

        self.variants_ = {}
        self.dependencies_ = {}
        self.version_ = None
        self.uuid_ = None
        self.is_installed = False

        self.define_class()
        self.define_versions()
        self.define_variants()
        if do_full_load:
            self.define_dependencies()

    def _get_name(self):
        name = self.__class__.__name__
        name = name.replace("Package", "")
        return to_snake_case(name)

    def classify(self, cls):
        self.cls = cls

    def version(self, vstring, git=None, url=None, stable=True):
        self.all_versions.append({
            'version': Version(vstring),
            'git': git,
            'url': url,
            'stable': stable
        })

    def variant(self, key, default=None, choices=None, msg=None):
        self.all_variants[key] = {
            'choices': choices,
            'msg': msg
        }
        self.variants_[key] = default

    def depends_on(self, cls):
        # TODO(llogan): verify cls is a class
        query = PackageQuery(cls)
        self.all_dependencies.append(query)

    @abstractmethod
    def define_class(self):
        pass

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
        self.all_versions.sort(reverse=True,
                               key=lambda x: x['version'])
        for version in self.all_versions:
            if self._version_in_range(version, pkg_query.versions):
                self.version_ = version
        if self.version_ is None:
            return None
        # Solidify variants
        for key, val in pkg_query.variants.items():
            if self._variant_valid(key, val):
                self.variants_[key] = val
            else:
                return None
        # Make uuid
        self.make_uuid()
        return self

    def matches(self, pkg_query):
        """
        Check whether or not a package satisfies a query

        :param pkg_query: The query being verified
        :return:
        """


    def _variant_valid(self, key, val):
        if key in self.all_variants:
            if val in self.all_variants[key]['choices']:
                return True
        return False

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
