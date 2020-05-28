from abc import ABC

from model.objects.datarange import OWLDatatype
from model.objects.individual import OWLNamedIndividual
from model.objects.classexpression import OWLClass
from model.objects.property import OWLObjectProperty, OWLDataProperty, \
    OWLAnnotationProperty


class OWLDeclarationAxiom(ABC):
    annotations = []


class OWLClassDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(self, cls: OWLClass, annotations=[]):
        self.cls = cls
        self.annotations = annotations


class OWLDatatypeDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(self, dtype: OWLDatatype, annotations=None):
        self.dtype = dtype
        self.annotations = annotations


class OWLObjectPropertyDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(self, obj_property: OWLObjectProperty, annotations=None):
        self.obj_property = obj_property
        self.annotations = annotations


class OWLDataPropertyDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(self, data_property: OWLDataProperty, annotations=None):
        self.data_property = data_property
        self.annotations = annotations


class OWLAnnotationPropertyDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(
            self, annotation_property: OWLAnnotationProperty, annotations=None):

        self.annotation_property = annotation_property
        self.annotations = annotations


class OWLNamedIndividualDeclarationAxiom(OWLDeclarationAxiom):
    def __init__(
            self, individual: OWLNamedIndividual, annotations=None):

        self.individual = individual
        self.annotations = annotations
