from jarvis_pkg.package.package_query import PackageQuery


class DepEnvEntry:
    def __init__(self, pkg, order, is_build_dep, parent, conditions):
        self.pkg = pkg
        self.order = order
        self.is_build_dep = is_build_dep
        self.conditions = []
        if parent is not None:
            self.conditions.append(parent)
        if conditions is not None:
            self.conditions += conditions


class DepEnvRow:
    def __init__(self):
        self.name = None
        self.is_required = False
        self.row = []

    def add_entry(self, pkg, order, is_build_dep, parent, conditions):
        self.row.append(DepEnvEntry(pkg, order, is_build_dep,
                                    parent, conditions))
        self.name = pkg.api_class
        if pkg.is_required:
            self.is_required = True

    def find(self, pkg_query):
        matching = []
        for dep_pkg in self.row:
            if not dep_pkg.pkg.copy().intersect(pkg_query).is_null():
                matching.append(dep_pkg)
        return matching


class DepEnvClass:
    def __init__(self, api_class):
        self.order = 0
        self.api_class = api_class
        self.map = {} #(namespace,name) -> row

    def add_entry(self, pkg, order, is_build_dep, parent, conditions):
        id = pkg.get_id()
        if id not in self.map:
            self.map[id] = DepEnvRow()
        self.map[id].add_entry(pkg, order, is_build_dep, parent, conditions)
        if self.order < order:
            self.order = order

    def find(self, pkg_query):
        matching = []
        for dep_row in self.map.values():
            matching += dep_row.find(pkg_query)
        return matching

    def list(self):
        return list(self.map.values())

    def _contains_condition(self, condition):
        if condition is None:
            return True
        if condition.api_class not in self.nodes:
            return False
        return condition in self.nodes[condition.api_class]


class DepEnv:
    def __init__(self):
        self.nodes = {}

    def add_entry(self, pkg, order=0, is_build_dep=False, parent=None, conditions=None):
        if pkg.api_class not in self.nodes:
            self.nodes[pkg.api_class] = DepEnvClass(pkg.api_class)
        self.nodes[pkg.api_class].add_entry(pkg, order, is_build_dep, parent, conditions)

    def add_row(self, pkgs, order):
        for pkg in pkgs:
            self.add_entry(pkg, order, False, None, None)

    def list(self, reverse=False):
        install_schema = list(self.nodes.values())
        install_schema.sort(reverse=reverse,key=lambda row: row.order)
        return install_schema

    def schema(self, reverse=False):
        install_schema = self.list(reverse)
        ordered_pkgs = []
        for dep_class in install_schema:
            for dep_row in dep_class.list():
                for dep_pkg in dep_row.row:
                    ordered_pkgs.append(dep_pkg.pkg)
        return ordered_pkgs

    def find(self, pkg_query):
        matching = []
        if pkg_query is None:
            return matching
        if pkg_query.api_class not in self.nodes:
            return matching
        matching = self.nodes[pkg_query.api_class].find(pkg_query)
        return matching

    def __getitem__(self, pkg_name):
        return self.nodes[pkg_name]

    def __contains__(self, key):
        if isinstance(key, PackageQuery):
            return len(self.find(key)) > 0
        if isinstance(key, str):
            return key in self.nodes

