from jarvis_pkg.basic.installer import Installer
from jarvis_pkg.basic.introspectable import Introspectable


class AptPackage(Installer, Introspectable):
    def installer_requirements(self):
        pass

    def get_dependencies(self, spec):
        """
        Get dependencies based on the installation specification.

        :param spec: the set of solidified installers
        :return: PackageQueryList()
        """
        pass

    def load_env(self):
        pass

    def unload_env(self):
        pass

    def introspect(self):
        pass