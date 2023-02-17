from jarvis_pkg.basic.installer import Installer
from jarvis_pkg.basic.introspectable import Introspectable
from jarvis_pkg.util.exec import Exec
import re


class AptInstaller(Installer, Introspectable):
    def installer_requirements(self):
        return True

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

    def get_introspect_state(self):
        apt_list = Exec("apt list --installed")
        lines = apt_list.stdout.splitlines()
        state = {}
        for line in lines:
            toks = re.split('[/\s]', line)
            if len(toks) != 5:
                continue
            name = toks[0]
            state[name] = {
                'repo': toks[1],
                'version': toks[2],
                'arch': toks[3],
                'install': toks[4]
            }
        return state
