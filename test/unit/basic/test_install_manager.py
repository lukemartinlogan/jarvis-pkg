from jarvis_pkg.basic.jpkg_install_manager import JpkgInstallManager
from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.package_spec import PackageSpec
import sys, os
import pathlib


def test1():
    installer = JpkgInstallManager.get_instance()
    spec = PackageSpec("a@1.0.0")
    assert (len(spec['a'].install_phases) == 2)
    assert (len(spec['a'].uninstall_phases) == 2)

def test2():
    installer = JpkgInstallManager.get_instance()
    spec = PackageSpec("a@1.0.0")
    installer.install_spec(PackageSpec("a@1.0.0"))
    assert(installer.exists("a@1.0.0"))


repo_name = 'dummy_repo'
manifest = JpkgManifestManager.get_instance()
test_dir = pathlib.Path(__file__).parent.resolve()
repo_dir = os.path.join(test_dir, repo_name)
manifest.add_repo(repo_dir)

test1()