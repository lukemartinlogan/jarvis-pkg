"""
This file is an index to all important paths in jpkg

1. manifests: the set of all installers
2. installed: the set of all installed installers
3. setup.log: records the installation process to avoid repetition in
case of failure
"""

import os, sys
import pathlib
import pandas as pd
from .jpkg_manager import JpkgManager
from jarvis_pkg.util.system_info import SystemInfo
from jarvis_pkg.query_parser.parse import QueryParser
from jarvis_pkg.basic.jpkg_manifest_manager import JpkgManifestManager
from .introspectable import Introspectable
from tabulate import tabulate


class JpkgInstallManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgInstallManager.instance_ is None:
            JpkgInstallManager.instance_ = JpkgInstallManager()
        return JpkgInstallManager.instance_

    def __init__(self):
        self.columns = [
            'repo', 'cls', 'name', 'installer', 'version',
            'sysinfo', 'uuid', 'ref', 'pkg_state'
        ]
        self.df = pd.DataFrame(columns=self.columns)
        self.jpkg = JpkgManager.get_instance()
        self.manifest = JpkgManifestManager.get_instance()
        if os.path.exists(self.jpkg.installed_path):
            self.df = pd.read_pickle(self.jpkg.installed_path).reset_index(
                drop=True)

    def _register_package(self, pkg):
        if pkg.is_installed:
            df = self.df
            df.loc[df.uuid == pkg.uuid_, 'ref'] += 1
        else:
            pkg.is_installed = True
            record = [[pkg.repo, pkg.cls, pkg.name, pkg.installer, pkg.version_,
                       SystemInfo.get_instance(), pkg.uuid_,
                       1, pkg.get_state()]]
            self.df = pd.concat([self.df,
                                 pd.DataFrame(record, columns=self.columns)])

    def _get_refcnt(self, pkg):
        df = self.df
        return list(df[df.uuid == pkg.uuid_]['ref'])[0]

    def _unregister_package(self, pkg, primary=True,
                            full_uninstall=False):
        if pkg.is_installed:
            df = self.df
            df.loc[df.uuid == pkg.uuid_, 'ref'] -= 1
            ref = list(df.loc[df.uuid == pkg.uuid_, 'ref'])[0]
            if ref <= 0:
                if primary or full_uninstall:
                    df = self.df
                    self.df.drop(df[df.uuid == pkg.uuid_].index,
                                 inplace=True)
        for dep_pkg in pkg.dependencies_.values():
            self._unregister_package(dep_pkg, False, full_uninstall)

    def introspect(self):
        pkg_root = os.path.join(self.jpkg.jpkg_root, 'jarvs_pkg', 'installers')
        pkg_types = os.listdir(pkg_root)
        for pkg_type in pkg_types:
            pkg = __import__(f"jarvis_pkg.installers.{pkg_type}")(True)
            if isinstance(pkg, Introspectable):
                queries = pkg.introspect()
                for pkg_query in queries:
                    matches = self.manifest.match(pkg_query)
                    for pkg in matches:
                        pkg.make_uuid(self.df['uuid'])
                        self._register_package(pkg)

    def install_spec(self, pkg_spec):
        main_pkg = pkg_spec.install_graph[-1]
        if main_pkg.is_installed:
            print(f"{main_pkg.name}-{main_pkg.uuid_} is already installed")
            return
        for pkg in pkg_spec.install_graph:
            pkg.make_uuid(self.df['uuid'])
            phases = pkg.install_phases
            for phase in phases:
                try:
                    phase(pkg)
                except Exception as e:
                    print(e)
                    return
        for pkg in pkg_spec.install_graph:
            self._register_package(pkg)

    def uninstall_package(self, pkg_query):
        if isinstance(pkg_query, str):
            pkg_query = QueryParser(pkg_query).first()
        matches = self.match(pkg_query)
        if len(matches) > 1:
            raise Exception(f"Multiple installers match the query: {pkg_query}")
        if len(matches) == 0:
            raise Exception(f"No installers match the query: {pkg_query}")
        pkg = matches[0]
        if self._get_refcnt(pkg) > 1:
            raise Exception(f"Cannot uninstall {pkg.name} since it's a "
                            f"dependency of another package")
        self._unregister_package(pkg)
        phases = pkg.uninstall_phases
        for phase in phases:
            phase(pkg)

    def list(self, pkg_query=None):
        """
        List all package names which match the query
        [name] [version] [repo] [installer] [path]

        :param pkg_query:
        :return:
        """
        matches = self.match(pkg_query)
        headers = ['Class', 'Name', 'Version', 'Repo', 'Installer', 'Path']
        table = []
        for pkg in matches:
            table.append([
                pkg.cls, pkg.name, pkg.version_, pkg.repo,
                pkg.installer, pkg.install_path
            ])
        print(tabulate(table, headers=headers))

    def info(self, pkg_query):
        pass

    def match(self, pkg_query):
        """
        Find all installers matching this query

        :param pkg_query: the query to match
        :return:
        """
        if pkg_query is None:
            pkg_states = list(self.df['pkg_state'])
            pkgs = [self.manifest.load_pkg_from_state(pkg_state)
             for pkg_state in pkg_states]
            return pkgs
        df = self.df
        if isinstance(pkg_query, str):
            pkg_query = QueryParser(pkg_query).first()
        if pkg_query.repo is not None:
            df = df[df.repo == pkg_query.repo]
        if pkg_query.cls is not None:
            df = df[df.cls == pkg_query.cls]
        if pkg_query.name is not None:
            df = df[df.name == pkg_query.name]
        if pkg_query.versions is not None:
            for rng in pkg_query.versions:
                df = df[(df.version >= rng[0]) &
                        (df.version <= rng[1])]
        df = df[df.sysinfo == SystemInfo.get_instance()]
        if len(df) == 0:
            return []
        pkgs = list(df['pkg_state'])
        matches = []
        for pkg_state in pkgs:
            pkg = self.manifest.load_pkg_from_state(pkg_state)
            new_pkg = pkg.from_query(pkg_query)
            new_pkg.set_state(pkg_state)
            new_pkg.is_installed = True
            if new_pkg is not None:
                matches.append(new_pkg)
        return matches

    def solidify(self, pkg_query):
        """
        Find an existing package which matches this query

        :param pkg_query: the query to match
        :return:
        """
        matches = self.match(pkg_query)
        if len(matches):
            matches.sort(key=lambda x: x.version_,
                         reverse=True)
            return matches[0]
        else:
            return None

    def exists(self, pkg_query):
        return len(self.match(pkg_query)) != 0

    def save(self):
        self.df.to_pickle(self.jpkg.installed_path)
