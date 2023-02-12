from .package_query import PackageQuery
from jarvis_pkg.query_parser.parse import QueryParser
from jarvis_pkg.util.system_info import SystemInfo
from jarvis_pkg.util.naming import to_snake_case
from .jpkg_manifest_manager import JpkgManifestManager
from .jpkg_manager import JpkgManager
from .version import Version
from abc import ABC, abstractmethod
import inspect, pathlib, os


def install(method):
    def _install_impl(*args, **kwargs):
        method(*args, **kwargs)
    return _install_impl


def uninstall(method):
    def _uninstall_impl(*args, **kwargs):
        method(*args, **kwargs)
    return _uninstall_impl


class Package(ABC):
    def __init__(self, do_full_load):
        super().__init__()
        self.jpkg = JpkgManager.get_instance()
        self.manifest = JpkgManifestManager.get_instance()
        self.repo = self._get_repo()
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
        self.install_path = None

        self._parse_decorators()
        self.define_class()
        self.define_versions()
        self.define_variants()
        if do_full_load:
            self.define_dependencies()

    def _parse_decorators(self):
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_install_impl':
                        self.install_phases.append(value)
                    if value.__name__ == '_uninstall_impl':
                        self.uninstall_phases.append(value)

    def _get_repo(self):
        filepath = inspect.getfile(self.__class__)
        repo_path = pathlib.Path(filepath).parent.parent.parent.resolve()
        repo = os.path.basename(repo_path)
        return repo

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

    def variant(self, key, default=None, choices=None, vtype=None, msg=None):
        if vtype is None:
            if choices is not None:
                types = set(type(choice) for choice in choices
                            if not isinstance(choice, type(None)))
                if len(types) == 1:
                    vtype = list(types)[0]
            elif default is not None:
                vtype = type(default)
        self.all_variants[key] = {
            'choices': choices,
            'msg': msg,
            'type': vtype
        }
        self.variants_[key] = default

    def depends_on(self, cls):
        query = PackageQuery(cls)
        if query.cls is None:
            raise Exception(f"{cls} is not a class or package name")
        query.is_null = False
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

    def to_query(self):
        query = PackageQuery()
        query.name = self.name
        query.cls = self.cls
        query.intersect_version_range(self.version_, self.version_)
        query.variants = self.variants_.copy()
        query.is_null = False
        return query

    def from_query(self, pkg_query):
        """
        Select package version and variants based on pkg_query

        :param pkg_query:
        :return:
        """
        # Solidify version
        self.all_versions.sort(reverse=True,
                               key=lambda x: x['version'])
        for version_info in self.all_versions:
            version = version_info['version']
            if self._version_in_range(version, pkg_query.versions):
                self.version_ = version
                break
        if self.version_ is None:
            return None
        # Solidify variants
        for key, val in pkg_query.variants.items():
            if self._variant_valid(key, val):
                self.variants_[key] = self._variant_val(key, val)
            else:
                return None
        return self

    def matches(self, pkg_query):
        """
        Check whether or not a package satisfies a query

        :param pkg_query: The query being verified
        :return:
        """
        if isinstance(pkg_query, str):
            pkg_query = QueryParser(pkg_query).first()
        self_query = self.to_query()
        return not self_query.intersect(pkg_query).is_null

    def _variant_val(self, key, val):
        variant_info = self.all_variants[key]
        if val is not None and variant_info['type'] is not None:
            val = variant_info['type'](val)
        return val

    def _variant_valid(self, key, val):
        if key in self.all_variants:
            val = self._variant_val(key, val)
            if val in self.all_variants[key]['choices']:
                return True
        return False

    def _version_in_range(self, version, ranges):
        for rng in ranges:
            if rng[0] > version or version > rng[1]:
                return False
        return True

    def make_uuid(self, cur_uuids):
        nonce = 0
        while self.uuid_ is None:
            variants = hash(str(self.variants_))
            version = hash(self.version_) * nonce
            dependencies = hash(str(self.dependencies_))
            sysinfo = hash(SystemInfo.get_instance())
            uuid = abs(hash(variants ^ version ^ dependencies ^ sysinfo))
            nonce += 1
            if uuid not in cur_uuids:
                self.uuid_ = uuid
        self.install_path = os.path.join(self.jpkg.pkg_dir,
                                         f"{self.name}-{self.uuid_}")
        return self
