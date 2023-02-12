from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.query_parser.parse import QueryParser
import pathlib
import os

repo_name = 'dummy_repo'
manifest = JpkgManifestManager.get_instance()
test_dir = pathlib.Path(__file__).parent.resolve()
repo_dir = os.path.join(test_dir, repo_name)


manifest.add_repo(repo_dir)
rows = manifest.list_repo(repo_name)
for repo, cls, name, installer in rows:
    if name == 'a':
        assert(repo == repo_name)
        assert(cls == 'a')
    elif name == 'b':
        assert(repo == repo_name)
        assert(cls == 'b')
    elif name == 'c':
        assert(repo == repo_name)
        assert(cls == 'c')
    elif name == 'd':
        assert(repo == repo_name)
        assert(cls == 'd')
    else:
        raise Exception("Didn't list repo fully")
manifest.print_repo(repo_name)
query = QueryParser("a").first()
assert(query.cls == 'a')
manifest.rm_repo(repo_name)
