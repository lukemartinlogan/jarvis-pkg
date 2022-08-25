from jarvis_pkg.query.version import Version

class PackageSpec:
    def __init__(self, pkg_name=None):
        self.spec = {
            'pkg_name': pkg_name,
            'version_range': None,
            'variants': {},
            'build_deps': {},
            'runtime_deps': {}
        }
        self.order = 0

    def _set_order(self, order):
        self.order = order
    def _max_order(self, order):
        self.order = max(self.order, order)
    def _get_order(self):
        return self.order

    def SetVersionRange(self, version):
        if isinstance(version, str):
            version = Version(version)
        self.spec['version_range'] = [version,version]

    def GetVersionRange(self):
        return self.spec['version_range']

    def IntersectVersionRange(self, pkg_query):
        if pkg_query.spec['version_range'] is None:
            return True
        if self.spec['version_range'] is None:
            self.spec['version_range'] = pkg_query.spec['version_range']
            return True
        vmin = max([self.spec['version_range'][0], pkg_query.spec['version_range'][0]])
        vmax = max([self.spec['version_range'][1], pkg_query.spec['version_range'][1]])
        if vmin <= vmax:
            self.spec['version_range'] = [vmin, vmax]
            return True
        else:
            self.spec['version_range'] = None
            return False

    def IntersectVariants(self, pkg_query):
        for variant,val in pkg_query.spec['variants'].items():
            variants = self.spec['variants']
            if variant in variants and variants[variant] != val:
                return False
            variants[variant] = val
        return True

    def AddBuildDependency(self, pkg_dep):
        self.spec['build_deps'][pkg_dep.GetName()] = pkg_dep

    def GetBuildDependency(self, pkg_name):
        return self.spec['build_deps'][pkg_name]

    def AddRuntimeDependency(self, pkg_dep):
        self.spec['runtime_deps'][pkg_dep.GetName()] = pkg_dep

    def SetVariant(self, key, val):
        self.spec['variants'][key] = val

    def GetName(self):
        return self.spec['pkg_name']

    def __hash__(self):
        return hash(str(self.spec))

    def __str__(self):
        return str(self.spec)

    def __repr__(self):
        return str(self.spec)