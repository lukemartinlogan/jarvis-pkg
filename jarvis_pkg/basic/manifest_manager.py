
from jarvis_cd import *
from jarvis_cd.serialize.pickle import PickleFile
from jarvis_cd.util.expand_paths import ExpandPaths

from jarvis_pkg.basic.exception import Error,ErrorCode
from jarvis_pkg.basic.package_id import PackageId
from .jpkg_manager import JpkgManager

import argparse
import pathlib
import pandas as pd

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
        self.pkg_df = manifest['PKG_LIST']
        self.metadata = manifest['METADATA']
        self.namespace_order = []
        for namespace in manifest['SEARCH_ORDER']:
            self._track_namespace(namespace)

    def save(self):
        manifest = {
            "PKG_LIST": self.pkg_df,
            'METADATA': self.metadata,
            "SEARCH_ORDER": self.namespace_order
        }
        PickleFile(self.jpkg.manifest_path).Save(manifest)

    def add_repo(self, repo_path, namespace=None):
        if namespace is None:
            namespace = os.path.basename(repo_path)
        if namespace in self.metadata:
            print(f"Error: {namespace} already exists")
            return
        record = {
            'path': str(pathlib.Path(repo_path).absolute()),
            'enabled': True
        }
        self.metadata[namespace] = record
        self._track_namespace(namespace)
        self.update_repo(namespace)

    def disable_repo(self, namespace):
        self.metadata[namespace]['enabled'] = False

    def update_repo(self, namespace):
        record = self.metadata[namespace]
        root_path = os.path.join(record['path'], namespace)
        if not os.path.exists(root_path):
            print(f"Update Repo: {root_path} does not exist")
            return

        pkg_list = []
        for pkg_filename in os.listdir(root_path):
            pkg_root_path = pathlib.Path(os.path.join(root_path, str(pkg_filename)))
            if pkg_root_path.is_dir():
                pkg_name = pkg_root_path.name
                pkg_id = PackageId(namespace, None, pkg_name)
                # pkg = self._construct_pkg(pkg_id)
                # pkg_id.cls = pkg.pkg_id.cls
                pkg_list.append(pkg_id.dict())
        self.pkg_df = pd.concat([pd.DataFrame(pkg_list), self.pkg_df])

    def rm_repo(self, namespace):
        df = self.pkg_df
        self._untrack_namespace(namespace)
        self.pkg_df.drop(df[df.namespace == namespace].index, inplace=True)
        del self.metadata[namespace]

    def list_repos(self, namespaces):
        if len(namespaces) == 0:
            if len(self.namespace_order):
                print(" ".join(self.namespace_order))
            else:
                print("No repos currently in Jpkg")
            return
        for namespace in namespaces:
            print(f"REPO: {namespace}")
            df = self.pkg_df
            print(df[df.namespace == namespace][['cls', 'name']].to_string())

    def promote_repos(self, namespaces):
        for namespace in namespaces:
            self.namespace_order.remove(namespace)
        self.namespace_order = namespaces + self.namespace_order

    def find_pkg_ids(self, pkg_name_or_class, namespace=None):
        df = self.pkg_df
        if pkg_name_or_class in df['cls']:
            pkg_class = pkg_name_or_class
            if namespace is None:
                return set(df[df.cls == pkg_class])
            elif namespace in self.metadata:
                return set(df[(df.namespace == namespace) &
                              (df.cls == pkg_class)])
        elif pkg_name_or_class in self.pkg_df['name']:
            pkg_name = pkg_name_or_class
            if namespace is None:
                return set(df[df.name == pkg_name])
            elif namespace in self.metadata:
                return set(df[(df.namespace == namespace) &
                              (df.name == pkg_name)])
        return set()

    def find_load_pkgs(self, pkg_name_or_class, namespace=None):
        pkg_id_set = self.find_load_pkgs(pkg_name_or_class, namespace)
        pkg_list = []
        for pkg_id in pkg_id_set:
            if self.metadata[pkg_id.namespace]['enabled']:
                pkg_list.append(self._construct_pkg(pkg_id))
        return pkg_list

    @staticmethod
    def _construct_pkg(pkg_id):
        class_name = ToCamelCase(pkg_id.name)
        module = __import__(f"{pkg_id.namespace}.{pkg_id.name}.package",
                               fromlist=[class_name])
        return getattr(module, class_name)()

    def _track_namespace(self, namespace):
        root_path = self.metadata[namespace]['path']
        sys.path.insert(0, root_path)
        self.namespace_order.insert(0, namespace)

    def _untrack_namespace(self, namespace):
        root_path = self.metadata[namespace]['path']
        sys.path.remove(root_path)
        self.namespace_order.remove(namespace)

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