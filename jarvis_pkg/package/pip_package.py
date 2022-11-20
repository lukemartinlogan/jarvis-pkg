from .package import Package, phase, conf, introspect
from jarvis_cd import *


class PipPackage(Package):
    @conf(install="pip")
    def pip_conf(self):
        return {}

    @phase(install="pip", needs_root=False)
    def pip_phase(self):
        pip_conf = self.pip_conf(self)
        reqs = os.path.join(self.tmp_source_dir, 'requirements.txt')
        install_cmd_toks = [
            f"python3 -m pip install",
            f"-e" if 'dev' in pip_conf else None,
            f"{self.tmp_source_dir}" if 'git' in self.version_ else pip_conf['pkg_name'],
            f"-r {reqs}" if "requirements" in pip_conf else None,
        ]
        install_cmd = [tok for tok in install_cmd_toks if tok is not None]
        install_cmd = " ".join(install_cmd)
        ExecNode(install_cmd).Run()

