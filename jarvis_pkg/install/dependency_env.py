from jarvis_pkg.package.package import Package

class DependencyEnvEntry:
    def __init__(self, pkg, order, is_build_dep, parent, conditions):
        self.pkg = pkg
        self.order = order
        self.is_build_dep = is_build_dep
        self.conditions = []
        if parent is not None:
            self.conditions.append(parent)
        if conditions is not None:
            self.conditions += conditions

    def GetName(self):
        return self.pkg.GetClass()

class DependencyEnvRow:
    def __init__(self):
        self.order = 0
        self.name = None
        self.row = []

    def AddEntry(self, pkg, order, is_build_dep, parent, conditions):
        self.row.append(DependencyEnvEntry(pkg, order, is_build_dep, parent, conditions))
        if self.order < order:
            self.order = order
        if self.name is None:
            self.name = pkg.GetClass()

    def GetName(self):
        return self.name

    def list(self):
        return self.row

class DependencyEnv:
    def __init__(self):
        self.nodes = {}

    def AddEntry(self, pkg, order, is_build_dep, parent, conditions):
        if pkg.GetClass() not in self.nodes:
            self.nodes[pkg.GetClass()] = DependencyEnvRow()
        self.nodes[pkg.GetClass()].AddEntry(pkg, order, is_build_dep, parent, conditions)

    def AddRow(self, pkgs, order):
        for pkg in pkgs:
            self.AddEntry(pkg, order, False, None, None)

    def list(self, reverse=False):
        install_schema = list(self.nodes.values())
        install_schema.sort(reverse=reverse,key=lambda row: row.order)
        return install_schema

    def _contains_condition(self, condition):
        if condition is None:
            return True
        if condition.GetClass() not in self.nodes:
            return False
        for dep_entry in self.nodes[condition.GetClass()].row:
            if not dep_entry.pkg.copy().Intersect(condition).IsNull():
                return True
        #print(f"Condition {condition.variants} failed")
        return False

    def __getitem__(self, pkg_name):
        return self.nodes[pkg_name]

    def __contains__(self, key):
        if isinstance(key, Package):
            return self._contains_condition(key)
        if isinstance(key, str):
            return key in self.nodes

