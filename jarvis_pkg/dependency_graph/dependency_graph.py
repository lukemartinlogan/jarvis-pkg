from jarvis_pkg.basic.manifest_manager import ManifestManager
from jarvis_pkg.basic.package_manager import PackageManager
from jarvis_pkg.basic.package_query import PackageQuery
from jarvis_pkg.package.package import Package


class DependencyEnv:
    def __init__(self):
        self.pkg_queries_by_class = {
            "order": 0,
            "row": [],
            "unique_names": set()
        }

    def add_query(self, pkg_query, parent, order):
        pkg_class = pkg_query.get_class()
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
        self.pkg_env = DependencyEnv
        self.cyclic_set = set()

    def all_candidate_packages(self, pkg_query, order, parent):
        # Ensure there are no cyclic dependencies
        if pkg_query.get_class() in self.cyclic_set:
            raise Error(ErrorCode.CYCLIC_DEPENDENCY).format(
                pkg_query.get_class())
        else:
            self.cyclic_set.add(pkg_query.get_class())

        # Load the candidate packages
        if pkg_query.name is not None:
            pkgs = self.manifest_manager.find_load_pkgs(pkg_query.name)
        else:
            pkgs = self.manifest_manager.find_load_pkgs(pkg_query.cls)

        # Process the dependencies for each candidate
        for pkg in pkgs:
            for dep_pkg_query in pkg.dependencies:
                self.all_candidate_packages(dep_pkg_query, order + 1,
                                            pkg_query)

        # Add the current query to the dependency environment
        self.pkg_env.add_query(pkg_query, order, parent)

    @staticmethod
    def simple_query_matches_row(simple_query, row):
        for pkg_query in row:
            simple_query.intersect(pkg_query)
            if simple_query.is_null():
                return False
        return True

    def reduce_candidates(self, row_candidates):
        for candidate in row_candidates:
            # Prioritize already installed
            if self.pkg_manager.is_installed(candidate):
                return self.pkg_manager.query(candidate)
            # Prioritize introspectable candidates
            if self.pkg_manager.introspect(candidate):
                return self.pkg_manager.query(candidate)
        return self.manifest_manager.query(row_candidates[0])

    def filter_row(self, row, candidates_by_class):
        new_row = []
        for pkg_query in row:
            if pkg_query.parent is None:
                continue
            cls = pkg_query.pkg_id.cls
            if candidates_by_class[cls].intersect(pkg_query).is_null():
                continue
            new_row.append(pkg_query)
        return new_row

    def build_candidates(self, ordered_queries):
        candidates_by_class = {}
        candidates = []  # [pkg_query]
        for pkg_query_row in ordered_queries:
            cls = pkg_query_row[0]
            order = pkg_query_row[1]['order']
            row = pkg_query_row[1]['row']
            unique_names = pkg_query_row[1]['unique_names']

            # Filter out queries whose parents have been pruned
            self.filter_row(row, candidates_by_class)

            # Determine the set of candidate PKGs for this row
            row_candidates = []
            for name in unique_names:
                simple_query = PackageQuery()
                simple_query.pkg_id.cls = cls
                simple_query.pkg_id.name = name
                if self.simple_query_matches_row(simple_query, row):
                    row_candidates.append(simple_query)
            if len(row_candidates) == 0:
                raise Error(ErrorCode.UNSATISFIABLE).format(cls)

            # Choose a single candidate
            final_candidate = self.reduce_candidates(row_candidates)
            candidates.insert(0, final_candidate)
            candidates_by_class[cls] = final_candidate.to_query()
        return candidates

    def build(self, pkg_query_list):
        for pkg_query in pkg_query_list:
            self.all_candidate_packages(pkg_query, 0, None)
        ordered_queries = self.pkg_env.ordered_queries()
        candidates = self.build_candidates(ordered_queries)
        return candidates
