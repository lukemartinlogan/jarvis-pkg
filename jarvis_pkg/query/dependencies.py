from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.query.query_parser import QueryParser
from jarvis_pkg.package.package_spec import PackageSpec
from jarvis_pkg.basic.exception import Error,ErrorCode


class Env:
    def __init__(self):
        self.env = {}
        self.final_env = {}

    def Load(self, pkg_queries):
        for pkg_spec in pkg_queries:
            pkg_name = pkg_spec.GetName()
            if pkg_name not in self.env:
                self.env[pkg_name] = 0
                self.final_env[pkg_name] = PackageSpec(pkg_name)

            #Check if the pkg_spec version conflicts with the currently one
            if not self.final_env[pkg_name].IntersectVersionRange(pkg_spec):
                raise Error(ErrorCode.MULTIPLE_PACKAGE_VERSIONS_LOADED).format(pkg_name)

            #Check if the pkg_spec variants conflict with the current one
            if not self.final_env[pkg_name].IntersectVariants(pkg_spec):
                raise Error(ErrorCode.CONFLICTING_VARIANTS).format(pkg_name)

            #Order
            self.final_env[pkg_name]._max_order(pkg_spec._get_order())

            self.env[pkg_name] += 1

    def Unload(self, pkg_queries):
        for pkg_spec in pkg_queries:
            pkg_name = pkg_spec.GetName()
            self.env[pkg_name] -= 1
            if self.env[pkg_name] <= 0:
                del self.env[pkg_name]

class DependencyGraph:
    def __init__(self, pkg_queries):
        if isinstance(pkg_queries, str):
            pkg_queries = QueryParser().Parse(pkg_queries)
        self.pkg_queries = pkg_queries
        self.pkg_spec = pkg_queries[0]
        self.jpkg_manager = JpkgManager.GetInstance()

    def _PackageInstallSchema(self, pkg_spec, runtime_env, all_env, cycle_set, order = 0, buildtime=False):
        pkg_name = pkg_spec.GetName()
        pkg_klass = self.jpkg_manager._PackageImport(pkg_name)
        if pkg_klass is None:
            raise Error(ErrorCode.UNKOWN_PACKAGE).format(pkg_name)
        pkg = pkg_klass()

        #Verify that there are no cycles
        if pkg_spec.GetName() in cycle_set:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(pkg_spec.GetName())
        cycle_set.add(pkg_spec.GetName())

        #Verify and add this package's build/runtime dependencies
        run_deps = pkg.GetRunDeps(pkg_spec)
        build_deps = pkg.GetBuildDeps(pkg_spec)
        for dep_pkg_spec in run_deps:
            self._PackageInstallSchema(dep_pkg_spec, runtime_env, all_env, cycle_set, order=order + 1)
        for dep_pkg_spec in build_deps:
            self._PackageInstallSchema(dep_pkg_spec, runtime_env, all_env, cycle_set, order=order + 1, buildtime=True)
        pkg_spec._set_order(order)
        pkg_spec._set_pkg(pkg)

        #Check for buildtime and runtime conflicts
        run_deps += [pkg_spec]
        runtime_env.Load(run_deps + build_deps)
        runtime_env.Unload(build_deps)
        if buildtime:
            runtime_env.Unload(run_deps)
        all_env.Load(run_deps+build_deps)
        cycle_set.remove(pkg_spec.GetName())

    def Build(self):
        runtime_env = Env()
        all_env = Env()
        cycle_set = set()
        self._PackageInstallSchema(self.pkg_spec, runtime_env, all_env, cycle_set)
        install_schema = list(all_env.final_env.values())
        install_schema.sort(key=lambda x: x.order)
        install_schema = list(reversed(install_schema))
        return install_schema

    def Install(self, install_schema):
        #Create the installation+src directory

        #Install pkg
        for pkg_spec in install_schema:
            pkg = pkg_spec._get_pkg()
            for phase_name in pkg.phases:
                phase = getattr(pkg, phase_name)
                phase(pkg, pkg_spec)