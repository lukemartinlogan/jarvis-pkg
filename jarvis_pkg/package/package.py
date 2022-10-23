from jarvis_cd import *
from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.version import Version
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.query_parser import QueryParser
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


class Package:
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
        self.jpkg = JpkgManager.get_instance()
        self._load_superclass_decorators()
        self.versions = []
        self.variants = []
        self.dependencies = []
        self.patches = []
        self.conflicts = []

    def version(self, vstr, pkg_list=None, url=None, git=None, gpg=None):
        pass

    def depends_on(self, pkg_query):
        if isinstance(pkg_query, str):
            pkg = None  # TODO(llogan): parse into a query
        elif isinstance(pkg_query, PackageQuery):
            pkg = pkg_query
        else:
            raise Error(ErrorCode.INVALID_PARAMETER).format(type(pkg_query))
        self.dependencies.append(pkg)

    def variant(self, variant_name, default=None):
        pass

    def patch(self):
        pass

    def conflict(self):
        pass

    def _load_superclass_decorators(self):
        self.phases = {} # pkg_name -> (needs_root, [phase_functions])
        self.phase_confs = {} # pkg_name -> (needs_root, [conf_functions])
        self.introspect = {} # pkg_name -> (needs_root, [introspect_functions])
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_jpkg_decor_impl':
                        value(self, in_init=True)
