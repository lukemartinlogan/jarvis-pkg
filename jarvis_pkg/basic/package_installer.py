from jarvis_pkg.dependency_graph.dependency_graph import DependencyGraph
from .package_query import PackageQuery
from .package_id import PackageId
from jarvis_cd import *
from jarvis_pkg.basic.jpkg_manager import JpkgManager
import wget


class PackageInstaller:
    instance_ = None

    @staticmethod
    def get_instance():
        if PackageInstaller.instance_ is None:
            PackageInstaller.instance_ = PackageInstaller()
        return PackageInstaller.instance_

    def __init__(self):
        self.jpkg_manager = JpkgManager.get_instance()

    def download(self, candidate):
        candidate.source_dir = os.path.join(self.jpkg_manager.pkg_dirs, candidate.get_unique_name())
        candidate.tmp_source_dir = os.path.join(self.jpkg_manager.tmp_pkg_dirs, candidate.get_unique_name())
        if candidate._version['git'] is not None:
            GitNode(candidate._version['git'], candidate.tmp_source_dir, GitOps.CLONE,
                    branch=candidate._version['branch'],
                    commit=candidate._version['commit']).Run()
        elif candidate._version['url'] is not None:
            wget.download(candidate._version['url'], out=candidate.tmp_source_dir)

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