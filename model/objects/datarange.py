from rdflib import Literal

from model.objects import HasDatatypeOperands, HasIRI, OWLObject
from model.objects.facet import OWLFacetRestriction


class OWLDataRange(OWLObject):
    pass


class OWLDatatype(OWLDataRange, HasIRI):
    def __init__(self, iri_or_iri_str):
        self.iri = self._init_iri(iri_or_iri_str)

    def __eq__(self, other):
        if not isinstance(other, OWLDatatype):
            return False
        else:
            return self.iri == other.iri

    def __hash__(self):
        return hash(self.iri)


class OWLDataIntersectionOf(OWLDataRange, HasDatatypeOperands):
    def __init__(self, *operands):
        self.operands = self._init_operands(operands)


class OWLDataUnionOf(OWLDataRange, HasDatatypeOperands):
    def __init__(self, *operands):
        self.operands = self._init_operands(operands)


class OWLDataComplementOf(OWLDataRange):
    def __init__(self, data_range: OWLDataRange):
        self.data_range = data_range

    def __eq__(self, other):
        if not isinstance(other, OWLDataComplementOf):
            return False
        else:
            return self.data_range == other.data_range


class OWLDataOneOf(OWLDataRange):
    def __init__(self, *values):
        self.operands = set()

        for v in values:
            assert isinstance(v, Literal)
            self.operands.add(v)

    def __eq__(self, other):
        if not isinstance(other, OWLDataOneOf):
            return False
        else:
            return self.operands == other.operands


class OWLDatatypeRestriction(OWLDataRange):
    def __init__(self, datatype: OWLDatatype, facet_restrictions):
        self.datatype = datatype
        self.facet_restrictions = set()

        for facet_restriction in facet_restrictions:
            assert isinstance(facet_restriction, OWLFacetRestriction)
            self.facet_restrictions.add(facet_restriction)

    def __eq__(self, other):
        if not isinstance(other, OWLDatatypeRestriction):
            return False
        else:
            return self.datatype == other.datatype \
                   and self.facet_restrictions == other.facet_restrictions
