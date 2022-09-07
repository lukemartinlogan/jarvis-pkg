from jarvis_cd import *
from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.version import Version
from jarvis_pkg.basic.query_parser import QueryParser
from jarvis_pkg.package.package_query import PackageQuery
from abc import ABC,abstractmethod
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

    def __init__(self):
        super().__init__()
        self.jpkg_manager = JpkgManager.get_instance()
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_jpkg_decor_impl':
                        value(self, in_init=True)
        self.install = self.default_installer()
        self.define_versions()

    def _solidify_variants(self):
        for key, val in self.default_variants.items():
            if key not in self.variants:
                self.variants[key] = val
        self.variants_ = self.variants

    def _solidify_installer(self, install=None):
        if install is None:
            install = self.version_['install']
        self.install_ = install
        for method in self.get_install_methods():
            setattr(self, method.__name__, method)

    def _solidify_from_existing(self):
        return False
        if self in self.jpkg_manager.install_env:
            pkgs = self.jpkg_manager.install_env.find(self)
            self.copy(pkgs[0])
            return True
        return False

    def _solidify_from_introspect(self):
        if not self.variants['introspect']:
            versions = [v_info for v_info in self.versions if self.needs_root(v_info)]
            if len(versions) == 0:
                raise Error(ErrorCode.REQUIRE_INTROSPECT).format(
                    self.namespace, self.name
                )
            self.versions = versions
            return False
        for install in self.phases.keys():
            versions = self.get_versions(install)
            method = self.get_introspect(install)
            if method is not None and len(versions) > 0:
                self._solidify_installer(install)
                v_info = method(self, versions)
                if v_info is not None:
                    self.version_ = v_info
                    return True
        return False

    def solidify_version(self):
        if self.is_solidified_:
            return
        if self._solidify_from_existing():
            return

        self._solidify_variants()
        if self._solidify_from_introspect():
            self.versions = [self.version_]
            self._solidify_installer()
            return

        if self.variants['prefer_stable']:
            versions = [v_info for v_info in self.versions if v_info['stable']]
            if len(versions) > 0:
                self.versions = versions
        self.versions.sort(key=lambda x: x['version'])
        self.versions = [self.versions[-1]]
        self.version_ = self.versions[-1]
        self._solidify_installer()

    @staticmethod
    def _solidify_deps(cur_env, deps, new_deps=None):
        if new_deps is None:
            new_deps = []
        for dep_pkg_row in deps.values():
            for dep_pkg_query, condition in dep_pkg_row:
                if condition in cur_env:
                    dep_pkgs = cur_env.find(cur_env, dep_pkg_query)
                    new_deps.append(dep_pkgs[0])
        return new_deps

    def solidify_deps(self, cur_env):
        if self.is_solidified_:
            return
        # Solidify dependencies
        self.patches_ = [patch_info for patch_info, condition in self.patches if condition in cur_env]
        self.build_deps_ = self._solidify_deps(cur_env, self.build_deps)
        self.run_deps_ = self._solidify_deps(cur_env, self.run_deps)
        self.filter_build_deps(self.build_deps_)
        self.filter_run_deps(self.run_deps_)
        self.filter_patches(self.patches_)

        # Check conflicts
        for query_a, query_b, msg in self.conflicts:
            p1 = query_a in cur_env
            p2 = query_b in cur_env
            if p1 and p2:
                raise Error(ErrorCode.CONFLICT).format(msg)

        self.is_solidified_ = True

    def filter_build_deps(self, build_deps):
        pass
    def filter_run_deps(self, run_deps):
        pass
    def filter_patches(self, patches):
        pass
    def check_conflicts(self):
        pass

    @staticmethod
    def _prefix_deps(deps):
        return [dep.prefix_ for dep in deps]

    def _get_variant_kv(self):
        return {key: v_info['value'] for key, v_info in self.variants_}

    def prefix(self):
        sig = [
            str(self.namespace),
            str(self.name),
            str(self.api_class),
            str(self.version_),
            str(self._prefix_deps(self.run_deps_)),
            str(self._prefix_deps(self.build_deps_)),
            str(self._get_variant_kv()),
            str(self.jpkg_manager.sys_hash)
        ]
        self.prefix_ = hash(";".join(sig))
        return self.prefix_