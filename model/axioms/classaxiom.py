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
