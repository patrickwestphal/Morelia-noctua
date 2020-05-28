from model.objects import HasIRI, OWLObject


class OWLProperty(HasIRI):
    """Either OWLAnnotationProperty, OWLDataProperty, or OWLObjectProperty"""

    def __str__(self):
        return f'<{self.iri}>'

    def __repr__(self):
        return str(self)


class OWLObjectPropertyExpression(OWLObject):
    pass


class OWLAnnotationProperty(OWLProperty):
    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)


class OWLObjectProperty(OWLProperty, OWLObjectPropertyExpression):
    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)


class OWLObjectInverseOf(OWLObjectPropertyExpression):
    def __init__(self, inverse_property: OWLObjectProperty):
        self.inverse_property = inverse_property

    def __eq__(self, other):
        if not isinstance(other, OWLObjectInverseOf):
            return False
        else:
            return self.inverse_property == other.inverse_property


class OWLDataProperty(OWLProperty):
    def __init__(self, property_iri_or_iri_str):
        self.iri = self._init_iri(property_iri_or_iri_str)
