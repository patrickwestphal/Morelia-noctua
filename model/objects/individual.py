from rdflib import BNode

from model.objects import HasIRI, OWLObject


class OWLIndividual(OWLObject):
    pass


class OWLNamedIndividual(OWLIndividual, HasIRI):
    _hash_idx = 107

    def __init__(self, individual_iri_or_str):
        self.iri = self._init_iri(individual_iri_or_str)

    def __hash__(self):
        return self._hash_idx * hash(self.iri)


class OWLAnonymousIndividual(OWLIndividual):
    _hash_idx = 109

    def __init__(self, bnode_or_bnode_id):
        if isinstance(bnode_or_bnode_id, BNode):
            self.bnode = bnode_or_bnode_id
        else:
            assert isinstance(bnode_or_bnode_id, str)

            if bnode_or_bnode_id.startswith('_:'):
                bnode_or_bnode_id = bnode_or_bnode_id[2:]
            self.bnode = BNode(bnode_or_bnode_id)

    def __eq__(self, other):
        if not isinstance(other, OWLAnonymousIndividual):
            return False
        else:
            return self.bnode == other.bnode

    def __hash__(self):
        return self._hash_idx * hash(self.bnode)
