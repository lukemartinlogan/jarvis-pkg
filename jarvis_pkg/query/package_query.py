from jarvis_pkg.query.version import Version

class PackageQuery:
    def __init__(self, pkg_name=None):
        self.pkg_query = {
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
        self.pkg_query['version_range'] = [version,version]

    def GetVersionRange(self):
        return self.pkg_query['version_range']

    def IntersectVersionRange(self, pkg_query):
        vmin = max([self.pkg_query['version_range'][0], pkg_query['version_range'][0]])
        vmax = max([self.pkg_query['version_range'][1], pkg_query['version_range'][1]])
        if vmin <= vmax:
            self.pkg_query['version_range'] = [vmin, vmax]
            return True
        else:
            self.pkg_query['version_range'] = None
            return False

    def IntersectVariants(self, pkg_query):
        for variant,val in pkg_query['variants'].items():
            variants = self.pkg_query['variants']
            if variant in variants and variants[variant] != val:
                return False
            variants[variant] = val
        return True

    def AddBuildDependency(self, pkg_dep):
        self.pkg_query['build_deps'][pkg_dep.GetName()] = pkg_dep

    def GetBuildDependency(self, pkg_name):
        return self.pkg_query['build_deps'][pkg_name]

    def AddRuntimeDependency(self, pkg_dep):
        self.pkg_query['runtime_deps'][pkg_dep.GetName()] = pkg_dep

    def SetVariant(self, key, val):
        self.pkg_query['variants'][key] = val

    def __hash__(self):
        return hash(str(self.pkg_query))

    def __str__(self):
        return str(self.pkg_query)

    def __repr__(self):
        return str(self.pkg_query)