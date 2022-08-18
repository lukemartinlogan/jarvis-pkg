from abc import ABC,abstractmethod
import os, inspect, pathlib
from jarvis_cd import *
from jarvis_pkg.query.version import Version
from jarvis_pkg.query.query_parser import QueryParser

class Package(ABC):
    def __init__(self):
        self.versions = []
        self.build_dependencies = []
        self.dependencies = []
        self.conflicts = []
        self.patches = []

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

    @abstractmethod
    def _Init(self):
        return

    def version(self, version_string, version_tag=None, help="", url=None,
            git=None, branch=None, commit=None,
            apt=None, yum=None, dnf=None, zypper=None, pacman=None, repo=None, gpg=None,
            pip=None, npm=None):
        if version_tag is None:
            version_tag = version_string

        version_info = {}
        version_info['version'] = Version(version_string)
        version_info['tag'] = version_tag
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
        version_info['repo'] = repo if repo is not None else self.repo
        version_info['gpg'] = gpg if gpg is not None else self.gpg
        version_info['pip'] = pip if pip is not None else self.pip
        version_info['npm'] = npm if npm is not None else self.npm

        if version_info['git'] is not None:
            self.depends_on('git')
        if version_info['npm'] is not None:
            self.depends_on('npm')
        if version_info['pip'] is not None:
            self.depends_on('python')

    def depends_on(self, pkg_query, when=None, time='runtime'):
        if isinstance(pkg_query, str):
            pkg_query = QueryParser().Parse(pkg_query)
        if time == 'runtime':
            self.dependencies.append(pkg_query)
        else:
            self.build_dependencies.append(pkg_query)

    def patch(self, path, when=None):
        self.patches.append(path)

    def conflict(self, query_a, query_b):
        self.conflicts.append(query_a)

    @abstractmethod
    def _FilterDependencies(self, spec):
        pass

    def GetLatestVersion(self, version_string):
        v = Version(version_string)
        latest = max([exact_v for exact_v in self.versions if v.Matches(exact_v)])
        return latest

    def Versions(self):
        return

    def Variants(self):
        return

    def setup_run_environment(self, env):
        env.prepend_path('CPATH', os.path.join(self.prefix, 'include'))
        env.prepend_path('INCLUDE', os.path.join(self.prefix, 'include'))
        env.prepend_path('LIBRARY_PATH', os.path.join(self.prefix, 'lib'))
        env.prepend_path('LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('LD_LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('LD_LIBRARY_PATH', os.path.join(self.prefix, 'lib64'))
        env.prepend_path('PATH', os.path.join(self.prefix, 'bin'))

    def Uninstall(self):
        return