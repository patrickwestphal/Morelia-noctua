from model.axioms import OWLAxiom
from model.objects.classexpression import OWLClassExpression


class OWLClassAxiom(OWLAxiom):
    pass


class OWLSubClassOfAxiom(OWLClassAxiom):
    def __init__(
            self,
            sub_class: OWLClassExpression,
            super_class: OWLClassExpression,
            annotations=None):

        self.sub_class = sub_class
        self.super_class = super_class
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLSubClassOfAxiom):
            return False
        else:
            return self.sub_class == other.sub_class \
                   and self.super_class == other.super_class \
                   and self.annotations == other.annotations


class OWLEquivalentClassesAxiom(OWLClassAxiom):
    _hash_idx = 7

    def __init__(self, class_expressions, annotations=None):
        self.class_expressions = class_expressions
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLEquivalentClassesAxiom):
            return False
        else:
            return self.class_expressions == other.class_expressions \
                   and self.annotations == other.annotations

    def __hash__(self):
        return self._hash_idx * hash(self.class_expressions) \
               + hash(self.annotations)


class OWLDisjointClassesAxiom(OWLClassAxiom):
    _hash_idx = 17

    def __init__(self, class_expressions, annotations=None):
        self.class_expressions = class_expressions
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDisjointClassesAxiom):
            return False
        else:
            return self.class_expressions == other.class_expressions \
                   and self.annotations == other.annotations

    def __hash__(self):
        return self._hash_idx * hash(self.class_expressions) + \
               hash(self.annotations)
