from itertools import combinations
from typing import Set, Tuple, List

from rdflib import Graph, RDFS, RDF, OWL
from rdflib.term import Identifier, BNode, Literal

from morelianoctua.model import OWLOntology
from morelianoctua.model.axioms.assertionaxiom import OWLClassAssertionAxiom, \
    OWLObjectPropertyAssertionAxiom, OWLDataPropertyAssertionAxiom
from morelianoctua.model.axioms.classaxiom import OWLSubClassOfAxiom, \
    OWLDisjointClassesAxiom
from morelianoctua.model.axioms.declarationaxiom import \
    OWLClassDeclarationAxiom, OWLNamedIndividualDeclarationAxiom, \
    OWLDataPropertyDeclarationAxiom, OWLObjectPropertyDeclarationAxiom
from morelianoctua.model.axioms.owldatapropertyaxiom import \
    OWLDataPropertyRangeAxiom, OWLDataPropertyDomainAxiom
from morelianoctua.model.axioms.owlobjectpropertyaxiom import \
    OWLObjectPropertyRangeAxiom, OWLObjectPropertyDomainAxiom
from morelianoctua.model.objects import HasIRI, OWLObject
from morelianoctua.model.objects.annotation import OWLAnnotation
from morelianoctua.model.objects.classexpression import OWLClass, \
    OWLClassExpression, OWLDataHasValue, OWLObjectSomeValuesFrom, \
    OWLObjectUnionOf
from morelianoctua.model.objects.datarange import OWLDataRange, OWLDatatype
from morelianoctua.model.objects.individual import OWLNamedIndividual
from morelianoctua.model.objects.property import OWLObjectProperty, \
    OWLObjectPropertyExpression


def _build_seq(anchor: BNode, owl_objects: List[OWLObject]):
    first, *rest = owl_objects

    if rest:
        rest_node = BNode()
    else:
        rest_node = RDF.nil

    if isinstance(first, HasIRI):
        first_res = first.iri
    else:
        first_res = first.bnode

    triples = [
        (anchor, RDF.first, first_res),
        (anchor, RDF.rest, rest_node)]

    if rest:
        triples += _build_seq(rest_node, rest)

    return triples


def _seq_converter(ces: List[OWLObject]) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:

    seq_bnode = BNode()
    triples = [(seq_bnode, RDF.type, RDF.List)]

    triples += _build_seq(seq_bnode, ces)

    return seq_bnode, triples


def _obj_property_expression_converter(
        obj_prop_expression: OWLObjectPropertyExpression) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:

    if isinstance(obj_prop_expression, OWLObjectProperty):
        return obj_prop_expression.iri, []
    else:
        raise NotImplementedError(
            'Complex object property expressions not supported, yet')


def _owl_data_has_value_converter(ce: OWLDataHasValue) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:

    ce_bnode = BNode()

    # _:x rdf:type owl:Restriction .
    # _:x rdf:type owl:Class . [opt]
    # _:x owl:onProperty T(ID) .
    # _:x owl:hasValue T(value) .
    aux_triples = [
        (ce_bnode, RDF.type, OWL.Restriction),
        (ce_bnode, RDF.type, OWL.Class),
        (ce_bnode, OWL.onProperty, ce.owl_property.iri),
        (ce_bnode, OWL.hasValue, ce.value)]

    return ce_bnode, aux_triples


def _owl_obj_some_values_from_converter(ce: OWLObjectSomeValuesFrom) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:

    ce_bnode = BNode()
    filler_res, filler_aux_triples = _owl_ce_converter(ce.filler)

    aux_triples = filler_aux_triples[:]

    if not isinstance(ce.owl_property, OWLObjectProperty):
        # FIXME
        raise NotImplementedError(
            'Non-atomic object property expressions not supported, yet')

    # _:x rdf:type owl:Restriction .
    # _:x rdf:type owl:Class . [opt]
    # _:x owl:onProperty T(ID) .
    # _:x owl:someValuesFrom T(required) .
    aux_triples.append((ce_bnode, RDF.type, OWL.Restriction))
    aux_triples.append((ce_bnode, RDF.type, OWL.Class))
    aux_triples.append((ce_bnode, OWL.onProperty, ce.owl_property.iri))
    aux_triples.append((ce_bnode, OWL.someValuesFrom, filler_res))

    return ce_bnode, aux_triples


