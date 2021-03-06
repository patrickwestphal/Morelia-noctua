from functools import reduce
from typing import Set

from rdflib import Literal

from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.objects.annotation import OWLAnnotation
from morelianoctua.model.objects.classexpression import OWLClassExpression
from morelianoctua.model.objects.individual import OWLIndividual
from morelianoctua.model.objects.property import OWLDataProperty, \
    OWLObjectPropertyExpression


class OWLClassAssertionAxiom(OWLAxiom):
    _hash_idx = 229

    def __init__(
            self, individual: OWLIndividual,
            class_expression: OWLClassExpression,
            annotations: Set[OWLAnnotation] = None):

        self.individual = individual
        self.class_expression = class_expression
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLClassAssertionAxiom):
            return False

        else:
            is_equal = \
                self.individual == other.individual and \
                self.class_expression == other.class_expression

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = \
            self._hash_idx * hash(self.individual) + hash(self.class_expression)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLObjectPropertyAssertionAxiom(OWLAxiom):
    _hash_idx = 233

    def __init__(
            self,
            subject_individual: OWLIndividual,
            owl_property: OWLObjectPropertyExpression,
            object_individual: OWLIndividual,
            annotations=None):
        self.subject_individual = subject_individual
        self.owl_property = owl_property
        self.object_individual = object_individual
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLObjectPropertyAssertionAxiom):
            return False
        else:
            is_equal = \
                self.subject_individual == other.subject_individual and \
                self.owl_property == other.owl_property and \
                self.object_individual == other.object_individual

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = \
            self._hash_idx * hash(self.subject_individual) + \
            hash(self.owl_property)

        tmp += self._hash_idx * hash(self.object_individual)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLDataPropertyAssertionAxiom(OWLAxiom):
    _hash_idx = 239

    def __init__(
            self,
            subject_individual: OWLIndividual,
            owl_property: OWLDataProperty,
            value: Literal,
            annotations=None):

        self.subject_individual = subject_individual
        self.owl_property = owl_property
        self.value = value
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDataPropertyAssertionAxiom):
            return False
        else:
            is_equal = \
                self.subject_individual == other.subject_individual and \
                self.owl_property == other.owl_property and \
                self.value == other.value

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = \
            self._hash_idx * hash(self.subject_individual) + \
            hash(self.owl_property)

        tmp += self._hash_idx * hash(self.value)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp
