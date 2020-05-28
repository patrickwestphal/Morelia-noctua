from abc import ABC

from rdflib import URIRef, BNode, OWL, Literal, RDFS

from model.objects import HasIRI, HasOperands, OWLObject
from model.objects.datarange import OWLDataRange, OWLDatatype
from model.objects.individual import OWLIndividual, OWLAnonymousIndividual, \
    OWLNamedIndividual
from model.objects.property import OWLObjectPropertyExpression, OWLDataProperty


class OWLClassExpression(ABC):
    pass


class OWLClass(OWLClassExpression, HasIRI):
    def __init__(self, iri_or_iri_str):
        self.iri = self._init_iri(iri_or_iri_str)

    def __hash__(self):
        return hash(self.iri)


class OWLObjectIntersectionOf(OWLClassExpression, HasOperands):
    def __init__(self, *operands):
        self.operands = self._init_operands(operands)


class OWLObjectUnionOf(OWLClassExpression, HasOperands):
    def __init__(self, *operands):
        self.operands = self._init_operands(operands)


class OWLObjectComplementOf(OWLClassExpression):
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


class OWLObjectOneOf(OWLClassExpression):
    def __init__(self, *individuals):
        self.individuals = set()

        for individual in individuals:
            if isinstance(individual, OWLIndividual):
                self.individuals.add(individual)

            elif isinstance(individuals, URIRef):
                self.individuals.add(OWLNamedIndividual(individuals))

            elif isinstance(individual, BNode):
                self.individuals.add(OWLAnonymousIndividual(individual))

            else:  # just the identifier str given, not an individual objects
                assert isinstance(individual, str)

                if individual.startswith('_:'):
                    self.individuals.add(OWLAnonymousIndividual(individual))
                else:
                    self.individuals.add(OWLNamedIndividual(individuals))

    def __eq__(self, other):
        if not isinstance(other, OWLObjectOneOf):
            return False
        else:
            return self.individuals == other.individuals


class OWLObjectSomeValuesFrom(OWLClassExpression):
    def __init__(
            self,
            owl_property: OWLObjectPropertyExpression,
            filler: OWLClassExpression):

        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLObjectSomeValuesFrom):
            return False
        else:
            return self.property == other.property \
                   and self.filler == other.filler


class OWLObjectAllValuesFrom(OWLClassExpression):
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


class OWLObjectHasValue(OWLClassExpression):
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


class OWLObjectHasSelf(OWLClassExpression):
    def __init__(self, owl_property: OWLObjectPropertyExpression):
        self.property = owl_property

    def __eq__(self, other):
        if not isinstance(other, OWLObjectHasSelf):
            return False
        else:
            return self.property == other.property


class OWLObjectCardinalityRestriction(OWLClassExpression):
    property: OWLObject
    cardinality: int
    filler: OWLClassExpression

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        else:
            return self.property == other.property \
                   and self.cardinality == other.cardinality \
                   and self.filler == other.filler


class OWLObjectMinCardinality(OWLObjectCardinalityRestriction):
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


class OWLObjectMaxCardinality(OWLObjectCardinalityRestriction):
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


class OWLObjectExactCardinality(OWLObjectCardinalityRestriction):
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


class OWLDataSomeValuesFrom(OWLClassExpression):
    def __init__(self, owl_property: OWLDataProperty, filler: OWLDataRange):
        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLDataSomeValuesFrom):
            return False
        else:
            return self.property == other.property and \
                   self.filler == other.filler


class OWLDataAllValuesFrom(OWLClassExpression):
    def __init__(self, owl_property: OWLDataProperty, filler: OWLDataRange):
        self.property = owl_property
        self.filler = filler

    def __eq__(self, other):
        if not isinstance(other, OWLDataAllValuesFrom):
            return False
        else:
            return self.property == other.property \
                   and self.filler == other.filler


class OWLDataHasValue(OWLClassExpression):
    def __init__(self, owl_property: OWLDataProperty, value: Literal):
        self.property = owl_property
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, OWLDataHasValue):
            return False
        else:
            return self.property == other.property and self.value == other.value


class OWLDataCardinalityRestriction(OWLClassExpression):
    property: OWLDataProperty
    cardinality: int
    filler: OWLDataRange

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        else:
            return self.property == other.property \
                   and self.cardinality == other.cardinality \
                   and self.filler == other.filler


class OWLDataMinCardinality(OWLDataCardinalityRestriction):
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


class OWLDataMaxCardinality(OWLDataCardinalityRestriction):
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


class OWLDataExactCardinality(OWLDataCardinalityRestriction):
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
