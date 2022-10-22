"""
This file is the index to all primary locations of content in Jarvis

Jarvis State:
- manifest.yaml: the set of all packages that can be installed
- installed.yaml: the set of all packages currently installed
"""

from jarvis_cd import *
from jarvis_cd.serialize.pickle import PickleFile
from jarvis_cd.util.expand_paths import ExpandPaths
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
        self.jpkg_state_path = os.path.join(self.jpkg_root, '.jpkg_state')
        if not os.path.exists(self.jpkg_state_path):
            os.mkdir(self.jpkg_state_path)
        self._init_manifest_path()
        self._init_installed_path()
        self.sys_hash = hash(SystemInfoNode().Run())

    def _init_manifest_path(self):
        self.manifest_path = os.path.join(self.jpkg_state_path, "manifest.pkl")
        if not os.path.exists(self.manifest_path):
            default = {'REPOS': {}, 'SEARCH_ORDER': []}
            PickleFile(self.manifest_path).Save(default)
            return

    def _init_installed_path(self):
        self.installed_path = os.path.join(self.jpkg_state_path,
                                           "installed.pkl")
        if not os.path.exists(self.installed_path):
            default = []
            PickleFile(self.installed_path).Save(default)
            return
