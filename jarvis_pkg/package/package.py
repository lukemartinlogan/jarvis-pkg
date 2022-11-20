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
            self.versions_.add(v['version'])
        self.version_ = None
        self._install_method = None
        self.is_installed = False
        self.source_dir = None
        self.tmp_source_dir = None
        self.unique_name = None

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

    def version(self, version, method='source', url=None, git=None, branch=None, commit=None,
                gpg=None, stable=True, needs_root=False):
        if isinstance(version, str):
            version = Version(version)
        vinfo = {
            'version': version,
            'method': method,
            'url': url,
            'git': git,
            'branch': branch,
            'commit': commit,
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
        self.variants_.update(self.variants)
        self.variants_.update(pkg_query.variants_)
        versions = []
        for vinfo in self.versions:
            if vinfo['version'] not in self.versions_:
                continue
            if not self.variants_['root'] and vinfo['needs_root']:
                continue
            if self.variants_['stable'] and not vinfo['stable']:
                continue
            versions.append(vinfo)
        self.version_ = max(versions, key=lambda x: x['version'])
        if len(self.phases):
            self._solidify_install_method(list(self.phases.keys())[0])

    def _load_superclass_decorators(self):
        self.phases = {} # pkg_name -> (needs_root, [phase_functions])
        self.phase_confs = {} # pkg_name -> (needs_root, [conf_functions])
        self.introspect = {} # pkg_name -> (needs_root, [introspect_functions])
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_jpkg_decor_impl':
                        value(self, in_init=True)

    def _solidify_install_method(self, installer_name):
        self._install_method = installer_name
        if installer_name not in self.phase_confs:
            return
        for phase_conf in self.phase_confs[installer_name][1]:
            self.__dict__[phase_conf.__name__] = phase_conf

    def get_phases(self):
        return self.phases[self._install_method][1]

    def to_string(self):
        return f"{self.pkg_id} : {self.version_['version']}"

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def get_unique_name(self):
        if self.unique_name is not None:
            return self.unique_name
        sysinfo = hash(SystemInfoNode().Run())
        variants = hash(str(self.variants_))
        deps = hash(str(self.dependencies_))
        method = hash(self._install_method)
        h = abs(hash(sysinfo ^ variants ^ deps ^ method))
        self.unique_name = f"{self.pkg_id.name}-{h}"
        return self.unique_name

    def to_query(self):
        pkg_query = PackageQuery()
        pkg_query.copy_query(self)
        pkg_query.version_ = self.version_
        pkg_query._install_method = self._install_method
        pkg_query.is_installed = self.is_installed
        pkg_query.source_dir = self.source_dir
        pkg_query.tmp_source_dir = self.tmp_source_dir
        pkg_query.unique_name = self.unique_name
        return pkg_query

