""""
This file builds a solidified set of packages to install based on the
user's query.

1. Determine the set of packages needed to be installed
2.

Solidify root package
- Which version of A will be installed
- Check if a package matching this query is already installed?
- If not, select the latest version
Solidify next-level packages

"""
from .jpkg_manifest_manager import JpkgManifestManager
from .jpkg_install_manager import JpkgInstallManager
from .package_query import PackageQuery


class PackageSpec:
    def __init__(self, pkg_query):
        """
        For a single package, determine the set of packages to install
        and the order to install them.

        :param pkg_query: the primary package to install
        """

        self.manifest = JpkgManifestManager.get_instance()
        self.installed = JpkgInstallManager.get_instance()
        self.install_order = {}
        self.class_queries = {
            pkg_query.cls: [pkg_query]
        }
        self.spec = {}
        self.install_graph = []

        self.get_install_order(pkg_query, 0, {})
        self.install_order = list(self.install_order.items())
        self.install_order.sort(key=lambda x: x[1])
        self.build_spec()
        self.solidify_install_order()

    def get_install_order(self, pkg_query, order, cur_env):
        """
        Determines the order with which package classes should be solidified

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

    def smash_class_row(self, cls):
        """
        Intersects the row of package queries for a particular package class.

        :param cls: the package class to resolve
        :return:
        """
        row = self.class_queries[cls]
        query = PackageQuery(cls=cls)
        for pkg_query in row:
            new_query = query.intersect(pkg_query)
            if new_query.is_null:
                raise Exception(f"Conflicting dependencies: "
                                f"{pkg_query} and {query}")
            query = new_query
        return query

    def build_spec(self):
        """
        Solidifies the set of packages in order

        :return: None
        """

        for cls in self.install_order:
            pkg_query = self.smash_class_row(cls)
            pkg = self.installed.solidify(pkg_query)
            if pkg.is_null:
                pkg = self.manifest.solidify(pkg_query)
            if pkg.is_null:
                raise Exception(f"Couldn't resolve query: {pkg_query}")
            self.spec[cls] = pkg
            dep_queries = pkg.get_dependencies(self.spec)
            for dep_query in dep_queries:
                self.class_queries[dep_query.cls].append(dep_query)

    def solidify_install_order(self):
        """
        Build the order with which packages should be installed in the
        JpkgInstallManager

        :return:
        """
        self.install_order.sort(key=lambda x: x[1], reverse=True)
        for cls in self.install_order:
            self.install_graph.append(self.spec[cls])
