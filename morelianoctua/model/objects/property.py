from morelianoctua.model.objects import HasIRI, OWLObject


class OWLProperty(HasIRI):
    """Either OWLAnnotationProperty, OWLDataProperty, or OWLObjectProperty"""

    def __str__(self):
        return f'<{self.iri}>'

    def __repr__(self):
        return str(self)


class OWLObjectPropertyExpression(OWLObject):
    pass


class OWLAnnotationProperty(OWLProperty):
    _hash_idx = 113

    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)

    def __hash__(self):
        return self._hash_idx * hash(self.iri)


class OWLObjectProperty(OWLProperty, OWLObjectPropertyExpression):
    _hash_idx = 127

    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)

    def __hash__(self):
        return self._hash_idx * hash(self.iri)


class OWLObjectInverseOf(OWLObjectPropertyExpression):
    _hash_idx = 131

    def __init__(self, inverse_property: OWLObjectProperty):
        self.inverse_property = inverse_property

    def __eq__(self, other):
        if not isinstance(other, OWLObjectInverseOf):
            return False
        else:
            return self.inverse_property == other.inverse_property

    def __hash__(self):
        return self._hash_idx * hash(self.inverse_property)

    def __repr__(self):
        return f'ObjectInverseOf({self.inverse_property})'


class OWLDataProperty(OWLProperty):
    _hash_idx = 137

    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)

    def __hash__(self):
        return self._hash_idx * hash(self.iri)
