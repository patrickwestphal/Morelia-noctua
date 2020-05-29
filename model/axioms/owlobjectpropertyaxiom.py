from functools import reduce

from rdflib import URIRef

from model.axioms import OWLAxiom
from model.objects.property import OWLObjectPropertyExpression, \
    OWLObjectProperty


class OWLObjectPropertyAxiom(OWLAxiom):
    pass


class OWLSubObjectPropertyAxiomOfAxiom(OWLObjectPropertyAxiom):
    _hash_idx = 193

    def __init__(
            self,
            sub_property: OWLObjectPropertyExpression,
            super_property: OWLObjectPropertyExpression,
            annotations=None):
        self.sub_property = sub_property
        self.super_property = super_property
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLSubObjectPropertyAxiomOfAxiom):
            return False
        else:
            is_equal = self.sub_property == other.sub_property \
                 and self.super_property == other.super_property

            if self.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = self._hash_idx * hash(self.sub_property) + \
              (self._hash_idx * hash(self.super_property))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda o: hash(o), self.annotations))

        return tmp


class HasObjectProperties(OWLAxiom):
    @staticmethod
    def _init_properties(properties):
        obj_props = set()

        for prop in properties:
            if isinstance(prop, OWLObjectPropertyExpression):
                obj_props.add(prop)
            elif isinstance(prop, URIRef) or isinstance(prop, str):
                obj_props.add(OWLObjectProperty(prop))
            else:
                raise RuntimeError(
                    f'{prop} does not look like an object property expression')

        return obj_props


class OWLEquivalentObjectPropertiesAxiom(
        OWLObjectPropertyAxiom, HasObjectProperties):

    _hash_idx = 197

    def __init__(self, properties, annotations=None):
        self.properties = self._init_properties(properties)
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLEquivalentObjectPropertiesAxiom):
            return False
        else:
            is_equal = self.properties == other.properties

            if self.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda p: hash(p), self.properties))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp
