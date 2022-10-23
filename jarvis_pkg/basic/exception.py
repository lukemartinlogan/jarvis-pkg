class Error(BaseException):
    def __init__(self, error_code, child_error = None):
        if child_error is None:
            self._error_message = error_code.value
        else:
            self._error_message = str(child_error) + \
                                  "\n{}".format(error_code.value)

    def format(self, *error_code_args):
        """
        Formatted the error message
        :param error_code_args:
        :return: Error
        """
        self._error_message = self._error_message.format(*error_code_args)
        return self

    def __repr__(self):
        return self._error_message

    def __str__(self):
        return self._error_message


class ErrorCode:
    """
    A class shows all the error code in Luxio
    """
    SUCCESS = "SUCCESSFUL"
    INVALID_PARAMETER = "{} is not a valid input for {}"
    INVALID_VERSION_STRING = "Invalid version string: {}"

    # Dependency Graph
    UNKOWN_PACKAGE = "Cannot find package {}"
    CYCLIC_DEPENDENCY = "Cyclic dependency: {}"
    UNSATISFIABLE = "Cannot satisfy the dependency {}"
