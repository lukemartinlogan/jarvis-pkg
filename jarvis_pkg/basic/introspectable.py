from abc import ABC, abstractmethod


class Introspectable(ABC):
    @abstractmethod
    def introspect(self):
        pass
