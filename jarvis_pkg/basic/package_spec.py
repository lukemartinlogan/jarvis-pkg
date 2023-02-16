""""
This file builds a solidified set of installers to install based on the
user's query.

1. Determine the set of installers needed to be installed
2.

Solidify root package
- Which version of a will be installed
- Check if a package matching this query is already installed?
- If not, select the latest version
Solidify next-level installers

"""
from jarvis_pkg.query_parser.parse import QueryParser
from .jpkg_manifest_manager import JpkgManifestManager
from .jpkg_install_manager import JpkgInstallManager
from .package_query import PackageQuery


class PackageSpec:
    def __init__(self, pkg_query):
        """
        For a single package, determine the set of installers to install
        and the order to install them.

        :param pkg_query: the primary package to install
        """
        if isinstance(pkg_query, str):
            pkg_query = QueryParser(pkg_query).first()
        self.manifest = JpkgManifestManager.get_instance()
        self.installed = JpkgInstallManager.get_instance()
        self.install_order = {}
        self.spec = {}
        self.install_graph = []

        # Determine the order with which to solidify installers
        self.get_install_order(pkg_query, 0, {})
        self.install_order = list(self.install_order.items())
        self.install_order.sort(key=lambda x: x[1])

        # Initialize the map of pkg_class -> [pkg_query]
        self.class_queries = {}
        for key, order in self.install_order:
            self.class_queries[key] = []
        self.class_queries[pkg_query.cls].append(pkg_query)
        for dep_cls, dep_query in pkg_query.dependencies.items():
            self.class_queries[dep_cls].append(dep_query)
        self.build_spec()

        # Solidify the order with which installers are installed
        self.solidify_install_order()

    def get_install_order(self, pkg_query, order, cur_env):
        """
        Determines the order with which package classes should be solidified.
        Modifies self.install_order

        :param pkg_query: the query being inducted into self.class_queries
        :param order: the current depth of the dependency tree
        :param cur_env: the current set of dependencies
        :return:
        """
        pkgs = self.manifest.match(pkg_query)
        if len(pkgs) == 0:
            raise Exception(f"Couldn't resolve query: {pkg_query}")
        self.install_order[pkg_query.cls] = order
        if pkg_query.cls in cur_env:
            raise Exception(f"Cyclic dependency: {pkg_query.cls}")
        cur_env[pkg_query.cls] = True
        for pkg in pkgs:
            cur_env[pkg.cls] = True
            for dep_query in pkg.all_dependencies:
                self.get_install_order(dep_query, order + 1, cur_env)
        del cur_env[pkg_query.cls]

    def build_spec(self):
        """
        Solidifies the set of installers in order.
        Modifies self.spec and self.class_queries

        :return: None
        """
        for cls, order in self.install_order:
            pkg_query = self.smash_class_row(cls)
            pkg = self.installed.solidify(pkg_query)
            if pkg is None:
                pkg = self.manifest.solidify(pkg_query)
            if pkg is None:
                raise Exception(f"Couldn't resolve query: {pkg_query}")
            self.spec[cls] = pkg
            dep_queries = pkg.get_dependencies(self.spec).to_list()
            for dep_query in dep_queries:
                self.class_queries[dep_query.cls].append(dep_query)

    def smash_class_row(self, cls):
        """
        Intersects the row of package queries for a particular package class.

        :param cls: the package class to resolve
        :return:
        """
        row = self.class_queries[cls]
        query = PackageQuery(cls)
        for pkg_query in row:
            new_query = query.intersect(pkg_query)
            if new_query.is_null:
                raise Exception(f"Conflicting dependencies: "
                                f"{pkg_query} and {query}")
            query = new_query
        return query

    def solidify_install_order(self):
        """
        Build the order with which installers should be installed in the
        JpkgInstallManager. Also ensure that each package stores
        reference to each package it depends on.

        :return:
        """
        self.install_order.sort(key=lambda x: x[1], reverse=True)
        for cls, order in self.install_order:
            pkg = self.spec[cls]
            for dep_query in pkg.all_dependencies:
                dep_cls = dep_query.cls
                pkg.dependencies_[dep_cls] = self.spec[dep_cls]
            self.install_graph.append(pkg)

    def __getitem__(self, key):
        """
        Get a package from the spec.
        If key is an integer, will return the the i'th package in the
        self.install_graph. Otherwise, will return the package corresponding
        to key in self.spec.

        :param key:
        :return:
        """
        if isinstance(key, int):
            return self.install_graph[key]
        else:
            return self.spec[key]