def _owl_obj_union_of_converter(ce: OWLObjectUnionOf) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:
    union_res = BNode()
    seq_res, seq_triples = _seq_converter([o for o in ce.operands])

    triples = seq_triples[:]

    triples.append((union_res, RDF.type, OWL.Class))
    triples.append((union_res, OWL.unionOf, seq_res))

    return union_res, triples


def _owl_data_range_converter(data_range: OWLDataRange) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:

    if isinstance(data_range, OWLDatatype):
        return data_range.iri, []
    else:
        raise NotImplementedError(f'Data range {data_range} not supported, yet')


def _owl_ce_converter(ce: OWLClassExpression) \
        -> Tuple[Identifier, List[Tuple[Identifier, Identifier, Identifier]]]:
    #           class resource,        auxiliary triples

    if isinstance(ce, OWLClass):
        return ce.iri, []
    elif isinstance(ce, OWLDataHasValue):
        return _owl_data_has_value_converter(ce)
    elif isinstance(ce, OWLObjectSomeValuesFrom):
        return _owl_obj_some_values_from_converter(ce)
    elif isinstance(ce, OWLObjectUnionOf):
        return _owl_obj_union_of_converter(ce)
    else:
        raise NotImplementedError(
            f'class expressions of type {type(ce)} not supported, yet')


def _annotations_converter(annotations: Set[OWLAnnotation]) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:
    raise NotImplementedError('Annotation converter not implemented, yet')


