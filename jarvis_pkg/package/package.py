from jarvis_cd import *
from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.version import Version
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.query_parser import QueryParser
from abc import ABC, abstractmethod
import re


def multiparam_decor(self, class_f,
                  install, needs_root,
                  args, kwargs, phase_dict):
    in_init = False
    if 'in_init' in kwargs:
        in_init = kwargs['in_init']
    if in_init:
        if install not in phase_dict:
            phase_dict[install] = (needs_root, [])
        if needs_root:
            phase_dict[install][0] = needs_root
        phase_dict[install][1].append(class_f)
    else:
        class_f(self, *args, **kwargs)


def phase(install=None, needs_root=False):
    def wrap(class_f):
        def _jpkg_decor_impl(*args, **kwargs):
            self = args[0]
            multiparam_decor(self, class_f,
                          install, needs_root,
                          args, kwargs, self.phases)
        return _jpkg_decor_impl
    return wrap


def conf(install=None):
    def wrap(class_f):
        def _jpkg_decor_impl(*args, **kwargs):
            self = args[0]
            multiparam_decor(self, class_f,
                          install, False,
                          args, kwargs, self.phase_confs)
        return _jpkg_decor_impl
    return wrap


def introspect(install=None, needs_root=False):
    def wrap(class_f):
        def _jpkg_decor_impl(*args, **kwargs):
            self = args[0]
            multiparam_decor(self, class_f,
                          install, needs_root,
                          args, kwargs, self.introspect)
        return _jpkg_decor_impl
    return wrap


class Package(PackageQuery):
    def default_installer(self):
        if self.__class__.__name__ == 'Package':
            return None
        install = self.__class__.__mro__[1].__name__
        install = re.search('([a-zA-Z0-9]*)Package', install).group(1)
        install = ToSnakeCase(install)
        if len(install) == 0:
            install = None
        return install

    def __init__(self, pkg_id):
        super().__init__()
        self.pkg_id = pkg_id
        self.jpkg = JpkgManager.get_instance()
        self._load_superclass_decorators()
        self.versions = []
        self.version_set = set()
        self.variants = {}
        self.dependencies = {}
        self.patches = []
        self.conflicts = []
        self.variant("stable", bool, default=True,
                     msg = "Whether or not to prioritize stable versions")
        self.variant("root", bool, default=False,
                     msg = "Whether or not to consider installers which require root")

        self.define_versions()
        self.define_variants()
        self.define_dependencies()
        for v in self.versions:
            self._versions.add(v['version'])
        self._version = None

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
    def define_conflicts(self):
        pass

    def version(self, version, method='source', url=None, git=None, gpg=None,
                stable=True, needs_root=False):
        if isinstance(version, str):
            version = Version(version)
        vinfo = {
            'version': version,
            'method': method,
            'url': url,
            'git': git,
            'gpg': gpg,
            'stable': stable,
            'needs_root': needs_root
        }
        self.versions.append(vinfo)
        self.version_set.add(version)

    def depends_on(self, pkg_query):
        if isinstance(pkg_query, str):
            pkg = None  # TODO(llogan): parse into a query
        elif isinstance(pkg_query, PackageQuery):
            pkg = pkg_query
        else:
            raise Error(ErrorCode.INVALID_PARAMETER).format(type(pkg_query))
        self.dependencies[pkg.pkg_id.cls] = pkg

    def variant(self, key, dtype, default=None, multi=False, msg=None):
        variant_info = {
            'datatype': dtype,
            'multi': False,
            'value': default
        }
        self.variants[key] = variant_info

    def patch(self):
        # TODO(llogan)
        pass

    def conflict(self):
        # TODO(llogan)
        pass

    def solidify(self, pkg_query):
        self.update_query(pkg_query)
        self._variants.update(self.variants)
        self._variants.update(pkg_query._variants)
        versions = []
        for vinfo in self.versions:
            if vinfo['version'] not in self._versions:
                continue
            if not self._variants['root'] and vinfo['needs_root']:
                continue
            if self._variants['stable'] and not vinfo['stable']:
                continue
            versions.append(vinfo)
        self._version = max(versions, key=lambda x: x['version'])

    def _load_superclass_decorators(self):
        self.phases = {} # pkg_name -> (needs_root, [phase_functions])
        self.phase_confs = {} # pkg_name -> (needs_root, [conf_functions])
        self.introspect = {} # pkg_name -> (needs_root, [introspect_functions])
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_jpkg_decor_impl':
                        value(self, in_init=True)

    def to_string(self):
        return f"{self.pkg_id} : {self._version['version']}"

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()
