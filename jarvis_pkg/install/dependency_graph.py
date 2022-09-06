from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.exception import Error,ErrorCode
from .dependency_env import DepEnv


class DependencyGraph:
    def __init__(self):
        self.jpkg_manager = JpkgManager.get_instance()
        self.install_schema = None

    def _get_install_environment(self, root_pkg, env, order=0, build_dep=False, parent=None, conditions=None, cycle_set=None):
        if cycle_set is None:
            cycle_set = set()
        if root_pkg.get_class() not in cycle_set:
            cycle_set.add(root_pkg.get_class())
        else:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(root_pkg.get_class())
        root_pkg.define_deps()
        for dep_pkg,dep_conditions in root_pkg.get_build_deps():
            self._get_install_environment(dep_pkg, env, order=order+1, build_dep=True*build_dep, parent=root_pkg, conditions=dep_conditions)
        for dep_pkg,dep_conditions in root_pkg.get_run_deps():
            self._get_install_environment(dep_pkg, env, order=order+1, parent=root_pkg, conditions=dep_conditions)
        env.add_entry(root_pkg, order, build_dep, parent, conditions)

    def build(self, pkg_list):
        env = DepEnv()
        for root_pkg in pkg_list:
            self._get_install_environment(root_pkg, env)
        ordered_rows = env.list()

        final_env = DepEnv()
        for dep_class in ordered_rows:
            for dep_row in dep_class.list():
                row = dep_row.row

                """
                Filter out different versions of the current package based on various conditions:
                Whether or not the parent was selected and if the parent's conditions are met.
                """
                row_sub = []
                for dep_entry in row:
                    rets = [c in final_env for c in dep_entry.conditions]
                    if not all(rets):
                        continue
                    row_sub.append(dep_entry)
                row = row_sub
                if len(row) == 0:
                    print("All conditions failed")
                    continue
                build_row = [dep_entry for dep_entry in row if dep_entry.is_build_dep]
                run_row = [dep_entry for dep_entry in row if not dep_entry.is_build_dep]
                order = max(row, key=lambda dep_entry: dep_entry.order).order

                """
                intersect all runtime deps
                """
                final_pkg_set = [] #[pkg]
                if len(run_row):
                    final_run_pkg = run_row[0].pkg.copy()
                    for dep_entry in run_row[1:]:
                        final_run_pkg.intersect(dep_entry.pkg)
                        if final_run_pkg.is_null():
                            raise final_run_pkg.is_null_
                    final_pkg_set.append(final_run_pkg)

                """
                If row has both buildtime and runtime, ensure they don't conflict 
                """
                if len(build_row) and len(run_row):
                    final_run_pkg = final_pkg_set[0]
                    run_order_max = max(run_row, key=lambda dep_entry: dep_entry.order).order
                    for build_dep_entry in build_row:
                        if build_dep_entry.order <= run_order_max:
                            conflict = build_dep_entry.pkg.copy().intersect(final_run_pkg)
                            if conflict.is_null():
                                raise conflict.is_null_

                """
                Integrate buildtime deps
                """
                if len(final_pkg_set) == 0:
                    final_pkg_set.append(build_row[0].pkg.copy())
                    build_row = build_row[1:]
                for dep_entry in build_row:
                    for i,final_build_pkg in enumerate(final_pkg_set):
                        final_build_pkg = final_build_pkg.copy()
                        final_build_pkg.intersect(dep_entry.pkg)
                        if final_build_pkg.is_null():
                            final_pkg_set.append(dep_entry.pkg.copy())
                        else:
                            final_pkg_set[i] = final_build_pkg

                """
                Solidify package version + variants
                """
                final_env.add_row(final_pkg_set, order)
                for pkg in final_pkg_set:
                    pkg.solidify_version()

        install_schema = final_env.schema(reverse=True)
        for pkg in install_schema:
            pkg.solidify_deps(final_env)
        self.install_schema = install_schema #Ordered list of packages to install
        return self

    def print(self):
        for pkg in self.install_schema:
            pkg.print()

    def install(self):
        for pkg in self.install_schema:
            phases = pkg.get_phases()
            for phase in phases:
                phase_fun = getattr(pkg, phase)
                phase_fun(pkg)

