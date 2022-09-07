from jarvis_cd import *
from jarvis_cd.serialize.yaml_file import YAMLFile
from jarvis_cd.util.expand_paths import ExpandPaths
from jarvis_pkg.install.dependency_env import DepEnv
from jarvis_pkg.package.package_query import PackageQuery
from jarvis_pkg.basic.exception import Error,ErrorCode

class JpkgManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgManager.instance_ is None:
            JpkgManager.instance_ = JpkgManager()
        return JpkgManager.instance_

    def __init__(self):
        self.jpkg_root = os.path.dirname(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
        self.repos_file = os.path.join(self.jpkg_root, 'repos.yaml')
        self.install_file = os.path.join(self.jpkg_root, 'install.yaml')
        if os.path.exists(self.repos_file):
            self.repos = YAMLFile(self.repos_file).Load()
            self.repos = ExpandPaths(self.repos).Run()
            self.namespace_order = self.repos['NAMESPACE']
        else:
            self.repos = {'REPOS': {}, 'NAMESPACE': []}
            self.namespace_order = []
            YAMLFile(self.repos_file).Save(self.repos)
        if os.path.exists(self.install_file):
            self.installs = YAMLFile(self.install_file).Load()
        else:
            self.installs = []
        self.installer_root = os.path.join(self.jpkg_root, 'jpkg_installers')
        self._init_repos()
        self._init_installed()
        self.sys_hash = hash(SystemInfoNode().Run())

    def _init_repos(self):
        self.repo_env = DepEnv()
        for namespace,repo in self.repos['REPOS'].items():
            for pkg_name in repo['pkgs']:
                pkg = PackageQuery()
                pkg.namespace = namespace
                pkg.name = pkg_name
                self.repo_env.add_entry(pkg)

    def _init_installed(self):
        self.install_env = DepEnv()
        for install in self.installs:
            name,namespace = install['namespace'],install['name']
            matching = self.find_imports(namespace, name)
            if len(matching) == 0:
                raise Error(ErrorCode.CANT_FIND_INSTALLED_PKG).format(
                    namespace, name)
            pkg_class = matching[0]
            pkg = pkg_class()
            pkg.from_install_info(install)
            self.install_env.add_entry(pkg)

    def add_repo(self, repo_dir, namespace=None):
        if namespace is None:
            namespace = os.path.basename(repo_dir)
        repo = {
            'path': repo_dir,
            'pkgs': []
        }
        self.repos['REPOS'][namespace] = repo
        for pkg_name in os.listdir(repo_dir):
            pkg_class = self._package_import(namespace,pkg_name)
            pkg = pkg_class()
            repo['pkgs'].append((pkg.api_class,pkg_name))
        YAMLFile(self.repos_file).Save(self.repos)

    def rm_repo(self, repo_name):
        pass

    def _package_import(self, namespace, name):
        import_str = f"{namespace}.{name}"
        path = self.repos['REPOS'][namespace]['path']
        class_name = ToCamelCase(name)
        sys.path.insert(0, path)
        module = __import__(f"{import_str}.package", fromlist=[class_name])
        sys.path.pop(0)
        return getattr(module, class_name)

    def find_imports(self, namespace, name):
        name = ToSnakeCase(name)
        pkg = Package()
        pkg.namespace = namespace
        pkg.name = name
        matches = self.repo_env.find(pkg)
        if len(matches) == 0:
            pkg.name = None
            pkg.api_class = name
        matches = self.repo_env.find(pkg)
        if len(matches) == 0:
            return matches
        imports = []
        for match in matches:
            imports.append(self._package_import(
                match.namespace, match.name
            ))
        return imports
