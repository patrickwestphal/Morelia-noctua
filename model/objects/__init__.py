from abc import ABC

from rdflib import URIRef


class OWLObject(ABC):
    pass


class HasIRI(OWLObject):
    iri = None

    def __hash__(self):
        return hash(self.iri)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False

        else:
            return self.iri == other.iri

    @staticmethod
    def _init_iri(iri_or_iri_str):
        if isinstance(iri_or_iri_str, URIRef):
            return iri_or_iri_str
        else:
            return URIRef(iri_or_iri_str)


class HasOperands(OWLObject):
    operands = None

    def __hash__(self):
        return hash(self.operands)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False

        else:
            return self.operands == other.operands

    @staticmethod
    def _init_operands(operands):
        operand_cls_exprs = set()

        for operand in operands:
            from model.objects.classexpression import OWLClassExpression
            if isinstance(operand, OWLClassExpression):
                operand_cls_exprs.add(operand)

            elif isinstance(operand, URIRef):
                from model.objects.classexpression import OWLClass
                operand_cls_exprs.add(OWLClass(operand))

            else:
                operand_cls_exprs.add(OWLClass(operand))

        return operand_cls_exprs


class HasDatatypeOperands(OWLObject):
    operands = None

    def __hash__(self):
        return hash(self.operands)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False

        else:
            return self.operands == other.operands

    @staticmethod
    def _init_operands(operands):
        datatype_operands = set()

        for operand in operands:
            from model.objects.datarange import OWLDatatype
            if isinstance(operand, OWLDatatype):
                datatype_operands.add(operand)

            elif isinstance(operand, URIRef):
                datatype_operands.add(OWLDatatype(operand))

            else:
                datatype_operands.add(OWLDatatype(operand))

        return datatype_operands
