from jarvis_cd import *
from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.version import Version
from abc import ABC,abstractmethod
import re


class PackageQuery(ABC):


    def __init__(self):
        self.name = self.__class__.__name__
        self.api_class = self.name
        self.namespace = None
        self.is_required = True
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
        self.phases = {}  # install -> (needs_root, [@phase])
        self.phase_confs = {}  # install -> (needs_root, [@conf])
        self.introspect = {} #install -> (needs_root, [@introspect])
        self.install = None

        self.is_null_ = None
        self.prefix_ = None
        self.version_ = None
        self.patches_ = None # [patches]
        self.build_deps_ = None # [pkg]
        self.run_deps_ = None # [pkg]
        self.variants_ = self.variants
        self.install_ = self.install
        self.is_solidified_ = False
        self.is_installed_ = False

        self.url = None
        self.git = None
        self.branch = None
        self.commit = None
        self.pkg_list = None
        self.repo_url = None
        self.gpg = None

        self.variant('prefer_stable', type=bool, default=True,
                     msg="Whether or not to prefer stable versions of packages when processing version ranges.")
        self.variant('introspect', type=bool, default=True,
                     msg="Allow checking if packages are installed externally.")
        self.variant('prefer_scratch', type=bool, default=True,
                     msg="If a package is not installed, whether or not to build from source or"
                         "install using a different package manager")

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
        if pkg.api_class not in deps:
            deps[pkg.api_class] = []
        deps[pkg.api_class].append((pkg, when))
        all_deps.append((pkg, when))

    def depends_on(self, pkgs, when=None, time='run'):
        if isinstance(pkgs, str):
            pkgs = QueryParser(pkgs).parse()
        if isinstance(when, str):
            when = QueryParser(when).parse()
        if not isinstance(pkgs, list):
            pkgs = [pkgs]
        for pkg in pkgs:
            pkg.is_required = (len(pkgs) == 1)
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

    def get_id(self):
        return f"{self.namespace}.{self.name}"

    def get_phases(self):
        return self.phases[self.version_['install']][1]

    def get_versions(self, install):
        vs = []
        for v_info in self.versions:
            if v_info['install'] == install:
                vs.append(v_info)
        return vs

    def get_introspect(self, install):
        if install not in self.introspect:
            return None
        return self.introspect[install][1]

    def get_install_methods(self):
        install = self.install_
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
                self_deps[pkg.api_class][i][0].intersect(pkg)

    def _intersect_id(self, pkg, pkg_id, self_id):
        if pkg_id is not None and pkg_id != self_id:
            self.is_null_ = Error(ErrorCode.DIFFERENT_PKGS).format(
                pkg.namespace, pkg.name,
                self.namespace, self.name
            )

    def intersect(self, pkg):
        if self.is_null():
            return self
        self._intersect_id(pkg, pkg.name, self.name)
        self._intersect_id(pkg, pkg.namespace, self.namespace)
        self._intersect_id(pkg, pkg.api_class, self.api_class)
        self._intersect_id(pkg, pkg.prefix_, self.prefix_)
        if self.is_null():
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

    def is_class(self):
        return self.api_class is not None and self.name is None

    def needs_root(self, v_info):
        return self.phases[v_info['installer']][0]

    """
    Standard Library
    """
    def install_info(self):
        if not self.is_solidified_:
            return None
        return {
            'name': self.name,
            'namespace': self.namespace,
            'version': self.version_,
            'build_deps': self._prefix_deps(self.build_deps_),
            'run_deps': self._prefix_deps(self.run_deps_),
            'variants': self._get_variant_kv(),
        }

    @staticmethod
    def _prefix_pkg_list(dep_list, prefixes):
        for dep in prefixes:
            pkg = Package()
            pkg.prefix_ = dep
            dep_list.append(pkg)

    def from_install_info(self, install_info):
        self.is_installed_ = True
        self.version_ = install_info['version']
        self.versions = [self.version_]
        self.build_deps_ = []
        self._prefix_pkg_list(self.build_deps_, install_info['build_deps'])
        self._prefix_pkg_list(self.run_deps_, install_info['run_deps'])
        self.variants = self.default_variants.copy()
        for key in self.variants.keys():
            self.variants[key]['value'] = install_info['variants'][key]

    def dict(self):
        return {
            'name': self.name,
            'namespace': self.namespace,
            'class': self.api_class,
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

    def copy(self, src_pkg=None):
        if src_pkg is None:
            dst_pkg = self.__class__()
            src_pkg = self
        else:
            dst_pkg = self
        dst_pkg.name = src_pkg.name
        dst_pkg.api_class = src_pkg.api_class
        dst_pkg.namespace = src_pkg.namespace
        dst_pkg.versions = src_pkg.versions.copy()
        dst_pkg.version_set = src_pkg.version_set.copy()
        dst_pkg.all_build_deps = src_pkg.all_build_deps.copy()
        dst_pkg.all_run_deps = src_pkg.all_run_deps.copy()
        dst_pkg.build_deps = src_pkg.build_deps.copy()
        dst_pkg.run_deps = src_pkg.run_deps.copy()
        dst_pkg.patches = src_pkg.patches.copy()
        dst_pkg.default_variants = src_pkg.default_variants.copy()
        dst_pkg.variants = src_pkg.variants.copy()
        dst_pkg.conflicts = src_pkg.conflicts.copy()
        dst_pkg.install = src_pkg.install
        dst_pkg.jpkg_manager = src_pkg.jpkg_manager
        dst_pkg.phases = src_pkg.phases.copy()
        dst_pkg.phase_confs = src_pkg.phase_confs.copy()
        dst_pkg.is_installed_ = src_pkg.is_installed_
        if src_pkg.is_solidified_:
            dst_pkg.is_null_ = src_pkg.is_null_
            dst_pkg.version_ = src_pkg.version_
            dst_pkg.variants_ = src_pkg.variants_
            dst_pkg.install_ = src_pkg.install_
            dst_pkg.patches_ = src_pkg.patches_.copy()
            dst_pkg.build_deps_ = src_pkg.build_deps_.copy()
            dst_pkg.run_deps_ = src_pkg.run_deps_.copy()
            dst_pkg.prefix_ = src_pkg.prefix_
            dst_pkg.is_solidified_ = src_pkg.is_solidified_
        return dst_pkg

    def print(self):
        # Print versions
        print(f"----------{self.namespace}.{self.name}---------")
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
                    print(f"  {pkg.name}@{pkg.version_['version']}")
            if self.run_deps_ is not None and len(self.run_deps_):
                print('RUN DEPS:')
                for pkg in self.run_deps_:
                    print(f"  {pkg.name}@{pkg.version_['version']}")
                print()
        else:
            if self.build_deps is not None and len(self.build_deps):
                print('BUILD DEPS:')
                for pkg,condition in self.all_build_deps:
                    print(f"  {pkg.name}")
            if self.run_deps is not None and len(self.run_deps):
                print('RUN DEPS:')
                for pkg,condition in self.all_run_deps:
                    print(f"  {pkg.name}")
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
