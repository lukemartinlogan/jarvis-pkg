
from jarvis_cd import *
from jarvis_cd.serialize.pickle import PickleFile
from jarvis_cd.util.expand_paths import ExpandPaths

from jarvis_pkg.basic.exception import Error,ErrorCode
from jarvis_pkg.basic.package_id import PackageId
from .jpkg_manager import JpkgManager

import argparse
import pathlib


class ManifestManagerOp(Enum):
    ADD = "add"
    UPDATE = "update"
    DISABLE = "disable"
    REMOVE = "remove"
    LIST = "list"
    PROMOTE = "promote"


class ManifestManager:
    """
    The manifest file contains a table with the following structure:
    REPO_NAME:
        REPO_PATH: /path/to/repo
        ENTRIES: [pkg_id]
        ENABLED: true/false
    """

    instance_ = None

    @staticmethod
    def get_instance():
        if ManifestManager.instance_ is None:
            ManifestManager.instance_ = ManifestManager()
        return ManifestManager.instance_

    def __init__(self):
        self.jpkg = JpkgManager.get_instance()
        manifest = PickleFile(self.jpkg.manifest_path).Load()
        self.repos = manifest['REPOS']
        self.namespace_order = []
        self.pkg_by_name = {}
        self.pkg_by_class = {}
        for namespace in manifest['SEARCH_ORDER']:
            record = self.repos[namespace]
            self._track_namespace(namespace)
            for pkg_id in record['entries']:
                self._track_pkg(pkg_id)

    def save(self):
        manifest = {
            "REPOS": self.repos,
            "SEARCH_ORDER": self.namespace_order
        }
        PickleFile(self.jpkg.manifest_path).Save(manifest)

    def add_repo(self, repo_path, namespace=None):
        if namespace is None:
            namespace = os.path.basename(repo_path)
        if namespace in self.repos:
            print(f"Error: {namespace} already exists")
            return
        record = {
            'path': str(pathlib.Path(repo_path).absolute()),
            'entries': [],
            'enabled': True
        }
        self.repos[namespace] = record
        self._track_namespace(namespace)
        self.update_repo(namespace)

    def disable_repo(self, namespace):
        self.repos[namespace]['enabled'] = False

    def update_repo(self, namespace):
        record = self.repos[namespace]
        root_path = os.path.join(record['path'], namespace)
        record['entries'] = []
        if not os.path.exists(root_path):
            print(f"Update Repo: {root_path} does not exist")
            return
        for pkg_filename in os.listdir(root_path):
            pkg_root_path = pathlib.Path(os.path.join(root_path, str(pkg_filename)))
            if pkg_root_path.is_dir():
                pkg_name = pkg_root_path.name
                pkg_id = PackageId(namespace, None, pkg_name)
                # pkg = self._construct_pkg(pkg_id)
                # pkg_id.cls = pkg.pkg_id.cls

                record['entries'].append(pkg_id)
                self._track_pkg(pkg_id)

    def _track_namespace(self, namespace):
        root_path = self.repos[namespace]['path']
        sys.path.insert(0, root_path)
        self.namespace_order.insert(0, namespace)

    def _untrack_namespace(self, namespace):
        root_path = self.repos[namespace]['path']
        sys.path.remove(root_path)
        self.namespace_order.remove(namespace)
        del self.repos[namespace]

    def _track_pkg(self, pkg_id):
        if pkg_id.name not in self.pkg_by_name:
            self.pkg_by_name[pkg_id.name] = set()
        self.pkg_by_name[pkg_id.name].add(pkg_id)

        if pkg_id.cls not in self.pkg_by_class:
            self.pkg_by_class[pkg_id.cls] = set()
        self.pkg_by_class[pkg_id.cls].add(pkg_id)

    def _untrack_pkg(self, pkg_id):
        if pkg_id.name not in self.pkg_by_name:
            return
        del self.pkg_by_name[pkg_id.name][pkg_id]

        if pkg_id.cls not in self.pkg_by_class:
            return
        del self.pkg_by_class[pkg_id.cls][pkg_id]

    def rm_repo(self, namespace):
        for pkg_id in self.repos[namespace]['entries']:
            self._untrack_pkg(pkg_id)
        self._untrack_namespace(namespace)

    def list_repos(self, namespaces):
        if len(namespaces) == 0:
            if len(self.namespace_order):
                print(" ".join(self.namespace_order))
            else:
                print("No repos currently in Jpkg")
            return
        for namespace in namespaces:
            repo = self.repos[namespace]
            print(f"REPO: {namespace}")
            repo_list = [pkg_id.name for pkg_id in repo['entries']]
            print(" ".join(repo_list))
            print()

    def promote_repos(self, namespaces):
        for namespace in namespaces:
            self.namespace_order.remove(namespace)
        self.namespace_order = namespaces + self.namespace_order

    def find_pkg_ids(self, pkg_name_or_class, namespace=None):
        if pkg_name_or_class in self.pkg_by_class:
            pkg_class = pkg_name_or_class
            if namespace is None:
                return self.pkg_by_class[pkg_class]
            elif namespace in self.pkg_by_class[pkg_class]:
                return set(self.pkg_by_class[pkg_class])
        elif pkg_name_or_class in self.pkg_by_name:
            pkg_name = pkg_name_or_class
            if namespace is None:
                return self.pkg_by_name[pkg_name]
            elif namespace in self.pkg_by_name[pkg_name]:
                return set(self.pkg_by_name[pkg_name])
        return set()

    def find_load_pkgs(self, pkg_name_or_class, namespace=None):
        pkg_id_set = self.find_load_pkgs(pkg_name_or_class, namespace)
        pkg_list = []
        for pkg_id in pkg_id_set:
            if self.repos[pkg_id.namespace]['enabled']:
                pkg_list.append(self._construct_pkg(pkg_id))
        return pkg_list

    @staticmethod
    def _construct_pkg(pkg_id):
        class_name = ToCamelCase(pkg_id.name)
        module = __import__(f"{pkg_id.namespace}.{pkg_id.name}.package",
                               fromlist=[class_name])
        return getattr(module, class_name)()

    """
    Argument parsers
    """

    def parse_args(self, args):
        parser = argparse.ArgumentParser(description='repo')
        parser.prog = "jpkg repo"
        parser.add_argument('op', metavar='operation',
                            type=ManifestManagerOp,
                            choices=list(ManifestManagerOp),
                            help="The manifest operation")
        parser.add_argument('remainder', nargs=argparse.REMAINDER)
        args = parser.parse_args(args)

        if args.op == ManifestManagerOp.ADD:
            args = self.parse_repo_path_args(args.op, args.remainder)
            self.add_repo(args.repo_path, args.namespace)
        elif args.op == ManifestManagerOp.UPDATE:
            args = self.parse_namespace_args(args.op, args.remainder)
            self.update_repo(args.namespace)
        elif args.op == ManifestManagerOp.DISABLE:
            args = self.parse_namespace_args(args.op, args.remainder)
            self.disable_repo(args.namespace)
        elif args.op == ManifestManagerOp.REMOVE:
            args = self.parse_namespace_args(args.op, args.remainder)
            self.rm_repo(args.namespace)
        elif args.op == ManifestManagerOp.LIST:
            args = self.parse_namespace_list_args(args.op, args.remainder)
            self.list_repos(args)
        elif args.op == ManifestManagerOp.PROMOTE:
            args = self.parse_namespace_list_args(args.op, args.remainder)
            self.promote_repos(args)


    def parse_repo_path_args(self, op, args):
        parser = argparse.ArgumentParser(description='repo')
        parser.prog = f"jpkg repo {op.value}"
        parser.add_argument('repo_path', metavar='path',
                            type=str,
                            help="The path to the repo")
        parser.add_argument('-r', metavar='name',
                            dest='namespace',
                            type=str,
                            default=None,
                            help="Set the repo's name")
        return parser.parse_args(args)

    def parse_namespace_args(self, op, args):
        parser = argparse.ArgumentParser(description='repo')
        parser.prog = f"jpkg repo {op.value}"
        parser.add_argument('namespace', metavar='namespace',
                            type=str,
                            help="The path to the repo")
        return parser.parse_args(args)

    def parse_namespace_list_args(self, op, args):
        return args