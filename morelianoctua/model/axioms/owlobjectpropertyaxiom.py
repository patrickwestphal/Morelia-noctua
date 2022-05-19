from functools import reduce
from typing import Set

from rdflib import URIRef

from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.objects.annotation import OWLAnnotation
from morelianoctua.model.objects.classexpression import OWLClassExpression
from morelianoctua.model.objects.property import OWLObjectPropertyExpression, \
    OWLObjectProperty


class OWLObjectPropertyAxiom(OWLAxiom):
    pass


class OWLSubObjectPropertyOfAxiom(OWLObjectPropertyAxiom):
    _hash_idx = 193

    def __init__(
            self,
            sub_property: OWLObjectPropertyExpression,
            super_property: OWLObjectPropertyExpression,
            annotations: Set[OWLAnnotation] = None):
        self.sub_property = sub_property
        self.super_property = super_property
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLSubObjectPropertyOfAxiom):
            return False
        else:
            is_equal = self.sub_property == other.sub_property \
                 and self.super_property == other.super_property

            if self.annotations or other.annotations:
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

    def __str__(self):
        return f'SubObjectPropertyOf({self.sub_property} {self.super_property})'

    def __repr__(self):
        return str(self)


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

    def __init__(self, properties, annotations: Set[OWLAnnotation] = None):
        self.properties = self._init_properties(properties)
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLEquivalentObjectPropertiesAxiom):
            return False
        else:
            is_equal = self.properties == other.properties

            if self.annotations or other.annotations:
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

    def __str__(self):
        return f'EquivalentObjectProperties({" ".join(self.properties)})'

    def __repr__(self):
        return str(self)


class OWLDisjointObjectPropertiesAxiom(
        OWLObjectPropertyAxiom, HasObjectProperties):

    _hash_idx = 199

    def __init__(self, properties, annotations: Set[OWLAnnotation] = None):
        self.properties = self._init_properties(properties)
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDisjointObjectPropertiesAxiom):
            return False
        else:
            is_equal = self.properties == other.properties

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = reduce(
            lambda l, r: self._hash_idx * l + r,
            map(lambda p: hash(p), self.properties))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'DisjointObjectProperties({" ".join(self.properties)})'

    def __repr__(self):
        return str(self)


class OWLInverseObjectPropertiesAxiom(OWLObjectPropertyAxiom):
    _hash_idx = 211

    def __init__(
            self,
            first: OWLObjectPropertyExpression,
            second: OWLObjectPropertyExpression,
            annotations: Set[OWLAnnotation] = None):

        self.first = first
        self.second = second
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLInverseObjectPropertiesAxiom):
            return False
        else:
            is_equal = self.first == other.first and self.second == other.second

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = reduce(
            lambda l, r: self._hash_idx * l + r,
            map(lambda p: hash(p), [self.first, self.second]))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'InverseObjectProperties({self.first} {self.second})'

    def __repr__(self):
        return str(self)


class OWLObjectPropertyDomainAxiom(OWLObjectPropertyAxiom):
    _hash_idx = 223

    def __init__(
            self,
            object_property: OWLObjectPropertyExpression,
            domain: OWLClassExpression,
            annotations: Set[OWLAnnotation] = None):

        self.object_property = object_property
        self.domain = domain
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLObjectPropertyDomainAxiom):
            return False
        else:
            is_equal = \
                self.object_property == other.object_property and \
                self.domain == other.domain

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = self._hash_idx * hash(self.object_property) + hash(self.domain)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'ObjectPropertyDomain({self.object_property} {self.domain})'

    def __repr__(self):
        return str(self)


class OWLObjectPropertyRangeAxiom(OWLObjectPropertyAxiom):
    _hash_idx = 227

    def __init__(
            self,
            object_property: OWLObjectPropertyExpression,
            range_ce: OWLClassExpression,
            annotations: Set[OWLAnnotation] = None):

        self.object_property = object_property
        self.range_ce = range_ce
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLObjectPropertyRangeAxiom):
            return False
        else:
            is_equal = \
                self.object_property == other.object_property and \
                self.range_ce == other.range_ce

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = self._hash_idx * hash(self.object_property) + hash(self.range_ce)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp

    def __str__(self):
        return f'ObjectPropertyRange({self.object_property} {self.range_ce})'

    def __repr__(self):
        return str(self)
