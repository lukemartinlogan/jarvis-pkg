
class PackageId:
    def __init__(self, namespace, pkg_class, pkg_name):
        self.namespace = namespace
        if pkg_class is not None:
            self.cls = pkg_class
        else:
            self.cls = pkg_name
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

    def dict(self):
        return {
            "namespace": self.namespace,
            "cls": self.cls,
            "name": self.name
        }

    def to_string(self):
        return f"{self.namespace}.{self.cls}.{self.name}"

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()
