from jarvis_cd import *
from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.version import Version
from jarvis_pkg.basic.query_parser import QueryParser
from abc import ABC,abstractmethod
import re


def modify_phases(self, class_f,
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
        def _phase_impl(*args, **kwargs):
            self = args[0]
            modify_phases(self, class_f,
                          install, needs_root,
                          args, kwargs, self.phases)
        return _phase_impl
    return wrap


def conf(install=None):
    def wrap(class_f):
        def _phase_impl(*args, **kwargs):
            self = args[0]
            modify_phases(self, class_f,
                          install, False,
                          args, kwargs, self.phase_confs)
        return _phase_impl
    return wrap


class Package(ABC):
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
        self.name = self.__class__.__name__
        self.pclass = self.name
        self.namespace = None
        self.versions = []   # [version_info_dict]
        self.version_set = set()  # set of versions
        self.all_build_deps = []
        self.all_run_deps = []
        self.build_deps = {}  # pkg_name -> [(pkg, condition)]
        self.run_deps = {}  # pkg_name -> [(pkg, condition)]
        self.patches = []  # [(patch, condition)]
        self.default_variants = {}  # variant_name -> (variant_dict, condition)
        self.variants = {}  # variant_name -> variant_info_dict
        self.conflicts = []  # [(condition, condition, msg)]
        self.phases = {}  # install -> (needs_root, list of phases)
        self.phase_confs = {}  # install -> (needs_root, list of phase configure options)
        self.install = self.default_installer()
        self.jpkg_manager = JpkgManager.GetInstance()

        self.is_null_ = None
        self.version_ = None
        self.patches_ = None # [patches]
        self.build_deps_ = None # [pkg]
        self.run_deps_ = None # [pkg]
        self.is_solidified_ = False

        self.url = None
        self.git = None
        self.branch = None
        self.commit = None
        self.pkg_list = None
        self.repo_url = None
        self.gpg = None

        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_phase_impl':
                        value(self, in_init=True)

        self.variant('prefer_stable', type=bool, default=True,
                     msg="Whether or not to prefer stable versions of packages when processing version ranges.")
        self.variant('introspect', type=bool, default=True,
                     msg="Whether or not to check if a package is already installed externally.")
        self.variant('prefer_scratch', type=bool, default=True,
                     msg="If a package is not installed, whether or not to build from source or"
                         "install using a different package manager")
        self.define_versions()

    """
    Package Definition
    """

    def define_versions(self):
        pass

    def define_deps(self):
        for version_info in self.versions:
            if version_info['git'] is not None:
                self.depends_on('git')
            if version_info['npm'] is not None:
                self.depends_on('npm')
            if version_info['pip'] is not None:
                self.depends_on('python')

    def define_conflicts(self):
        pass

    def version(self, version_string, tag=None, help="", url=None,
                git=None, branch=None, commit=None, submodules=False,
                pkg_list=None, repo_url=None, gpg=None,
                stable=True, distro=None, install=None):
        if tag is None:
            tag = version_string
        version_info = {}
        version_info['version'] = Version(version_string)
        version_info['stable'] = stable
        version_info['tag'] = tag
        version_info['help'] = help
        version_info['url'] = url if url is not None else self.url
        version_info['git'] = git if git is not None else self.git
        version_info['branch'] = branch if branch is not None else self.branch
        version_info['commit'] = commit if commit is not None else self.commit
        version_info['submodules'] = submodules
        version_info['distro'] = distro
        version_info['pkg_list'] = pkg_list if pkg_list is not None else self.pkg_list
        version_info['repo_url'] = repo_url if repo_url is not None else self.repo_url
        version_info['gpg'] = gpg if gpg is not None else self.gpg
        version_info['install'] = install if install is not None else self.install

        if len(self.phases) != 0 or version_info['install'] is not None:
            if version_info['install'] not in self.phases:
                raise Error(ErrorCode.INSTALLER_UNDEFINED).format(
                    version_info['install'], self.namespace, self.name)

        self.versions.append(version_info)
        self.version_set.add(version_info['version'])

    def variant(self, name, default=None, type=None, choices=None, msg=None):
        variant_info = {
            'value': default,
            'type': type,
            'choices': choices,
            'msg': msg
        }
        self.default_variants[name] = variant_info

    def _depends_on(self, pkg, when, deps, all_deps):
        if pkg.get_class() not in deps:
            deps[pkg.get_class()] = []
        deps[pkg.get_class()].append((pkg, when))
        all_deps.append((pkg, when))

    def depends_on(self, pkg, when=None, time='run'):
        if isinstance(pkg, str):
            pkg = QueryParser(pkg).parse()
        if isinstance(when, str):
            when = QueryParser(when).parse()
        if time == 'run':
            self._depends_on(pkg, when, self.run_deps, self.all_run_deps)
        elif time == 'build':
            self._depends_on(pkg, when, self.build_deps, self.all_build_deps)

    def patch(self, path, when=None):
        if isinstance(when, str):
            when = QueryParser(when).parse()
        self.patches.append((path, when))

    def conflict(self, query_a, query_b):
        if isinstance(query_a, str):
            query_a = QueryParser(query_a).parse()
        if isinstance(query_b, str):
            query_b = QueryParser(query_b).parse()
        self.conflicts.append((query_a, query_b))

    """
    Package Modification
    """

    def set_namespace(self, namespace):
        self.namespace = namespace

    def get_namespace(self):
        return self.namespace

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def set_class(self, pclass):
        self.pclass = pclass

    def get_class(self):
        return self.pclass

    def get_phases(self):
        return self.phases[self.version_['install']][1]

    def get_phase_methods(self):
        install = self.version_['install']
        if len(self.phases) == 0 and install is None:
            return []
        methods = self.phases[install][1].copy()
        if install in self.phase_confs:
            methods += self.phase_confs[install][1]
        return methods

    def intersect_version_range(self, min, max):
        if isinstance(min, str):
            min = Version(min)
        if isinstance(max, str):
            max = Version(max)
        self.versions = [v_info for v_info in self.versions if v_info['version'] >= min and v_info['version'] <= max]
        self.version_set = {v_info['version'] for v_info in self.versions}

    def get_build_deps(self):
        return self.all_build_deps

    def get_run_deps(self):
        return self.all_run_deps

    def set_variant(self, key, value):
        if key not in self.variants:
            self.variants[key] = self.default_variants.copy()
        self.variants[key]['value'] = value

    def variant_eq(self, key, value):
        if key not in self.variants:
            return False
        return self.variants[key]['value'] == value

    def variant_true(self, key):
        return self.variant_eq(key, True)

    def variant_false(self, key):
        return self.variant_eq(key, False)

    @staticmethod
    def _intersect_deps(pkg_deps, self_deps):
        for pkg_name, pkg_row in pkg_deps.items():
            for i,(pkg,c) in enumerate(pkg_row):
                self_deps[pkg.get_class()][i][0].intersect(pkg)

    def intersect(self, pkg):
        if self.is_null_ is not None:
            return self
        self.versions = [v_info for v_info in self.versions if v_info['version'] in self.version_set and v_info['version'] in pkg.version_set]
        if len(self.versions) == 0:
            self.is_null_ = Error(ErrorCode.CONFLICTING_VERSIONS).format(self.get_name())
            return self
        self.version_set = {v_info['version'] for v_info in self.versions}
        self._intersect_deps(pkg.build_deps, self.build_deps)
        self._intersect_deps(pkg.run_deps, self.run_deps)
        for key,val in pkg.variants.items():
            if key in self.variants:
                if self.variants[key]['value'] != val['value']:
                    self.is_null_ = Error(ErrorCode.CONFLICTING_VARIANTS).format(key, self.variants[key], val)
                    return self
            else:
                self.variants[key] = val
        return self

    def is_null(self):
        return self.is_null_ is not None

    def needs_root(self, v_info):
        return self.phases[v_info['installer']][0]

    @staticmethod
    def _solidify_deps(cur_env, deps):
        new_deps = []
        for pkg_name, pkg_row in deps.items():
            for pkg, condition in pkg_row:
                if condition in cur_env:
                    new_deps.append(cur_env.find_pkg(cur_env, pkg))
        return new_deps

    def solidify_version(self):
        #Solidify variants
        for key,val in self.default_variants.items():
            if key not in self.variants:
                self.variants[key] = val

        #Check if a matching package is already installed
        if not self.variants['introspect']:
            self.versions = [v_info for v_info in self.versions if self.needs_root(v_info)]
        if self.solidify_from_existing():
            return

        #Solidify version
        if self.variants['prefer_stable']:
            versions = [v_info for v_info in self.versions if v_info['stable']]
            if len(versions) > 0:
                self.versions = versions
        self.versions.sort(key=lambda x: x['version'])
        self.versions = [self.versions[-1]]

    def solidify_deps(self, cur_env):
        # Solidify dependencies
        self.version_ = self.versions[-1]
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

        # Set phase definitions
        for method in self.get_phase_methods():
            setattr(self, method.__name__, method)

        self.is_solidified_ = True

    def solidify_from_existing(self):
        #Check if a package with this version range and these variants are installed
        return False
    def filter_build_deps(self, build_deps):
        pass
    def filter_run_deps(self, run_deps):
        pass
    def filter_patches(self, patches):
        pass
    def check_conflicts(self):
        pass

    """
    Standard Library
    """
    def dict(self):
        return {
            'versions': self.versions,
            'build_deps': self.build_deps,
            'run_deps': self.run_deps,
            'variants': self.variants
        }

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return str(self.dict())

    def __repr__(self):
        return str(self.dict())

    def copy(self, new_pkg=None):
        if new_pkg is None:
            new_pkg = self.__class__()

        new_pkg.name = self.name
        new_pkg.pclass = self.pclass
        new_pkg.namespace = self.namespace
        new_pkg.versions = self.versions.copy()
        new_pkg.version_set = self.version_set.copy()
        new_pkg.all_build_deps = self.all_build_deps.copy()
        new_pkg.all_run_deps = self.all_run_deps.copy()
        new_pkg.build_deps = self.build_deps.copy()
        new_pkg.run_deps = self.run_deps.copy()
        new_pkg.patches = self.patches.copy()
        new_pkg.default_variants = self.default_variants.copy()
        new_pkg.variants = self.variants.copy()
        new_pkg.conflicts = self.conflicts.copy()
        new_pkg.install = self.install
        new_pkg.jpkg_manager = self.jpkg_manager
        new_pkg.phases = self.phases.copy()
        new_pkg.phase_confs = self.phase_confs.copy()
        if self.is_solidified_:
            new_pkg.is_null_ = self.is_null_
            new_pkg.version_ = self.version_
            new_pkg.patches_ = self.patches_.copy()
            new_pkg.build_deps_ = self.build_deps_.copy()
            new_pkg.run_deps_ = self.run_deps_.copy()
            new_pkg.is_solidified_ = self.is_solidified_
        return new_pkg

    def print(self):
        # Print versions
        print(f"----------{self.get_namespace()}.{self.get_name()}---------")
        if len(self.versions):
            print('VERSIONS:')
            for version_info in self.versions:
                print(f"  {version_info['version']} ({version_info['install']})")
        if len(self.variants):
            print('VARIANTS:')
            for key,val in self.variants.items():
                print(f"  {key}: {val['value']}")
        if self.is_solidified_:
            if self.build_deps_ is not None and len(self.build_deps_):
                print('BUILD DEPS:')
                for pkg in self.build_deps_:
                    print(f"  {pkg.get_name()}@{pkg.version_['version']}")
            if self.run_deps_ is not None and len(self.run_deps_):
                print('RUN DEPS:')
                for pkg in self.run_deps_:
                    print(f"  {pkg.get_name()}@{pkg.version_['version']}")
                print()
        else:
            if self.build_deps is not None and len(self.build_deps):
                print('BUILD DEPS:')
                for pkg,condition in self.all_build_deps:
                    print(f"  {pkg.get_name()}")
            if self.run_deps is not None and len(self.run_deps):
                print('RUN DEPS:')
                for pkg,condition in self.all_run_deps:
                    print(f"  {pkg.get_name()}")
                print()

    """
    Other
    """

    def setup_run_environment(self, env):
        env.prepend_path('CPATH', os.path.join(self.prefix, 'include'))
        env.prepend_path('INCLUDE', os.path.join(self.prefix, 'include'))
        env.prepend_path('LIBRARY_PATH', os.path.join(self.prefix, 'lib'))
        env.prepend_path('LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('LD_LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('LD_LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('PATH', os.path.join(self.prefix, 'bin'))

    def _register_repo_rhel(self, repo_url, gpg):
        self.download(repo_url, 'beegfs.repo')
        self.copy('beegfs.repo', '/etc/yum/repos.d', sudo=True)
