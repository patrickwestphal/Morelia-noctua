from functools import reduce

from model.axioms import OWLAxiom
from model.objects import HasOperands
from model.objects.classexpression import OWLClassExpression, OWLClass


class OWLClassAxiom(OWLAxiom):
    pass


class OWLSubClassOfAxiom(OWLClassAxiom):
    _hash_idx = 139

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

    def __hash__(self):
        tmp = self._hash_idx * hash(self.sub_class) + \
              (self._hash_idx * hash(self.super_class))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLEquivalentClassesAxiom(OWLClassAxiom):
    _hash_idx = 149

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
        tmp = reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda ce: hash(ce), self.class_expressions))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLDisjointClassesAxiom(OWLClassAxiom):
    _hash_idx = 151

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
        tmp = reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda ce: hash(ce), self.class_expressions))

        if self.annotations:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))

        return tmp


class OWLDisjointUnionAxiom(OWLClassAxiom, HasOperands):
    _hash_idx = 157

    def __init__(
            self,
            owl_class: OWLClass,
            class_expressions,
            annotations=None):

        self.owl_class = owl_class
        self.operands = self._init_operands(class_expressions)
        self.annotations = annotations

    def __eq__(self, other):
        if not isinstance(other, OWLDisjointUnionAxiom):
            return False
        else:
            return self.owl_class == other.owl_class \
                   and self.operands == other.operands \
                   and self.annotations == other.annotations

    def __hash__(self):
        tmp = self._hash_idx * hash(self.owl_class) + reduce(
            lambda l, r: self._hash_idx*l+r,
            map(lambda o: hash(o), self.operands))

        if self.operands is not None:
            tmp += reduce(
                lambda l, r: self._hash_idx*l+r,
                map(lambda a: hash(a), self.annotations))