def _owl_sub_class_of_converter(axiom: OWLSubClassOfAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:
    triples = []
    s, aux_triples1 = _owl_ce_converter(axiom.sub_class)
    p = RDFS.subClassOf
    o, aux_triples2 = _owl_ce_converter(axiom.super_class)

    triples += aux_triples1
    triples += aux_triples2
    triples.append((s, p, o))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_class_declaration_converter(axiom: OWLClassDeclarationAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = [(axiom.cls.iri, RDF.type, OWL.Class)]

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_class_assertion_converter(axiom: OWLClassAssertionAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = []

    if not isinstance(axiom.individual, OWLNamedIndividual):
        indiv_term = axiom.individual.bnode
    else:
        indiv_term = axiom.individual.iri

    class_resource, aux_triples = _owl_ce_converter(axiom.class_expression)

    triples += aux_triples
    triples.append((indiv_term, RDF.type, class_resource))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_named_individual_declaration_converter(
        axiom: OWLNamedIndividualDeclarationAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = []

    if not isinstance(axiom.individual, OWLNamedIndividual):
        indiv_term = axiom.individual.bnode
    else:
        indiv_term = axiom.individual.iri

    triples.append((indiv_term, RDF.type, OWL.NamedIndividual))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_disjoint_classes_converter(axiom: OWLDisjointClassesAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = []
    class_resources = []

    for ce in axiom.class_expressions:
        cls_res, aux_triples = _owl_ce_converter(ce)

        triples += aux_triples
        class_resources.append(cls_res)

    for c1, c2 in combinations(class_resources, 2):
        triples.append((c1, OWL.disjointWith, c2))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_data_property_declaration_converter(
        axiom: OWLDataPropertyDeclarationAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = [(axiom.data_property.iri, RDF.type, OWL.DatatypeProperty)]

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_obj_property_range_converter(axiom: OWLObjectPropertyRangeAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = []

    range_cls_res, aux_triples = _owl_ce_converter(axiom.range_ce)

    triples += aux_triples

    if not isinstance(axiom.object_property, OWLObjectProperty):
        raise NotImplementedError(
            'Non-atomic object property expressions not supported, yet')

    triples.append((axiom.object_property.iri, RDFS.range, range_cls_res))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_obj_property_domain_converter(axiom: OWLObjectPropertyDomainAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    triples = []

    domain_cls_res, aux_triples = _owl_ce_converter(axiom.domain)

    triples += aux_triples

    if not isinstance(axiom.object_property, OWLObjectProperty):
        raise NotImplementedError(
            'Non-atomic object property expressions not supported, yet')

    triples.append((axiom.object_property.iri, RDFS.domain, domain_cls_res))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_obj_property_declaration_converter(
        axiom: OWLObjectPropertyDeclarationAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    if not isinstance(axiom.object_property, OWLObjectProperty):
        raise NotImplementedError(
            'Non-atomic object property expressions not supported, yet')

    triples = [
        (axiom.object_property.iri, RDF.type, OWL.ObjectProperty)]

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_data_property_range_converter(axiom: OWLDataPropertyRangeAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    data_range_res, aux_triples = _owl_data_range_converter(axiom.data_range)

    triples = aux_triples[:]

    triples.append((axiom.data_property.iri, RDFS.range, data_range_res))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_data_property_domain_converter(axiom: OWLDataPropertyDomainAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    domain_res, aux_triples = _owl_ce_converter(axiom.domain)

    triples = aux_triples[:]

    triples.append((axiom.data_property.iri, RDFS.domain, domain_res))

    if axiom.annotations:
        triples += _annotations_converter(axiom.annotations)

    return triples


def _owl_obj_property_assertion_converter(
        axiom: OWLObjectPropertyAssertionAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    s = axiom.subject_individual.iri
    p, aux_triples = _obj_property_expression_converter(axiom.owl_property)
    o = axiom.object_individual.iri

    triples = aux_triples[:]
    triples.append((s, p, o))

    return triples


def _owl_data_property_assertion_converter(
        axiom: OWLDataPropertyAssertionAxiom) \
        -> List[Tuple[Identifier, Identifier, Identifier]]:

    s = axiom.subject_individual.iri
    p = axiom.owl_property.iri
    o: Literal = axiom.value

    return [(s, p, o)]


def to_rdf(ontology: OWLOntology) -> Graph:
    g = Graph()

    for axiom in ontology.axioms:
        if isinstance(axiom, OWLSubClassOfAxiom):
            triples = _owl_sub_class_of_converter(axiom)
        elif isinstance(axiom, OWLClassDeclarationAxiom):
            triples = _owl_class_declaration_converter(axiom)
        elif isinstance(axiom, OWLClassAssertionAxiom):
            triples = _owl_class_assertion_converter(axiom)
        elif isinstance(axiom, OWLNamedIndividualDeclarationAxiom):
            triples = _owl_named_individual_declaration_converter(axiom)
        elif isinstance(axiom, OWLDisjointClassesAxiom):
            triples = _owl_disjoint_classes_converter(axiom)
        elif isinstance(axiom, OWLDataPropertyDeclarationAxiom):
            triples = _owl_data_property_declaration_converter(axiom)
        elif isinstance(axiom, OWLObjectPropertyRangeAxiom):
            triples = _owl_obj_property_range_converter(axiom)
        elif isinstance(axiom, OWLObjectPropertyDomainAxiom):
            triples = _owl_obj_property_domain_converter(axiom)
        elif isinstance(axiom, OWLObjectPropertyDeclarationAxiom):
            triples = _owl_obj_property_declaration_converter(axiom)
        elif isinstance(axiom, OWLDataPropertyRangeAxiom):
            triples = _owl_data_property_range_converter(axiom)
        elif isinstance(axiom, OWLDataPropertyDomainAxiom):
            triples = _owl_data_property_domain_converter(axiom)
        elif isinstance(axiom, OWLObjectPropertyAssertionAxiom):
            triples = _owl_obj_property_assertion_converter(axiom)
        elif isinstance(axiom, OWLDataPropertyAssertionAxiom):
            triples = _owl_data_property_assertion_converter(axiom)
        else:
            raise NotImplementedError(
                f'RDF converter for axiom type {type(axiom)} not implemented, '
                f'yet')

        for triple in triples:
            g.add(triple)

    return g
