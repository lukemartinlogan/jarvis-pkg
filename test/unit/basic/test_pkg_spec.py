from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.package_spec import PackageSpec
from jarvis_pkg.basic.version import Version
import os, pathlib


def test1():
    spec = PackageSpec(PackageQuery("a"))
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("3.1.0"))


def test2():
    spec = PackageSpec(PackageQuery("a@1.1.0"))
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("1.1.0"))


def test3():
    spec = PackageSpec(PackageQuery("a@1.1.0:3.0.0"))
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("3.0.0"))

repo_name = 'dummy_repo'
manifest = JpkgManifestManager.get_instance()
test_dir = pathlib.Path(__file__).parent.resolve()
repo_dir = os.path.join(test_dir, repo_name)
manifest.add_repo(repo_dir)

test3()
