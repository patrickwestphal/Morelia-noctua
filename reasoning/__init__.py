from abc import ABC, abstractmethod


class OWLReasoner(ABC):
    @abstractmethod
    def get_classes(self):
        pass

    @abstractmethod
    def get_subclasses(self, class_expression):
        pass

    @abstractmethod
    def get_superclasses(self, class_expression):
        pass
