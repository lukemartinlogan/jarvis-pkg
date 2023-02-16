from abc import ABC, abstractmethod


def install(method):
    def _install_impl(*args, **kwargs):
        method(*args, **kwargs)
    return _install_impl


def uninstall(method):
    def _uninstall_impl(*args, **kwargs):
        method(*args, **kwargs)
    return _uninstall_impl


class Installer(ABC):
    def __init__(self):
        self.install_phases = []
        self.uninstall_phases = []

    def _parse_decorators(self):
        for superclass in self.__class__.__mro__:
            for value in superclass.__dict__.values():
                if callable(value):
                    if value.__name__ == '_install_impl':
                        self.install_phases.append(value)
                    if value.__name__ == '_uninstall_impl':
                        self.uninstall_phases.append(value)

    @abstractmethod
    def installer_requirements(self):
        """
        Any requirements of the system in order to use a package.
        Called during "match" in ManifestManager.

        :return: True if the system matches requirements. False otherwise.
        """
        pass
