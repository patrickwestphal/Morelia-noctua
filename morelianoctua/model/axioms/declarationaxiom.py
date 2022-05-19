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

    def __str__(self):
        return f'Declaration(Class({self.cls}))'

    def __repr__(self):
        return str(self)


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

    def __str__(self):
        return f'Declaration(Datatype({self.dtype}))'

    def __repr__(self):
        return str(self)


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

    def __str__(self):
        return f'Declaration(ObjectProperty({self.object_property}))'

    def __repr__(self):
        return str(self)


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

    def __str__(self):
        return f'Declaration(DatatypeProperty({self.data_property}))'

    def __repr__(self):
        return str(self)


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

    def __str__(self):
        return f'AnnotationProperty({self.annotation_property})'

    def __repr__(self):
        return str(self)


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

    def __str__(self):
        return f'Declaration(NamedIndividual({self.individual}))'

    def __repr__(self):
        return str(self)
