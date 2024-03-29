from functools import reduce
from typing import Set

from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.objects.annotation import OWLAnnotation
from morelianoctua.model.objects.classexpression import OWLClassExpression
from morelianoctua.model.objects.datarange import OWLDataRange
from morelianoctua.model.objects.property import OWLDataProperty


class OWLDataPropertyAxiom(OWLAxiom):
    pass


class OWLDataPropertyDomainAxiom(OWLDataPropertyAxiom):
    _hash_idx = 241

    def __init__(
            self,
            data_property: OWLDataProperty,
            domain: OWLClassExpression,
            annotations: Set[OWLAnnotation] = None):

        self.data_property = data_property
        self.domain = domain
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDataPropertyDomainAxiom):
            return False
        else:
            is_equal = \
                self.data_property == other.data_property and \
                self.domain == other.domain

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = self._hash_idx * hash(self.data_property) + hash(self.domain)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'DataPropertyDomain({self.data_property} {self.domain})'

    def __repr__(self):
        return str(self)


class OWLDataPropertyRangeAxiom(OWLDataPropertyAxiom):
    _hash_idx = 251

    def __init__(
            self,
            data_property: OWLDataProperty,
            data_range: OWLDataRange,
            annotations: Set[OWLAnnotation] = None):

        self.data_property = data_property
        self.data_range = data_range
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDataPropertyRangeAxiom):
            return False
        else:
            is_equal = \
                self.data_property == other.data_property and \
                self.data_range == other.data_range

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = self._hash_idx * hash(self.data_property) + hash(self.data_range)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'DataPropertyRange({self.data_property} {self.data_range})'

    def __repr__(self):
        return str(self)
