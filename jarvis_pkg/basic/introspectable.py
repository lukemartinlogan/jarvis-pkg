from abc import ABC, abstractmethod


class Introspectable(ABC):
    @abstractmethod
    def get_introspect_state(self):
        """
        Query the state of the alternate package manager.

        :return:
        """
        pass

    def introspect(self, state):
        """
        Find the specific package in the alternate package manager.

        :param state: return value of introspect_state
        :return:
        """
        pass
