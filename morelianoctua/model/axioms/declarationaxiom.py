from functools import reduce
from typing import Set

from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.objects.annotation import OWLAnnotation
from morelianoctua.model.objects.classexpression import OWLClass
from morelianoctua.model.objects.datarange import OWLDatatype
from morelianoctua.model.objects.individual import OWLNamedIndividual
from morelianoctua.model.objects.property import OWLObjectProperty, \
    OWLDataProperty, OWLAnnotationProperty


class OWLDeclarationAxiom(OWLAxiom):
    annotations = []


class OWLClassDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 163

    def __init__(self, cls: OWLClass, annotations: Set[OWLAnnotation] = None):
        self.cls = cls
        self.annotations = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.cls)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLDatatypeDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 167

    def __init__(self, dtype: OWLDatatype, annotations=None):
        self.dtype = dtype
        self.annotations: Set[OWLAnnotation] = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.dtype)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLObjectPropertyDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 173

    def __init__(
            self,
            object_property: OWLObjectProperty,
            annotations: Set[OWLAnnotation] = None):
        self.object_property = object_property
        self.annotations = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.object_property)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLDataPropertyDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 179

    def __init__(self, data_property: OWLDataProperty, annotations=None):
        self.data_property = data_property
        self.annotations = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.data_property)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLAnnotationPropertyDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 181

    def __init__(
            self, annotation_property: OWLAnnotationProperty, annotations=None):

        self.annotation_property = annotation_property
        self.annotations = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.annotation_property)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLNamedIndividualDeclarationAxiom(OWLDeclarationAxiom):
    _hash_idx = 191

    def __init__(
            self,
            individual: OWLNamedIndividual,
            annotations: Set[OWLAnnotation] = None):

        self.individual = individual
        self.annotations = annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.individual)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp
