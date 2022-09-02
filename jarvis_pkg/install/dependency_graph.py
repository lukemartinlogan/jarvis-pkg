from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.exception import Error,ErrorCode
from .dependency_env import DependencyEnv

class DependencyGraph:
    def __init__(self):
        self.jpkg_manager = JpkgManager.GetInstance()

    def _GetInstallEnvironment(self, root_pkg, env, order=0, build_dep=False, parent=None, conditions=None, cycle_set=None):
        if cycle_set is None:
            cycle_set = set()
        if root_pkg.GetClass() not in cycle_set:
            cycle_set.add(root_pkg.GetClass())
        else:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(root_pkg.GetClass())
        for pkg,conditions in root_pkg.GetBuildDeps():
            self._GetInstallEnvironment(pkg, env, order=order+1, build_dep=True*build_dep, parent=root_pkg, conditions=conditions)
        for pkg,conditions in root_pkg.GetRunDeps():
            self._GetInstallEnvironment(pkg, env, order=order+1, parent=root_pkg, conditions=conditions)
        env.AddEntry(root_pkg, order, build_dep, parent, conditions)

    def Build(self, pkg_list):
        env = DependencyEnv()
        for root_pkg in pkg_list:
            self._GetInstallEnvironment(root_pkg, env)
        ordered_rows = env.list()

        final_env = DependencyEnv()
        for dep_row in ordered_rows:
            row = dep_row.list()
            print(dep_row.GetName())

            """
            Filter out different versions of the current package based on various conditions:
            Whether or not the parent was selected and if the parent's conditions are met.
            """
            row_sub = []
            for dep_entry in row:
                if dep_entry.GetName() == 'B':
                    for c in dep_entry.conditions:
                        c.print()
                    exit()
                rets = [c in final_env for c in dep_entry.conditions]
                if not all(rets):
                    continue
                row_sub.append(dep_entry)
            row = row_sub
            if len(row) == 0:
                continue
            build_row = [dep_entry for dep_entry in row if dep_entry.is_build_dep]
            run_row = [dep_entry for dep_entry in row if not dep_entry.is_build_dep]
            order = max(row, key=lambda dep_entry: dep_entry.order).order

            """
            Intersect all runtime deps
            """
            final_pkg_set = [] #[pkg]
            if len(run_row):
                final_run_pkg = run_row[0].pkg.copy()
                for dep_entry in run_row[1:]:
                    final_run_pkg.Intersect(dep_entry.pkg)
                    if final_run_pkg.IsNull():
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
                        conflict = build_dep_entry.pkg.copy().Intersect(final_run_pkg)
                        if conflict.IsNull():
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
                    final_build_pkg.Intersect(dep_entry.pkg)
                    if final_build_pkg.IsNull():
                        final_pkg_set.append(dep_entry.pkg.copy())
                    else:
                        final_pkg_set[i] = final_build_pkg

            """
            Solidify package version + variants
            """
            final_env.AddRow(final_pkg_set, order)
            for pkg in final_pkg_set:
                pkg.SolidifyVersion()
                #pkg.print()


        """
        Create ordered list of packages to install
        """
        install_schema = final_env.list(reverse=True)
        install_schema = [dep_entry.pkg for dep_row in install_schema for dep_entry in dep_row.list()]

        """
        Solidify package dependencies
        """
        for pkg in install_schema:
            pkg.SolidifyDeps(final_env)
        return install_schema
