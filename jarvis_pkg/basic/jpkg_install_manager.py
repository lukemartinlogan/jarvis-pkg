"""
This file is an index to all important paths in jpkg

1. manifests: the set of all packages
2. installed: the set of all installed packages
3. setup.log: records the installation process to avoid repetition in
case of failure
"""

import os, sys
import pathlib
import pandas as pd
from .jpkg_manager import JpkgManager
from jarvis_pkg.util.system_info import SystemInfo


class JpkgInstallManager:
    instance_ = None

    @staticmethod
    def get_instance():
        if JpkgInstallManager.instance_ is None:
            JpkgInstallManager.instance_ = JpkgInstallManager()
        return JpkgInstallManager.instance_

    def __init__(self):
        # TODO(llogan): add sysinfo to the dataframe filter
        self.columns = [
            'repo', 'cls', 'name', 'version',
            'sysinfo', 'uuid', 'ref', 'pkg'
        ]
        self.df = pd.DataFrame(columns=self.columns)
        self.jpkg = JpkgManager.get_instance()
        if os.path.exists(self.jpkg.installed_path):
            self.df = pd.load_parquet(self.jpkg.installed_path)

    def register_package(self, pkg):
        if pkg.is_installed:
            df = self.df
            df[df.uuid == pkg.uuid_]['ref'] += 1
        else:
            pkg.is_installed = True
            self.df += pd.DataFrame(
                [[pkg.repo, pkg.cls, pkg.name, pkg.version_,
                  SystemInfo.get_instance(), pkg.uuid_,
                  0, pkg]],
                columns=self.columns)

    def get_refcnt(self, pkg):
        df = self.df
        return list(df[df.uuid == pkg.uuid_]['ref'])[0]

    def unregister_package(self, pkg):
        if pkg.is_installed:
            df = self.df
            df[df.uuid == pkg.uuid_]['ref'] -= 1
        for dep_pkg in pkg.dependencies_:
            self.unregister_package(dep_pkg)

    def install_spec(self, pkg_spec):
        for pkg in pkg_spec.install_graph:
            phases = pkg.install_phases
            for phase in phases:
                try:
                    phase(pkg, pkg_spec.spec)
                except Exception as e:
                    print(e)
                    return
        for pkg in pkg_spec.install_order:
            self.register_package(pkg)

    def uninstall_package(self, pkg):
        if self.get_refcnt(pkg) > 1:
            raise Exception(f"Cannot uninstall {pkg.name} since it's a "
                            f"dependency of another package")
        self.unregister_package(pkg)
        phases = pkg.uninstall_phases
        for phase in phases:
            phase(pkg)

    def list(self, pkg_query):
        pass

    def info(self, pkg_query):
        pass

    def match(self, pkg_query):
        """
        Find all packages matching this query

        :param pkg_query: the query to match
        :return:
        """
        df = self.df
        if pkg_query.repo is not None:
            df = df[df.repo == pkg_query.repo]
        if pkg_query.cls is not None:
            df = df[df.cls == pkg_query.cls]
        if pkg_query.name is not None:
            df = df[df.name == pkg_query.name]
        if pkg_query.versions is not None:
            for rng in pkg_query.versions:
                df = df[(rng[0] <= df.version) &
                        (df.version <= rng[1])]
        df = df[df.sysinfo == SystemInfo.get_instance()]
        if len(df) == 0:
            return []
        pkgs = list(df['pkg'])
        matches = []
        for pkg in pkgs:
            new_pkg = pkg.from_query(pkg_query)
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

    def save(self):
        self.df.to_parquet(self.jpkg.installed_path)
