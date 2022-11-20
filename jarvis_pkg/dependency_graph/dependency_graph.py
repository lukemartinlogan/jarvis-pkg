from jarvis_pkg.basic.exception import Error, ErrorCode
from jarvis_pkg.basic.manifest_manager import ManifestManager
from jarvis_pkg.basic.package_manager import PackageManager
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.basic.package_id import PackageId
from jarvis_pkg.package.package import Package


class DependencyEnv:
    def __init__(self):
        self.pkg_queries_by_class = {}

    def add_query(self, pkg_query, order, parent):
        pkg_class = pkg_query.get_class()
        if pkg_class not in self.pkg_queries_by_class:
            self.pkg_queries_by_class[pkg_class] = {
                "order": 0,
                "row": [],
                "unique_names": set()
            }
        row = self.pkg_queries_by_class[pkg_class]
        pkg_query.parent = parent
        row['order'] = max(row['order'], order)
        row['row'].append(pkg_query)
        for name in pkg_query.get_names():
            row['unique_names'].add(name)

    def ordered_queries(self):
        ordered_queries = list(self.pkg_queries_by_class.items())
        ordered_queries.sort(key=lambda x: x[1]['order'])
        return ordered_queries


class DependencyGraph:
    def __init__(self):
        self.pkg_manager = PackageManager.get_instance()
        self.manifest_manager = ManifestManager.get_instance()
        self.pkg_env = DependencyEnv()
        self.cyclic_set = set()

    def all_candidate_packages(self, pkg_query, order, parent):
        # Ensure there are no cyclic dependencies
        if pkg_query.get_class() in self.cyclic_set:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(
                pkg_query.get_class())
        else:
            self.cyclic_set.add(pkg_query.get_class())

        # Load the candidate packages
        pkgs = self.manifest_manager.find_load_pkgs(pkg_query.pkg_id)
        if len(pkgs) == 0:
            raise Error(ErrorCode.CANT_FIND_PACKAGE).format(
                pkg_query.pkg_id.name)

        # Process the dependencies for each candidate
        for pkg in pkgs:
            for dep_pkg_query in pkg.dependencies.values():
                self.all_candidate_packages(dep_pkg_query, order + 1,
                                            pkg_query)
            for dep_pkg_query in pkg_query.dependencies_.values():
                self.all_candidate_packages(dep_pkg_query, order + 1,
                                            pkg_query)

        # Add the current query to the dependency environment
        self.pkg_env.add_query(pkg_query, order, parent)
        self.cyclic_set.remove(pkg_query.get_class())

    @staticmethod
    def filter_row(row, candidates_by_class):
        new_row = []
        for pkg_query in row:
            if pkg_query.parent is not None:
                cls = pkg_query.parent.pkg_id.cls
                if candidates_by_class[cls].intersect(pkg_query).is_null():
                    continue
            new_row.append(pkg_query)
        return new_row

    @staticmethod
    def pkg_matches_row(pkg, row):
        for pkg_query in row:
            isect = pkg.intersect(pkg_query)
            if isect.is_null():
                return False
            pkg.update_query(isect)
        return True

    def select_installed(self, installed, pkg_by_class):
        for pkg in installed:
            for dep_pkg_query in pkg.dependencies_:
                if not self.select_installed(dep_pkg_query, pkg_by_class):
                    return False
            pkg_class = pkg.pkg_id.cls
            pkg_query_row = self.pkg_env.pkg_queries_by_class[pkg_class]
            row = pkg_query_row['row']
            if self.pkg_matches_row(pkg, row):
                pkg_by_class[pkg_class] = pkg
                return True
        return False

    def reduce_candidates(self, row_candidates, candidates_by_class):
        # Prioritize installed or introspected candidates
        for candidate in row_candidates:
            self.pkg_manager.introspect(candidate)
            installed = self.pkg_manager.query(candidate)
            if len(installed) > 0:
                pkg_by_class = {}
                if self.select_installed(installed, pkg_by_class):
                    candidates_by_class.update(pkg_by_class)
                    return candidates_by_class[candidate.pkg_id.cls]
        candidate = row_candidates[0]
        pkg = self.manifest_manager.select(candidate)
        candidates_by_class[candidate.pkg_id.cls] = pkg
        return candidates_by_class[candidate.pkg_id.cls]

    def build_candidates(self, ordered_queries):
        candidates_by_class = {}
        candidates = []  # [pkg_query]
        for pkg_query_row in ordered_queries:
            cls = pkg_query_row[0]
            row = pkg_query_row[1]['row']
            unique_names = pkg_query_row[1]['unique_names']

            if cls in candidates_by_class:
                final_candidate = candidates_by_class[cls]
                candidates.insert(0, final_candidate)
                continue

            # Filter out queries whose parents have been pruned
            row = self.filter_row(row, candidates_by_class)

            # Determine the set of candidate PKGs for this row
            row_candidates = []
            for name in unique_names:
                pkgs = self.manifest_manager.find_load_pkgs(
                    PackageId(None, cls, name))
                for pkg in pkgs:
                    if self.pkg_matches_row(pkg, row):
                        row_candidates.append(pkg)
            if len(row_candidates) == 0:
                raise Error(ErrorCode.UNSATISFIABLE).format(cls)

            # Choose a single candidate
            final_candidate = self.reduce_candidates(row_candidates,
                                                     candidates_by_class)
            candidates.insert(0, final_candidate)
        return candidates

    def build(self, pkg_query_list):
        for pkg_query in pkg_query_list:
            self.all_candidate_packages(pkg_query, 0, None)
        ordered_queries = self.pkg_env.ordered_queries()
        candidates = self.build_candidates(ordered_queries)
        return candidates
