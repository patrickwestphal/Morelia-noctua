from functools import reduce

from rdflib import Literal, URIRef

from morelianoctua.model.objects import HasDatatypeOperands, HasIRI, OWLObject
from morelianoctua.model.objects.facet import OWLFacetRestriction


class OWLDataRange(OWLObject):
    pass


class OWLDatatype(OWLDataRange, HasIRI):
    _hash_idx = 73

    def __init__(self, iri_or_iri_str):
        self.iri = self._init_iri(iri_or_iri_str)

    def __eq__(self, other):
        if not isinstance(other, OWLDatatype):
            return False
        else:
            return self.iri == other.iri

    def __hash__(self):
        return self._hash_idx * hash(self.iri)

    def __str__(self):
        return f'<{self.iri}>'

    def __repr__(self):
        return str(self)


class OWLDataIntersectionOf(OWLDataRange, HasDatatypeOperands):
    _hash_idx = 79

    def __init__(self, *operands):
        self.operands = self._init_operands(operands)

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda o: hash(o), self.operands))

    def __str__(self):
        return \
            f'DataIntersectionOf({" ".join([str(o) for o in self.operands])})'

    def __repr__(self):
        return str(self)


class OWLDataUnionOf(OWLDataRange, HasDatatypeOperands):
    _hash_idx = 83

    def __init__(self, *operands):
        self.operands = self._init_operands(operands)

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda o: hash(o), self.operands))

    def __str__(self):
        return \
            f'DataUnionOf(' \
            f'{" ".join([str(drange) for drange in self.operands])})'

    def __repr__(self):
        return str(self)


class OWLDataComplementOf(OWLDataRange):
    _hash_idx = 89

    def __init__(self, data_range: OWLDataRange):
        if isinstance(data_range, URIRef):
            self.data_range = OWLDatatype(data_range)
        else:
            self.data_range = data_range

    def __eq__(self, other):
        if not isinstance(other, OWLDataComplementOf):
            return False
        else:
            return self.data_range == other.data_range

    def __hash__(self):
        return self._hash_idx * hash(self.data_range)

    def __str__(self):
        return f'DataComplementOf({str(self.data_range)})'

    def __repr__(self):
        return str(self)


class OWLDataOneOf(OWLDataRange):
    _hash_idx = 97

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

    def __hash__(self):
        return reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda l: hash(l), self.operands))

    def __str__(self):
        operands_strs = [f'"{o.value}"^^<{o.datatype}>' for o in self.operands]
        return f'DataOneOf({" ".join(operands_strs)})'

    def __repr__(self):
        return str(self)


class OWLDatatypeRestriction(OWLDataRange):
    _hash_idx = 101

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

    def __hash__(self):
        return self._hash_idx * hash(self.datatype) + \
               reduce(lambda l, r: l*r,
                      map(lambda fr: hash(fr), self.facet_restrictions))

    def __str__(self):
        return \
            f'DatatypeRestriction(<{self.datatype}> ' \
            f'{" ".join([str(fr) for fr in self.facet_restrictions])})'

    def __repr__(self):
        return str(self)
