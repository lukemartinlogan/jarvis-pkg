from jarvis_pkg.dependency_graph.dependency_graph import DependencyGraph
from .package_query import PackageQuery
from .package_id import PackageId
from jarvis_cd import *
from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.package_manager import PackageManager
import wget


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

    def download(self, candidate):
        candidate.source_dir = os.path.join(self.jpkg.pkg_dirs,
                                            candidate.get_unique_name())
        candidate.tmp_source_dir = os.path.join(self.jpkg.tmp_pkg_dirs,
                                                candidate.get_unique_name())
        if candidate.version_['git'] is not None:
            GitNode(candidate.version_['git'],
                    candidate.tmp_source_dir, GitOps.CLONE,
                    branch=candidate.version_['branch'],
                    commit=candidate.version_['commit']).Run()
        elif candidate.version_['url'] is not None:
            wget.download(candidate.version_['url'],
                          out=candidate.tmp_source_dir)

    def install(self):
        graph = DependencyGraph()
        query = PackageQuery()
        query.pkg_id = PackageId(None, None, 'jarvis_cd')
        candidates = graph.build([query])
        for candidate in candidates:
            if candidate.is_installed:
                continue
            self.download(candidate)
            for phase in candidate.get_phases():
                phase(candidate)
            self.package_manager.register(candidate)
