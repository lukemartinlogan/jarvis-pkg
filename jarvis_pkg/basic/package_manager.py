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

    def register(self, pkg):
        record = pd.Series({
            'namespace': pkg.pkg_id.namespace,
            'cls': pkg.pkg_id.cls,
            'name': pkg.pkg_id.name,
            'version': pkg._version,
            'pkg': pkg,
        })
        self.df = pd.concat([self.df, record])

    def unregister(self, pkg):
        return

    def list(self, pkg_list):
        return

    def info(self, pkg_list):
        return

    def versions(self, pkg_list):
        return

    def is_installed(self, pkg_query):
        return False

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
