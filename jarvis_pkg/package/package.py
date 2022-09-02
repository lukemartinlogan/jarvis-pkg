from jarvis_cd import *
from jarvis_pkg import Error, ErrorCode
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.version import Version
from jarvis_pkg.basic.query_parser import QueryParser
import json

class Package(ABC):
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
        self.jpkg_manager = JpkgManager.GetInstance()

        self.version_ = None
        self.patches_ = None # [patches]
        self.build_deps_ = None # [pkg]
        self.run_deps_ = None # [pkg]
        self.is_solidified_ = False

        self.url = None
        self.git = None
        self.branch = None
        self.commit = None
        self.apt = None
        self.yum = None
        self.dnf = None
        self.zypper = None
        self.pacman = None
        self.repo = None
        self.gpg = None
        self.pip = None
        self.npm = None

        self.variant('prefer_stable', type=bool, default=True,
                     msg="Whether or not to prefer stable versions of packages when processing version ranges.")
        self.variant('introspect', type=bool, default=True,
                     msg="Whether or not to check if a package is already installed externally.")
        self.variant('prefer_scratch', type=bool, default=True,
                     msg="If a package is not installed, whether or not to build from source or"
                         "install using a different package manager")

    """
    Package Command Line
    """

    def GetName(self):
        return self.name

    def SetName(self, name):
        self.name = name

    def SetClass(self, pclass):
        self.pclass = pclass

    def GetClass(self):
        return self.pclass

    def IntersectVersionRange(self, min, max):
        if isinstance(min, str):
            min = Version(min)
        if isinstance(max, str):
            max = Version(max)
        self.versions = [v_info for v_info in self.versions if v_info['version'] >= min and v_info['version'] <= max]
        self.version_set = {v_info['version'] for v_info in self.versions}

    def AddBuildDep(self, pkg):
        pass

    def AddRunDep(self, ):
        pass

    def GetBuildDeps(self):
        return self.all_build_deps

    def GetRunDeps(self):
        return self.all_run_deps

    def AddVariant(self, key, value):
        pass

    def _intersect_deps(self, pkg_deps, self_deps):
        for pkg_name, pkg_row in pkg_deps.items():
            for i,(pkg,c) in enumerate(pkg_row):
                self_deps[pkg.GetClass()][i][0].Intersect(pkg)

    def Intersect(self, pkg):
        self.versions = [v_info for v_info in self.versions if v_info['version'] in self.version_set and v_info['version'] in pkg.version_set]
        self.version_set = {v_info['version'] for v_info in self.versions}
        self._intersect_deps(pkg.build_deps, self.build_deps)
        self._intersect_deps(pkg.run_deps, self.run_deps)
        for key,val in pkg.variants.items():
            if key in self.variants:
                if self.variants[key] != val:
                    self.versions = []
                    return
            else:
                self.variants[key] = val
        return self

    def IsNull(self):
        return len(self.versions) == 0

    def IsScratch(self, v_info):
        return v_info['git'] is None or v_info['url'] is None

    def _check_condition(self, cur_env, condition):
        if condition is None:
            return True
        if condition.GetClass() not in cur_env:
            return False
        pkg_set = cur_env[condition.GetClass()]['pkg_set']
        for pkg in pkg_set:
            if not pkg.copy().Intersect(condition).IsNull():
                return True
        return False

    def _find_pkg(self, cur_env, pkg_query):
        pkg_set = cur_env[pkg_query.GetClass()]['pkg_set']
        for pkg in pkg_set:
            if not pkg.copy().Intersect(pkg_query).IsNull():
                return pkg
        return None

    def _solidify_deps(self, cur_env, deps):
        new_deps = []
        for pkg_name, pkg_row in deps.items():
            for pkg, condition in pkg_row:
                if self._check_condition(cur_env, condition):
                    new_deps.append(self._find_pkg(cur_env, pkg))
        return new_deps

    def SolidifyVersion(self):
        #Solidify variants
        for key,val in self.default_variants.items():
            if key not in self.variants:
                self.variants[key] = val

        #Check if a matching package is already installed
        if not self.variants['introspect']:
            self.versions = [v_info for v_info in self.versions if self.IsScratch(v_info)]
        if self.SolidifyFromExisting():
            return

        #Solidify version
        if self.variants['prefer_stable']:
            versions = [v_info for v_info in self.versions if v_info['stable']]
            if len(versions) > 0:
                self.versions = versions
        self.versions.sort(key=lambda x: x['version'])
        self.versions = [self.versions[-1]]

    def SolidifyDeps(self, cur_env):
        # Solidify dependencies
        self.version_ = self.versions[-1]
        self.patches_ = [patch_info for patch_info, condition in self.patches if
                        self._check_condition(cur_env, condition)]
        self.build_deps_ = self._solidify_deps(cur_env, self.build_deps)
        self.run_deps_ = self._solidify_deps(cur_env, self.run_deps)
        self.FilterBuildDeps(self.build_deps_)
        self.FilterRunDeps(self.run_deps_)
        self.FilterPatches(self.patches_)

        # Check conflicts
        for query_a, query_b, msg in self.conflicts:
            p1 = self._check_condition(cur_env, query_a)
            p2 = self._check_condition(cur_env, query_b)
            if p1 and p2:
                raise Error(ErrorCode.CONFLICT).format(msg)

        self.is_solidified_ = True

    def SolidifyFromExisting(self):
        #Check if a package with this version range and these variants are installed
        return False
    def FilterBuildDeps(self, build_deps):
        pass
    def FilterRunDeps(self, run_deps):
        pass
    def FilterPatches(self, patches):
        pass
    def CheckConflicts(self):
        pass

    """
    Package Initialization
    """

    def version(self, version_string, tag=None, help="", url=None,
            git=None, branch=None, commit=None, submodules=False,
            apt=None, yum=None, dnf=None, zypper=None, pacman=None, repo_url=None, gpg=None,
            pip=None, npm=None, stable=True):

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
        version_info['apt'] = apt if apt is not None else self.apt
        version_info['yum'] = yum if yum is not None else self.yum
        version_info['dnf'] = dnf if dnf is not None else self.dnf
        version_info['zypper'] = zypper if zypper is not None else self.zypper
        version_info['pacman'] = pacman if pacman is not None else self.pacman
        version_info['repo_url'] = repo_url if repo_url is not None else self.repo
        version_info['gpg'] = gpg if gpg is not None else self.gpg
        version_info['pip'] = pip if pip is not None else self.pip
        version_info['npm'] = npm if npm is not None else self.npm

        if version_info['git'] is not None:
            self.depends_on('git')
        if version_info['npm'] is not None:
            self.depends_on('npm')
        if version_info['pip'] is not None:
            self.depends_on('python')

        self.versions.append(version_info)
        self.version_set.add(version_info['version'])

    def _depends_on(self, pkg, when, deps, all_deps):
        if pkg.GetClass() not in deps:
            deps[pkg.GetClass()] = []
        deps[pkg.GetClass()].append((pkg, when))
        all_deps.append(pkg)

    def depends_on(self, pkg, when=None, time='runtime'):
        if isinstance(pkg, str):
            pkg = QueryParser().Parse(pkg)
        if isinstance(when, str):
            when = QueryParser().Parse(when)
        if time == 'runtime':
            self._depends_on(pkg, when, self.run_deps, self.all_run_deps)
        else:
            self._depends_on(pkg, when, self.build_deps, self.all_build_deps)

    def variant(self, name, default=None, type=None, choices=None, msg=None):
        variant_info = {
            'value': default,
            'type': type,
            'choices': choices,
            'msg': msg
        }
        self.default_variants[name] = variant_info

    def patch(self, path, when=None):
        self.patches.append((path, when))

    def conflict(self, query_a, query_b):
        self.conflicts.append((query_a, query_b))

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

    def copy(self):
        new_pkg = self.__class__()
        new_pkg.versions = self.versions.copy()
        new_pkg.version_set = self.version_set.copy()
        new_pkg.all_build_deps = self.all_build_deps.copy()
        new_pkg.all_run_deps = self.all_run_deps.copy()
        new_pkg.build_deps = self.build_deps.copy()
        new_pkg.run_deps = self.run_deps.copy()
        new_pkg.patches = self.patches.copy()
        new_pkg.variants = self.variants.copy()
        return new_pkg

    def print(self):
        # Print versions
        print(f"----------{self.GetName()}---------")
        if len(self.versions):
            print('VERSIONS:')
            for version_info in self.versions:
                print(f"  {version_info['version']}")
        if len(self.build_deps_):
            print('BUILD DEPS:')
            for pkg in self.build_deps_:
                print(f"  {pkg.GetName()}@{pkg.version_['version']}")
        if len(self.run_deps_):
            print('RUN DEPS:')
            for pkg in self.run_deps_:
                print(f"  {pkg.GetName()}@{pkg.version_['version']}")
            print()
        if len(self.variants):
            print('VARIANTS:')
            for key,val in self.variants.items():
                print(f"  {key}: {val['value']}")