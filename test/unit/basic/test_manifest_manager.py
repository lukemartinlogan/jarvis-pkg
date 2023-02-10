from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.package_query import PackageQuery
import pathlib
import os

repo_name = 'dummy_repo'
manifest = JpkgManifestManager.get_instance()
test_dir = pathlib.Path(__file__).parent.resolve()
repo_dir = os.path.join(test_dir, repo_name)


manifest.add_repo(repo_dir)
rows = manifest.list_repo(repo_name)
for repo, cls, name, installer in rows:
    if name == 'A':
        assert(repo == repo_name)
        assert(cls == 'A')
    elif name == 'B':
        assert(repo == repo_name)
        assert(cls == 'B')
    elif name == 'C':
        assert(repo == repo_name)
        assert(cls == 'C')
    elif name == 'D':
        assert(repo == repo_name)
        assert(cls == 'D')
    else:
        raise Exception("Didn't list repo fully")
manifest.print_repo(repo_name)
query = PackageQuery("A")
assert(query.cls == 'A')
manifest.rm_repo(repo_name)
