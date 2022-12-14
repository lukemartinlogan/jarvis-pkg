class Error(BaseException):
    def __init__(self, error_code, child_error = None):
        self._error_code = error_code["id"]
        if child_error is None:
            self._error_message = error_code["msg"]
        else:
            self._error_message = str(child_error) + "\n{}".format(error_code["msg"])

    def format(self, *error_code_args):
        """
        Formatted the error message
        :param error_code_args:
        :return: Error
        """
        self._error_message = self._error_message.format(*error_code_args)
        return self

    def __repr__(self):
        return {'error_code': self._error_code, 'error_message': self._error_message}

    def __str__(self):
        return self._error_message

class ErrorCode:
    """
    A class shows all the error code in Luxio
    """
    SUCCESS = {"id": 0, "msg": "SUCCESSFUL"}

    # Dependency Graph
    UNKOWN_PACKAGE = {"id": 101, "msg": "Cannot find package {}"}
    CYCLIC_DEPENDENCY = {"id": 102, "msg": "{} depends on itself. Cyclic dependency"}
    CONFLICTING_VERSIONS = {"id": 103, "msg": "The installation requires multiple versions of {}"}
    CONFLICTING_VARIANTS = {"id": 104, "msg": "An installation candidate requires variant {} with both values {} and {}"}
    INVALID_VERSION_STRING = {"id": 105, "msg": "Invalid version string install: {}"}
    VERSION_SET_NOT_STRING = {"id": 106, "msg": "When setting version range, string notation required"}
    CONFLICT = {"id": 107, "msg": "{}"}

    # Repo manager
    CANT_FIND_INSTALLED_PKG = {"id": 400, "msg": "Cannot find installed package {}.{}"}

    # Query Parser
    MALFORMED_VERSION_QUERY = {"id": 200, "msg": "Malformed version query in token: {}"}
    MALFORMED_PKG_NAME_QUERY = {"id": 201, "msg": "Malformed package name query in token: {}"}
    MALFORMED_VARIANT = {"id": 202, "msg": "Malformed variant in package query {}: {}"}
    MULTIPLE_VERSIONS_IN_QUERY = {"id": 203, "msg": "Multiple versions specified for a single package query {}"}

    # Package definition
    PACKAGE_PHASE_UNDEFINED = {"id": 300, "msg": "Phase {} in {}.{} was not defined"}
    INSTALLER_UNDEFINED = {"id": 301, "msg": "The installer {} in {}.{} was not defined"}
    REQUIRE_INTROSPECT = {"id": 302, "msg": "Introspect disabled for {}.{}, but not satisifiable version"}
    CLASS_NOT_FOUND = {"id": 303, "msg": "Class {} was not found in any namespace"}
    DIFFERENT_PKGS = {"id": 304, "msg": "Cannot compare {}.{} with {}.{}"}