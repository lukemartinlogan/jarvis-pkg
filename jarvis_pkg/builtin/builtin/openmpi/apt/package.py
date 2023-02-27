from jarvis_pkg.installers.apt import AptInstaller
from jarvis_pkg.basic.package import Package, install, uninstall
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.package_query_list import PackageQueryList
from jarvis_pkg.basic.version import Version
from itertools import product
import re


class OpenmpiPackage(AptInstaller, Package):
    def define_class(self):
        self.classify('mpi')

    def define_versions(self):
        self.version('inf')
        for i, j, k in product(range(4), range(10), range(10)):
            self.version(f"{i}.{j}.{k}")

    def define_variants(self):
        pass

    def define_dependencies(self):
        pass

    def get_dependencies(self, spec):
        return PackageQueryList()

    def load_env(self):
        pass

    def unload_env(self):
        pass

    def get_apt_packages(self):
        if self.version_ == Version('inf'):
            return [
                'libopenmpi3', 'openmpi-bin'
            ]
        else:
            return

    def introspect(self, state):
        return self._introspect_ubuntu20(state)

    def _introspect_ubuntu20(self, state):
        if 'libopenmpi3' not in state:
            return None
        if 'openmpi-bin' not in state:
            return None
        pkg_query = PackageQuery(name='openmpi')
        ompi_state = state['libopenmpi3']
        version = ompi_state['version']
        match = re.match('(\d+\.\d+.\d+)-\w+', version)
        if match is None:
            return
        pkg_query.set_version(match.group(1))
        return pkg_query
