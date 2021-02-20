from functools import reduce
from typing import Set, Tuple

from rdflib import OWL, Literal, RDFS

from morelianoctua.model.objects import HasIRI, HasOperands, OWLObject
from morelianoctua.model.objects.datarange import OWLDataRange, OWLDatatype
from morelianoctua.model.objects.individual import OWLIndividual
from morelianoctua.model.objects.property import OWLObjectPropertyExpression, \
    OWLDataProperty


class OWLClassExpression(OWLObject):
    pass


class OWLClass(OWLClassExpression, HasIRI):
    _hash_idx = 5

    def __init__(self, iri_or_iri_str):
        self.iri = self._init_iri(iri_or_iri_str)

    def __hash__(self):
        return self._hash_idx * hash(self.iri)


class OWLObjectIntersectionOf(OWLClassExpression, HasOperands):
    _hash_idx = 7

    def __init__(self, *operands: Tuple[OWLClassExpression]):
        self.operands: Set[OWLClassExpression] = {o for o in operands}

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda o: hash(o), self.operands))


class OWLObjectUnionOf(OWLClassExpression, HasOperands):
    _hash_idx = 11

    def __init__(self, *operands: Tuple[OWLClassExpression]):
        self.operands: Set[OWLClassExpression] = {o for o in operands}

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda o: hash(o), self.operands))


class OWLObjectComplementOf(OWLClassExpression):
    _hash_idx = 13

    def __init__(self, operand: OWLClassExpression):
        self.operand = operand

    def __eq__(self, other):
        if not isinstance(other, OWLObjectComplementOf):
            return False
        else:
            return self.operand == other.operand

    def __str__(self):
        return f'ComplementOf({str(self.operand)})'

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self._hash_idx * hash(self.operand)


class OWLObjectOneOf(OWLClassExpression):
    _hash_idx = 17

    def __init__(self, *individuals: Tuple[OWLIndividual]):
        self.individuals: Set[OWLIndividual] = {i for i in individuals}

    def __eq__(self, other):
        if not isinstance(other, OWLObjectOneOf):
            return False
        else:
            return self.individuals == other.individuals

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda i: hash(i), self.individuals))


class OWLObjectSomeValuesFrom(OWLClassExpression):
    _hash_idx = 19

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            filler: OWLClassExpression):

        self.owl_property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLObjectSomeValuesFrom):
            return False
        else:
            return self.owl_property == other.owl_property \
                   and self.filler == other.filler

    def __hash__(self):
        return self._hash_idx * hash(self.owl_property) + hash(self.filler)


class OWLObjectAllValuesFrom(OWLClassExpression):
    _hash_idx = 23

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            filler: OWLClassExpression):

        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLObjectAllValuesFrom):
            return False
        else:
            return self.property == other.property \
                   and self.filler == other.filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + hash(self.filler)


class OWLObjectHasValue(OWLClassExpression):
    _hash_idx = 29

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            value: OWLIndividual):

        self.property = owl_property
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, OWLObjectHasValue):
            return False
        else:
            return self.property == other.property and self.value == other.value

    def __hash__(self):
        return self._hash_idx * hash(self.property) + hash(self.value)


class OWLObjectHasSelf(OWLClassExpression):
    _hash_idx = 31

    def __init__(self, owl_property: OWLObjectPropertyExpression):
        self.property = owl_property

    def __eq__(self, other):
        if not isinstance(other, OWLObjectHasSelf):
            return False
        else:
            return self.property == other.property

    def __hash__(self):
        return self._hash_idx * hash(self.property)


class OWLObjectCardinalityRestriction(OWLClassExpression):
    owl_property: OWLObject
    cardinality: int
    filler: OWLClassExpression

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        else:
            return self.owl_property == other.owl_property \
                   and self.cardinality == other.cardinality \
                   and self.filler == other.filler


class OWLObjectMinCardinality(OWLObjectCardinalityRestriction):
    _hash_idx = 37

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            cardinality: int,
            filler: OWLClassExpression = None):

        self.property = owl_property
        self.cardinality = cardinality

        if filler is None:
            self.filler = OWLClass(OWL.Thing)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)


class OWLObjectMaxCardinality(OWLObjectCardinalityRestriction):
    _hash_idx = 41

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            cardinality: int,
            filler: OWLClassExpression = None):

        self.property = owl_property
        self.cardinality = cardinality
        if filler is None:
            self.filler = OWLClass(OWL.Thing)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)


class OWLObjectExactCardinality(OWLObjectCardinalityRestriction):
    _hash_idx = 53

    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            cardinality: int,
            filler: OWLClassExpression = None):

        self.property = owl_property
        self.cardinality = cardinality

        if filler is None:
            self.filler = OWLClass(OWL.Thing)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)


class OWLDataSomeValuesFrom(OWLClassExpression):
    _hash_idx = 47

    def __init__(self, owl_property: OWLDataProperty, filler: OWLDataRange):
        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLDataSomeValuesFrom):
            return False
        else:
            return self.property == other.property and \
                   self.filler == other.filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + hash(self.filler)


class OWLDataAllValuesFrom(OWLClassExpression):
    _hash_idx = 53

    def __init__(self, owl_property: OWLDataProperty, filler: OWLDataRange):
        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLDataAllValuesFrom):
            return False
        else:
            return self.property == other.property \
                   and self.filler == other.filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + hash(self.filler)


class OWLDataHasValue(OWLClassExpression):
    _hash_idx = 59

    def __init__(self, owl_property: OWLDataProperty, value: Literal):
        self.owl_property = owl_property
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, OWLDataHasValue):
            return False
        else:
            return self.owl_property == other.owl_property and \
                self.value == other.value

    def __hash__(self):
        return self._hash_idx * hash(self.owl_property) + hash(self.value)


class OWLDataCardinalityRestriction(OWLClassExpression):
    owl_property: OWLDataProperty
    cardinality: int
    filler: OWLDataRange

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        else:
            return self.owl_property == other.owl_property \
                   and self.cardinality == other.cardinality \
                   and self.filler == other.filler


class OWLDataMinCardinality(OWLDataCardinalityRestriction):
    _hash_idx = 61

    def __init__(
            self,
            owl_property: OWLDataProperty,
            cardinality: int,
            filler: OWLDataRange = None):

        self.property = owl_property
        self.cardinality = cardinality

        if filler is None:
            self.filler = OWLDatatype(RDFS.Literal)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)


class OWLDataMaxCardinality(OWLDataCardinalityRestriction):
    _hash_idx = 67

    def __init__(
            self,
            owl_property: OWLDataProperty,
            cardinality: int,
            filler: OWLDataRange = None):

        self.property = owl_property
        self.cardinality = cardinality

        if filler is None:
            self.filler = OWLDatatype(RDFS.Literal)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)


class OWLDataExactCardinality(OWLDataCardinalityRestriction):
    _hash_idx = 71

    def __init__(
            self,
            owl_property: OWLDataProperty,
            cardinality: int,
            filler: OWLDataRange = None):

        self.property = owl_property
        self.cardinality = cardinality

        if filler is None:
            self.filler = OWLDatatype(RDFS.Literal)
        else:
            self.filler = filler

    def __hash__(self):
        return self._hash_idx * hash(self.property) + \
               (self._hash_idx * hash(self.cardinality)) + hash(self.filler)
