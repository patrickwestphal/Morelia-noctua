from rdflib import Graph


class OWLOntology(object):
    default_prefix_dummy = 'DEFAULT'

    def __init__(
            self,
            prefix_declarations: dict,
            axioms,
            ontology_iri=None,
            version_iri=None,
            annotations=None):

        self.prefixes = prefix_declarations
        self.axioms = axioms
        self.iri = ontology_iri
        self.version_iri = version_iri

        if annotations is not None:
            self.annotations = annotations
        else:
            self.annotations = []

    def as_rdf_graph(self) -> Graph:
        from morelianoctua.util.converters.rdfconverter import to_rdf
        return to_rdf(self)
