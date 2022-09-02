from jarvis_pkg.basic.jpkg_manager import JpkgManager
from jarvis_pkg.basic.exception import Error,ErrorCode

class DependencyGraph:
    def __init__(self):
        self.jpkg_manager = JpkgManager.GetInstance()

    def _GetInstallEnvironment(self, root_pkg, env, order=0, build_dep=False, parent=None, cycle_env=None):
        if cycle_env is None:
            cycle_env = set()
        if root_pkg.GetClass() not in cycle_env:
            cycle_env.add(root_pkg.GetClass())
        else:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(root_pkg.GetClass())
        for pkg in root_pkg.GetBuildDeps():
            self._GetInstallEnvironment(pkg, env, order=order+1, build_dep=True*build_dep, parent=root_pkg)
        for pkg in root_pkg.GetRunDeps():
            self._GetInstallEnvironment(pkg, env, order=order+1, parent=root_pkg)
        if root_pkg.GetClass() not in env:
            env[root_pkg.GetClass()] = []
        pkg_info = {
            'pkg': root_pkg,
            'order': order,
            'is_build_dep': build_dep,
            'depends_on': parent
        }
        env[root_pkg.GetClass()].append(pkg_info)

    def _DependencyInEnv(self, pkg_name, final_env, pkg_info):
        for pkg in final_env[pkg_name]['pkg_set']:
            if pkg_info['depends_on'] is None:
                return True
            if not pkg_info['depends_on'].copy().Intersect(pkg).IsNull():
                return True
        return False

    def Build(self, pkg_list):
        env = {} #pkg_name -> [{pkg, order, is_build_dep, depends_on}]
        for root_pkg in pkg_list:
            self._GetInstallEnvironment(root_pkg, env)
        install_schema = [] #[{order_min, row: {pkg, order, is_build_dep, depends_on}}]
        for pkg_info_row in env.values():
            order_min = min(pkg_info_row, key=lambda x: x['order'])
            schema_row = {
                'order_min': order_min['order'],
                'row': pkg_info_row
            }
            install_schema.append(schema_row)
        install_schema.sort(key=lambda x: x['order_min'])

        final_env = {} #pkg_name -> {order, pkg_set: [pkg]}
        for schema_row in install_schema:
            pkg_info_row = schema_row['row']

            """
            Filter out runtime and buildtime deps
            """
            for pkg_info in pkg_info_row:
                if pkg_info['depends_on'] is None:
                    continue
                pkg_name = pkg_info['depends_on'].GetClass()
                if pkg_name not in final_env and not pkg_info['is_build_dep']:
                    del pkg_info
                    continue
                if not self._DependencyInEnv(pkg_name, final_env, pkg_info):
                    del pkg_info
                    continue
            if len(pkg_info_row) == 0:
                continue
            build_row = [pkg_info for pkg_info in pkg_info_row if pkg_info['is_build_dep']]
            run_row = [pkg_info for pkg_info in pkg_info_row if not pkg_info['is_build_dep']]
            order_max = max(pkg_info_row, key=lambda x: x['order'])['order']

            """
            Intersect all runtime deps
            """
            final_pkg_set = [] #[pkg]
            if len(run_row):
                final_run_pkg = run_row[0]['pkg'].copy()
                for pkg_info in run_row[1:]:
                    final_run_pkg.Intersect(pkg_info['pkg'])
                    if final_run_pkg.IsNull():
                        raise 1
                final_pkg_set.append(final_run_pkg)

            """
            If row has both buildtime and runtime, ensure they don't conflict 
            """
            if len(build_row) and len(run_row):
                final_run_pkg = final_pkg_set[0]
                run_order_max = max(run_row, key=lambda x: x['order'])['order']
                for pkg_info in build_row:
                    if pkg_info['order'] <= run_order_max:
                        if pkg_info['pkg'].copy().Intersect(final_run_pkg).IsNull():
                            raise 2

            """
            Integrate buildtime deps
            """
            if len(final_pkg_set) == 0:
                final_pkg_set.append(build_row[0]['pkg'].copy())
                build_row = build_row[1:]
            for pkg_info in build_row:
                for i,final_build_pkg in enumerate(final_pkg_set):
                    final_build_pkg  = final_build_pkg.copy()
                    final_build_pkg.Intersect(pkg_info['pkg'])
                    if final_build_pkg.IsNull():
                        final_pkg_set.append(pkg_info['pkg'].copy())
                    else:
                        final_pkg_set[i] = final_build_pkg

            """
            Solidify package version + variants
            """
            final_env[final_pkg_set[0].GetClass()] = {'order': order_max, 'pkg_set': final_pkg_set}
            for pkg in final_pkg_set:
                pkg.SolidifyVersion()

        """
        Create ordered list of packages to install
        """
        install_schema = list(final_env.values())  # [{order, pkg_set: {pkg, order, is_build_dep, depends_on}}]
        install_schema.sort(reverse=True, key=lambda x: x['order'])
        install_schema = [pkg for pkg_info in install_schema for pkg in pkg_info['pkg_set']]

        """
        Solidify package dependencies
        """
        for pkg in install_schema:
            pkg.SolidifyDeps(final_env)
        return install_schema
