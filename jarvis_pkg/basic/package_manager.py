from jarvis_cd import *
from jarvis_cd.serialize.pickle import PickleFile
from jarvis_cd.util.expand_paths import ExpandPaths

from jarvis_pkg.basic.exception import Error,ErrorCode
from jarvis_pkg.basic.package_id import PackageId
from .jpkg_manager import JpkgManager
import pandas as pd

import argparse
import pathlib


class PackageManagerOp(Enum):
    LIST = "list"
    INFO = "info"
    VERSIONS = "versions"


class PackageManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if PackageManager.instance_ is None:
            PackageManager.instance_ = PackageManager()
        return PackageManager.instance_

    def __init__(self):
        self.jpkg = JpkgManager.get_instance()
        self.df = PickleFile(self.jpkg.installed_path).Load()
        pass

    def save(self):
        PickleFile(self.jpkg.installed_path).Save(self.df)

    def inc_refcnt(self, pkg):
        for dep in pkg.dependencies_.values():
            dep_entry = self._query(dep)
            if len(dep_entry) > 1:
                print("FATAL: Stored dependency does not match specific package")
                exit(1)
            dep_entry['ref'] += 1
            self.inc_refcnt(dep)

    def dec_refcnt(self, pkg):
        for dep in pkg.dependencies_.values():
            dep_entry = self._query(dep)
            if len(dep_entry) > 1:
                print("FATAL: Stored dependency does not match specific package")
                exit(1)
            dep_entry['ref'] -= 1
            self.dec_refcnt(dep)

    def register(self, pkg):
        pkg.is_installed = True
        record = pd.DataFrame.from_records([{
            'uuid': pkg.get_unique_name(),
            'namespace': pkg.pkg_id.namespace,
            'cls': pkg.pkg_id.cls,
            'name': pkg.pkg_id.name,
            'version': pkg.version_,
            'pkg': pkg.to_query(),
            'ref': 1
        }], index=None)
        self.inc_refcnt(pkg)
        self.df = pd.concat([self.df, record])

    def unregister(self, pkg):
        df = self._query(pkg)
        if len(df) == 1 and list(df['ref'])[0] == 1:
            self.dec_refcnt(pkg)
            self.df = self.df.drop(df.index)
        else:
            print("Cannot unregister multiple packages at once!")
            print(df)

    def _query(self, pkg_query):
        df = self.df
        pkg_id = pkg_query.pkg_id
        if pkg_id.namespace is not None:
            df = df[df.namespace == pkg_id.namespace]
        if pkg_id.cls is not None:
            df = df[df.name == pkg_id.name]
        if pkg_id.name is not None:
            df = df[df.name == pkg_id.name]
        return df

    def query(self, pkg_query):
        df = self._query(pkg_query)
        return list(df['pkg'])

    def find_by_name(self, pkg_name_dict):
        pkgs = []
        for uuid in pkg_name_dict.values():
            uuid_set = self.df[self.df.uuid == uuid]
            if len(uuid_set) > 1:
                print("FATAL: More than one package has the same uuid?")
                exit(1)
            if len(uuid_set) == 0:
                print("FATAL: No package has the same uuid?")
                exit(1)
            pkgs += list(uuid_set['pkg'])
        return pkgs

    def is_installed(self, pkg_query):
        return len(self.query(pkg_query)) > 0

    def list(self, pkg_list):
        return

    def info(self, pkg_list):
        return

    def versions(self, pkg_list):
        return

    def introspect(self, pkg_query):
        pass

    """
    Argument Parser
    """

    def parse_args(self, args):
        parser = argparse.ArgumentParser(description='repo')
        parser.prog = "jpkg repo"
        parser.add_argument('op', metavar='operation',
                            type=PackageManagerOp,
                            choices=list(PackageManagerOp),
                            help="The manifest operation")
        parser.add_argument('remainder', nargs=argparse.REMAINDER)
        args = parser.parse_args(args)

        if args.op == PackageManagerOp.LIST:
            args = self.parse_namespace_list_args(args.op, args.remainder)
            self.list(args)
        elif args.op == PackageManagerOp.INFO:
            args = self.parse_namespace_list_args(args.op, args.remainder)
            self.info(args)
        elif args.op == PackageManagerOp.VERSIONS:
            args = self.parse_namespace_list_args(args.op, args.remainder)
            self.versions(args)

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
