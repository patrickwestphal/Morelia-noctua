from model.objects.property import OWLAnnotationProperty


class OWLAnnotation(object):
    _hash_idx = 3

    def __init__(
            self,
            owl_property: OWLAnnotationProperty,
            value):

        self.owl_property = owl_property
        self.value = value

    def __str__(self):
        return f'Annotation({self.owl_property} {self.value})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, OWLAnnotation):
            return False

        return self.owl_property == other.owl_property and \
            self.value == other.value

    def __hash__(self):
        return self._hash_idx * hash(self.owl_property) + hash(self.value)
