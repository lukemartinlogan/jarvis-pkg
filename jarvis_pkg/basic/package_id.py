
class PackageId:
    def __init__(self, namespace, pkg_class, pkg_name):
        self.namespace = namespace
        self.cls = pkg_class
        self.name = pkg_name

    def __hash__(self):
        return (hash(self.namespace) ^
                hash(self.cls) ^
                hash(self.name))

    def __eq__(self, other):
        if other.namespace != self.namespace:
            return False
        if other.cls != self.cls:
            return False
        if other.name != self.name:
            return False
        return True
