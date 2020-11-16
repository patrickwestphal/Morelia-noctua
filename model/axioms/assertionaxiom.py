from functools import reduce

from model.axioms import OWLAxiom
from model.objects.classexpression import OWLClassExpression
from model.objects.individual import OWLIndividual


class OWLClassAssertionAxiom(OWLAxiom):
    _hash_idx = 229

    def __init__(
            self, individual: OWLIndividual,
            class_expression: OWLClassExpression,
            annotations=None):

        self.individual = individual
        self.class_expression = class_expression
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLClassAssertionAxiom):
            return False

        else:
            is_equal = \
                self.individual == other.individual and \
                self.class_expression == other.class_expression

            if self.annotations or other.annotations:
                is_equal = is_equal and self.annotations == other.annotations

            return is_equal

    def __hash__(self):
        tmp = \
            self._hash_idx * hash(self.individual) + hash(self.class_expression)

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx * l + r,
                map(lambda a: hash(a), self.annotations))

        return tmp
