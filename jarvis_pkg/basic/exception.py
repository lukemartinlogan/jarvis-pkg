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

    #Query Parser
    MALFORMED_QUERY = {"id": 100, "msg": "Malformed query: {}"}
    UNKOWN_PACKAGE = {"id": 101, "msg": "Cannot find package {}"}
    CYCLIC_DEPENDENCY = {"id": 102, "msg": "{} depends on itself. Cyclic dependency"}
    MULTIPLE_PACKAGE_VERSIONS_LOADED = {"id": 103, "msg": "Different version of {} were required for install, which is not allowed."}
    CONFLICTING_VARIANTS = {"id": 104, "msg": "Different variants of {} were required, which is not allowed."}

