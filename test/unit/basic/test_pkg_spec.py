from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.package_spec import PackageSpec
from jarvis_pkg.basic.version import Version
import os, pathlib


def test1():
    spec = PackageSpec("a")
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("3.1.0"))


def test2():
    spec = PackageSpec("a@1.1.0")
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("1.1.0"))


def test3():
    spec = PackageSpec("a@1.1.0:3.0.0")
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("3.0.0"))


def test4():
    spec = PackageSpec("a@1.1.0:3.0.0 a=3")
    pkg = spec.install_graph[0]
    assert(pkg.name == 'a')
    assert(pkg.version_ == Version("3.0.0"))
    assert(pkg.variants_['a'] == 3)


def test5():
    spec = PackageSpec("c")
    assert(spec[0].name == 'a')
    assert(spec[1].name == 'b')
    assert(spec[2].name == 'c')
    assert(spec['a'].version_ == Version("3.0.0"))
    assert(spec['b'].version_ == Version("3.0.0"))
    assert(spec['c'].version_ == Version("3.0.0"))


def test6():
    spec = PackageSpec("c@2.0.0 % b@1.0.0")
    assert (spec[0].name == 'a')
    assert (spec[1].name == 'b')
    assert (spec[2].name == 'c')
    assert (spec['a'].version_ == Version("2.0.0"))
    assert (spec['b'].version_ == Version("1.0.0"))
    assert (spec['c'].version_ == Version("2.0.0"))


repo_name = 'dummy_repo'
manifest = JpkgManifestManager.get_instance()
test_dir = pathlib.Path(__file__).parent.resolve()
repo_dir = os.path.join(test_dir, repo_name)
manifest.add_repo(repo_dir)

test1()
test2()
test3()
test4()
test5()
test6()
