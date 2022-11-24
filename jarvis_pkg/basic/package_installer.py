from jarvis_pkg.basic.dependency_graph import DependencyGraph
from jarvis_cd import *
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.package_manager import PackageManager
import wget
import shutil


class PackageInstaller:
    instance_ = None

    @staticmethod
    def get_instance():
        if PackageInstaller.instance_ is None:
            PackageInstaller.instance_ = PackageInstaller()
        return PackageInstaller.instance_

    def __init__(self):
        self.jpkg = JpkgManager.get_instance()
        self.package_manager = PackageManager.get_instance()

    def save(self):
        self.package_manager.save()

    @staticmethod
    def download(candidate):
        if candidate.version_['git'] is not None:
            GitNode(candidate.version_['git'],
                    candidate.source_dir, GitOps.CLONE,
                    branch=candidate.version_['branch'],
                    commit=candidate.version_['commit']).Run()
        elif candidate.version_['url'] is not None:
            wget.download(candidate.version_['url'],
                          out=candidate.source_dir)

    @staticmethod
    def download_update(candidate):
        if candidate.version_['git'] is not None:
            GitNode(candidate.version_['git'],
                    candidate.source_dir, GitOps.UPDATE,
                    branch=candidate.version_['branch'],
                    commit=candidate.version_['commit']).Run()

    def install(self, pkg_list):
        graph = DependencyGraph()
        candidates = graph.build(pkg_list)
        for candidate in candidates:
            if candidate.is_installed:
                continue
            candidate.install_dir = os.path.join(self.jpkg.pkg_dirs,
                                                 candidate.get_unique_name())
            candidate.source_dir = os.path.join(candidate.install_dir, 'src')
            self.download(candidate)
            for phase in candidate.get_phases():
                phase(candidate)
            self.package_manager.register(candidate)

    def update(self, pkg_list):
        for pkg in pkg_list:
            matches = self.package_manager.query(pkg)
            if len(matches) > 1:
                print("Can't upate more than one candidate!")
                print(matches)
                exit(1)
            if len(matches) == 0:
                print("No packages match update query")
                exit(1)
            ipkg = matches[0]
            self.download_update(ipkg)
            for phase in ipkg.get_phases():
                phase(ipkg)

    def uninstall(self, pkg_list):
        for pkg in pkg_list:
            matches = self.package_manager.query(pkg)
            if len(matches) > 1:
                print("Can't uninstall more than one candidate!")
                print(matches)
                exit(1)
            if len(matches) == 0:
                print("No packages match uninstall query")
                exit(1)
            ipkg = matches[0]
            self.package_manager.unregister(ipkg)
            shutil.rmtree(ipkg.install_dir)
