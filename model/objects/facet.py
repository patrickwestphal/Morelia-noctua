from rdflib import XSD, RDF, Literal, URIRef

from model.objects import OWLObject

LENGTH = XSD.length
MIN_LENGTH = XSD.minLength
MAX_LENGTH = XSD.maxLength
PATTERN = XSD.pattern
MIN_INCLUSIVE = XSD.minInclusive
MIN_EXCLUSIVE = XSD.minExclusive
MAX_INCLUSIVE = XSD.maxInclusive
MAX_EXCLUSIVE = XSD.maxExclusive
TOTAL_DIGITS = XSD.totalDigits
FRACTION_DIGITS = XSD.fractionDigits
LANG_RANGE = URIRef(RDF.uri + 'langRange')


class OWLFacetRestriction(OWLObject):
    _hash_idx = 103

    def __init__(self, facet: URIRef, facet_value: Literal):
        self.facet = facet
        self.facet_value = facet_value

    def __eq__(self, other):
        if not isinstance(other, OWLFacetRestriction):
            return False
        else:
            return self.facet == other.facet \
                   and self.facet_value == other.facet_value

    def __hash__(self):
        return self._hash_idx * hash(self.facet) + hash(self.facet_value)
