import logging
import uuid
from typing import Set
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import requests
from rdflib import Literal, XSD

from model import OWLOntology
from model.axioms import OWLAxiom
from model.axioms.assertionaxiom import OWLObjectPropertyAssertionAxiom, \
    OWLClassAssertionAxiom, OWLDataPropertyAssertionAxiom
from model.axioms.classaxiom import OWLSubClassOfAxiom
from model.axioms.declarationaxiom import OWLClassDeclarationAxiom, \
    OWLNamedIndividualDeclarationAxiom, OWLObjectPropertyDeclarationAxiom, \
    OWLDataPropertyDeclarationAxiom, OWLAnnotationPropertyDeclarationAxiom
from model.axioms.owldatapropertyaxiom import OWLDataPropertyDomainAxiom, \
    OWLDataPropertyRangeAxiom
from model.axioms.owlobjectpropertyaxiom import OWLObjectPropertyRangeAxiom, \
    OWLObjectPropertyDomainAxiom
from model.objects.classexpression import OWLClass, OWLClassExpression, \
    OWLObjectSomeValuesFrom, OWLDataSomeValuesFrom
from model.objects.datarange import OWLDatatype, OWLDataRange
from model.objects.individual import OWLNamedIndividual, OWLIndividual
from model.objects.property import OWLObjectProperty, OWLAnnotationProperty, \
    OWLDataProperty, OWLObjectPropertyExpression
from parsing.functional import FunctionalSyntaxParser
from reasoning import OWLReasoner


def _translate_cls(cls: OWLClass) -> Element:
    cls_element = Element('owl:Class')
    cls_element.set('IRI', str(cls.iri))

    return cls_element


def _translate_obj_some_values_from(ce: OWLObjectSomeValuesFrom) -> Element:
    ex_restriction_element = Element('owl:ObjectSomeValuesFrom')
    role_element = SubElement(ex_restriction_element, 'owl:ObjectProperty')
    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_class_expression(ce.filler)
    ex_restriction_element.append(filler_element)

    return ex_restriction_element


def _translate_data_some_values_from(ce: OWLDataSomeValuesFrom) -> Element:
    ex_restriction_element = Element('owl:DataSomeValuesFrom')
    role_element = SubElement(ex_restriction_element, 'owl:DataProperty')

    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_data_range(ce.filler)
    ex_restriction_element.append(filler_element)

    return ex_restriction_element


def _translate_datatype(datatype: OWLDatatype) -> Element:
    dtype_element = Element('Datatype')
    dtype_element.set('IRI', datatype.iri)

    return dtype_element


def _translate_data_range(data_range: OWLDataRange) -> Element:
    if isinstance(data_range, OWLDatatype):
        return _translate_datatype(data_range)
    else:
        # TODO:
        # OWLDataIntesectionOf
        # OWLDataUnionOf
        # OWLDataComplementOf
        # OWLDataOneOf
        # OWLDatatypeRestriction
        raise NotImplementedError('Data range type not supported, yet')


def _translate_class_expression(ce: OWLClassExpression) -> Element:
    if isinstance(ce, OWLClass):
        return _translate_cls(ce)
    elif isinstance(ce, OWLObjectSomeValuesFrom):
        return _translate_obj_some_values_from(ce)
    elif isinstance(ce, OWLDataSomeValuesFrom):
        return _translate_data_some_values_from(ce)
    else:
        raise NotImplementedError('Complex class expressions not supported, '
                                  'yet')


def _translate_owl_class_declaration_axiom(
        axiom: OWLClassDeclarationAxiom) -> Element:

    axiom_element = Element('owl:Declaration')
    axiom_element.append(_translate_cls(axiom.cls))

    return axiom_element


def _translate_owl_subclass_of_axiom(axiom: OWLSubClassOfAxiom) -> Element:
    axiom_element = Element('owl:SubClassOf')

    sub_cls_element = SubElement(axiom_element, 'owl:Class')

    if isinstance(axiom.sub_class, OWLClass):
        sub_cls_element.set('IRI', str(axiom.sub_class.iri))

    else:
        raise NotImplementedError('OWLLink translation for non-named classes '
                                  'not implemented, yet')

    super_cls_element = SubElement(axiom_element, 'owl:Class')

    if isinstance(axiom.super_class, OWLClass):
        super_cls_element.set('IRI', str(axiom.super_class.iri))

    else:
        raise NotImplementedError('OWLLink translation for non-named classes '
                                  'not implemented, yet')
    return axiom_element


def _translate_owl_named_individual_declaration_axiom(
        axiom: OWLNamedIndividualDeclarationAxiom) -> Element:
    # e.g.
    # <owl:NamedIndividual abbreviatedIRI="family:Mary"/>

    axiom_element = Element('owl:NamedIndividual')
    axiom_element.set('IRI', str(axiom.individual.iri))

    return axiom_element


def _translate_owl_obj_property_assertion_axiom(
        axiom: OWLObjectPropertyAssertionAxiom) -> Element:

    axiom_element = Element('owl:ObjectPropertyAssertion')
    obj_prop_element = SubElement(axiom_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.owl_property.iri))

    subj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    subj_individual_element.set('IRI', str(axiom.subject_individual.iri))

    obj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    obj_individual_element.set('IRI', str(axiom.object_individual.iri))

    return axiom_element


def _translate_owl_data_property_assertion_axiom(
        axiom: OWLDataPropertyAssertionAxiom) -> Element:

    axiom_element = Element('owl:DataPropertyAssertion')
    obj_prop_element = SubElement(axiom_element, 'owl:DataProperty')
    obj_prop_element.set('IRI', str(axiom.owl_property.iri))

    subj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    subj_individual_element.set('IRI', str(axiom.subject_individual.iri))

    value_literal_element = SubElement(axiom_element, 'owl:Literal')
    value_literal_element.text = str(axiom.value)
    if axiom.value.datatype:
        value_literal_element.set('datatype', axiom.value.datatype)

    return axiom_element


def _translate_owl_class_assertion_axiom(
        axiom: OWLClassAssertionAxiom) -> Element:

    axiom_element = Element('owl:ClassAssertion')
    axiom_element.append(_translate_class_expression(axiom.class_expression))

    individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    # FIXME: Will cause an error if individual not named
    individual_element.set('IRI', str(axiom.individual.iri))

    return axiom_element


def _translate_owl_object_property_declaration_axiom(
        axiom: OWLObjectPropertyDeclarationAxiom) -> Element:

    declaration_element = Element('owl:Declaration')
    obj_prop_element = SubElement(declaration_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.obj_property.iri))

    return declaration_element


def _translate_owl_data_property_declaration_axiom(
        axiom: OWLDataPropertyDeclarationAxiom) -> Element:

    declaration_element = Element('owl:Declaration')
    data_prop_element = SubElement(declaration_element, 'owl:DataProperty')
    data_prop_element.set('IRI', str(axiom.data_property.iri))

    return declaration_element


def _translate_obj_property_range_axiom(
        axiom: OWLObjectPropertyRangeAxiom) -> Element:

    obj_prop_range_element = Element('owl:ObjectPropertyRange')
    obj_prop_element = SubElement(obj_prop_range_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.object_property.iri))

    range_element = _translate_class_expression(axiom.range_ce)
    obj_prop_range_element.append(range_element)

    return obj_prop_range_element


def _translate_obj_property_domain_axiom(
        axiom: OWLObjectPropertyDomainAxiom) -> Element:

    obj_prop_domain_element = Element('owl:ObjectPropertyDomain')
    obj_prop_element = SubElement(obj_prop_domain_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.object_property.iri))

    domain_element = _translate_class_expression(axiom.domain)
    obj_prop_domain_element.append(domain_element)

    return obj_prop_domain_element


def _translate_owl_annotation_property_declaration(
        axiom: OWLAnnotationPropertyDeclarationAxiom) -> Element:

    declaration_element = Element('owl:Declaration')

    ann_prop_element = SubElement(declaration_element, 'owl:AnnotationProperty')
    ann_prop_element.set('IRI', str(axiom.annotation_property.iri))

    return declaration_element


def _translate_owl_data_property_domain_axiom(
        axiom: OWLDataPropertyDomainAxiom) -> Element:

    data_prop_domain_element = Element('owl:DataPropertyDomain')
    data_prop_element = SubElement(data_prop_domain_element, 'owl:DataProperty')
    data_prop_element.set('IRI', str(axiom.data_property.iri))

    domain_element = _translate_class_expression(axiom.domain)
    data_prop_domain_element.append(domain_element)

    return data_prop_domain_element


def _translate_owl_data_property_range_axiom(
        axiom: OWLDataPropertyRangeAxiom) -> Element:

    data_prop_range_element = Element('owl:DataPropertyRange')
    data_prop_element = SubElement(data_prop_range_element, 'owl:DataProperty')
    data_prop_element.set('IRI', str(axiom.data_property.iri))

    range_element = _translate_data_range(axiom.data_range)
    data_prop_range_element.append(range_element)

    return data_prop_range_element


def translate_axiom(owl_axiom) -> Element:
    translators = {
        OWLClassDeclarationAxiom: _translate_owl_class_declaration_axiom,
        OWLSubClassOfAxiom: _translate_owl_subclass_of_axiom,
        OWLNamedIndividualDeclarationAxiom:
            _translate_owl_named_individual_declaration_axiom,
        OWLObjectPropertyAssertionAxiom:
            _translate_owl_obj_property_assertion_axiom,
        OWLDataPropertyAssertionAxiom:
            _translate_owl_data_property_assertion_axiom,
        OWLClassAssertionAxiom:
            _translate_owl_class_assertion_axiom,
        OWLObjectPropertyDeclarationAxiom:
            _translate_owl_object_property_declaration_axiom,
        OWLDataPropertyDeclarationAxiom:
            _translate_owl_data_property_declaration_axiom,
        OWLObjectPropertyRangeAxiom:
            _translate_obj_property_range_axiom,
        OWLObjectPropertyDomainAxiom:
            _translate_obj_property_domain_axiom,
        OWLAnnotationPropertyDeclarationAxiom:
            _translate_owl_annotation_property_declaration,
        OWLDataPropertyDomainAxiom:
            _translate_owl_data_property_domain_axiom,
        OWLDataPropertyRangeAxiom:
            _translate_owl_data_property_range_axiom,
    }

    translator = translators.get(type(owl_axiom))

    if translator is None:
        raise NotImplementedError(f'No translator implementation found '
                                  f'for {owl_axiom}')
    else:
        return translator(owl_axiom)


class OWLLinkReasoner(OWLReasoner):
    _prefixes = {
        'owllink': 'http://www.owllink.org/owllink#',
        'owl': 'http://www.w3.org/2002/07/owl#'
    }

    def __init__(self, ontology: OWLOntology, owllink_server_url: str):
        self.ontology = ontology
        self.server_url = owllink_server_url

        self.kb_uri = self._init_kb()

    @staticmethod
    def _get_kb_uri():
        return 'http://example.com/' + str(uuid.uuid4())

    @staticmethod
    def _init_request() -> Element:
        request_element = Element('RequestMessage')
        request_element.set('xmlns', 'http://www.owllink.org/owllink#')
        request_element.set('xmlns:owl', 'http://www.w3.org/2002/07/owl#')

        return request_element

    def _init_kb(self):
        request_element = self._init_request()

        kb_element = SubElement(request_element, 'CreateKB')
        kb_uri = self._get_kb_uri()
        kb_element.set('kb', kb_uri)

        tell_element = SubElement(request_element, 'Tell')
        tell_element.set('kb', kb_uri)

        for axiom in self.ontology.axioms:
            axiom_element = translate_axiom(axiom)
            tell_element.append(axiom_element)

        response = requests.post(
            self.server_url,
            tostring(request_element))

        logging.debug(response.content.decode('utf-8'))

        return kb_uri

    def _make_class_expression(self, node: Element) -> OWLClassExpression:
        if node.tag == '{http://www.w3.org/2002/07/owl#}Class':
            return OWLClass(node.get('IRI'))
        else:
            raise NotImplementedError(f'Node type {node.tag} not supported, '
                                      f'yet')

    def _make_individual(self, node: Element) -> OWLIndividual:
        if node.tag == '{http://www.w3.org/2002/07/owl#}NamedIndividual':
            return OWLNamedIndividual(node.get('IRI'))
        else:
            raise NotImplementedError(
                f'Node type {node.tag} not supported, '
                f'yet')

    ###########################################################################
    # Entailment Queries, KB Entities, and KB Status
    #

    def is_entailed(self, axiom: OWLAxiom) -> bool:
        request_element = self._init_request()

        is_entailed_element = SubElement(request_element, 'IsEntailed')
        is_entailed_element.set('kb', self.kb_uri)

        is_entailed_element.append(translate_axiom(axiom))

        response = requests.post(
            self.server_url,
            tostring(request_element))

        # Example response:
        # <?xml version="1.0" encoding="utf-8"?>
        # <!DOCTYPE ResponseMessage>
        # <ResponseMessage
        #     xmlns="http://www.owllink.org/owllink#"
        #     xml:base="http://www.w3.org/2002/07/owl#"
        #     xmlns:owl="http://www.w3.org/2002/07/owl#"
        #     xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #
        #     <BooleanResponse result="false"/>
        # </ResponseMessage>
        etree = fromstring(response.content)

        response_elem = \
            etree.find('.//{http://www.owllink.org/owllink#}BooleanResponse')

        is_entailed = response_elem.attrib['result'].lower() == 'true'

        return is_entailed

    def is_entailed_direct(self, axiom: OWLAxiom) -> bool:
        """
        TODO: Implement and document

        :param axiom:
        :return:
        """
        raise NotImplementedError()

    def get_all_object_properties(self) -> Set[OWLObjectProperty]:
        """
        TODO: Implement and document

        :return:
        """
        request_element = self._init_request()

        get_all_object_properties = \
            SubElement(request_element, 'GetAllObjectProperties')
        get_all_object_properties.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        object_properties = set()
        for oprop_node in etree.findall('*/owl:ObjectProperty', self._prefixes):
            object_properties.add(OWLObjectProperty(oprop_node.get('IRI')))

        return object_properties

    def get_all_individuals(self) -> Set[OWLNamedIndividual]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_all_classes(self) -> Set[OWLClass]:
        request_element = self._init_request()
        get_all_classes = SubElement(request_element, 'GetAllClasses')
        get_all_classes.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        classes = set()
        for class_node in etree.findall('*/owl:Class', self._prefixes):
            classes.add(OWLClass(class_node.get('IRI')))

        return classes

    def get_all_annotation_properties(self) -> Set[OWLAnnotationProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_all_datatypes(self) -> Set[OWLDatatype]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_all_data_properties(self) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def is_kb_satisfiable(self) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def is_kb_consistently_declared(self) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_kb_language(self) -> str:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    ###########################################################################
    # Queries about Classes and Properties
    #

    def is_class_satisfiable(self, ce: OWLClassExpression) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_disjoint_classes(self, ce: OWLClassExpression) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_sub_classes(
            self,
            ce: OWLClassExpression,
            direct: bool = False) -> Set[OWLClassExpression]:

        request_element = self._init_request()

        get_subclasses_element = SubElement(request_element, 'GetSubClasses')
        get_subclasses_element.set('direct', str(direct).lower())
        get_subclasses_element.set('kb', self.kb_uri)

        get_subclasses_element.append(
            _translate_class_expression(ce))

        response = requests.post(
            self.server_url,
            tostring(request_element))

        etree = fromstring(response.content)
        subclasses = set()
        for synset_node in etree.findall(
                '*/owllink:ClassSynset', self._prefixes):

            for ce_node in synset_node.getchildren():
                subclasses.add(self._make_class_expression(ce_node))

        return subclasses

    def get_super_classes(
            self,
            ce: OWLClassExpression,
            direct: bool = False) -> Set[OWLClassExpression]:

        request_element = self._init_request()

        get_subclasses_element = SubElement(request_element, 'GetSuperClasses')
        get_subclasses_element.set('direct', str(direct).lower())
        get_subclasses_element.set('kb', self.kb_uri)

        get_subclasses_element.append(
            _translate_class_expression(ce))

        response = requests.post(
            self.server_url,
            tostring(request_element))

        etree = fromstring(response.content)
        superclasses = set()
        for synset_node in etree.findall(
                '*/owllink:ClassSynset', self._prefixes):

            for ce_node in synset_node.getchildren():
                superclasses.add(self._make_class_expression(ce_node))

        return superclasses

    def get_equivalent_classes(self, ce: OWLClassExpression) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_sub_class_hierarchy(self) -> dict:
        """
        TODO: Think about return type, implement and document
        """
        raise NotImplementedError()

    def is_object_property_satisfiable(
            self, pe: OWLObjectPropertyExpression) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_sub_object_properties(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_super_object_properties(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_equivalent_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_disjoint_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        """

    def get_sub_object_property_hierarchy(self) -> dict:
        """
        TODO: Think about return type, implement and document
        """
        raise NotImplementedError()

    def is_data_property_satisfiable(
            self, data_property: OWLDataProperty) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_sub_data_properties(
            self,
            data_property: OWLDataProperty,
            direct: bool = False) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_super_data_properties(
            self,
            data_property: OWLDataProperty,
            direct: bool = True) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_equivalent_data_properties(
            self,
            data_property: OWLDataProperty) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_disjoint_data_properties(
            self,
            data_property: OWLDataProperty) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_sub_data_property_hierarchy(self) -> dict:
        """
        TODO: Think about return type, implement and document
        """
        raise NotImplementedError()

    ###########################################################################
    # Queries about Individuals
    #

    def get_types(
            self,
            individual: OWLNamedIndividual,
            direct: bool = False) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_different_individuals(
            self,
            individual: OWLNamedIndividual) -> Set[OWLNamedIndividual]:
        """
        TODO: Implement and ducument
        """
        raise NotImplementedError()

    def get_same_individuals(
            self,
            individual: OWLNamedIndividual) -> Set[OWLNamedIndividual]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_object_properties_of_source(
            self,
            source_individual: OWLIndividual) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLObjectProperty instead of ...Expression, OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_object_properties_between(
            self,
            source_individual: OWLIndividual,
            target_individual: OWLIndividual) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLObjectProperty instead of ...Expression, OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_object_properties_of_target(
            self,
            target_individual: OWLIndividual) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLObjectProperty instead of ...Expression, OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_data_properties_of_source(
            self, source_individual: OWLIndividual) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_data_properties_between(
            self,
            source_individual: OWLIndividual,
            target_literal: Literal) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_data_properties_of_literal(
            self, target_literal: Literal) -> Set[OWLDataProperty]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_instances(
            self,
            class_expression: OWLClassExpression,
            direct: bool = False) -> Set[OWLIndividual]:

        request_element = self._init_request()

        get_instances_element = SubElement(request_element, 'GetInstances')
        get_instances_element.set('kb', self.kb_uri)

        get_instances_element.append(
            _translate_class_expression(class_expression))

        response = requests.post(self.server_url, tostring(request_element))

        etree = fromstring(response.content)
        instances = set()

        for synset_node in etree.findall(
                '*/owllink:IndividualSynset', self._prefixes):

            for individual_node in synset_node.getchildren():
                instances.add(self._make_individual(individual_node))

        return instances

    def get_object_property_targets(
            self, pe: OWLObjectPropertyExpression) -> Set[OWLIndividual]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLObjectProperty instead of ...Expression, OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_object_property_source(
            self, pe: OWLObjectPropertyExpression) -> Set[OWLIndividual]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLObjectProperty instead of ...Expression, OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    def get_data_property_targets(self, data_property: OWLDataProperty) -> Set[Literal]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_data_property_sources(self, data_property: OWLDataProperty) -> Set[OWLIndividual]:
        """
        TODO: Implement and document
        FIXME: Types might be wrong (OWLNamedIndividual instead of OWLIndividual)
        """
        raise NotImplementedError()

    ###########################################################################
    # Remaining OWLReasoner method implementations
    #
    def get_data_property_domains(
            self,
            data_property: OWLDataProperty,
            direct: bool = False) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_data_property_values(
            self,
            individual: OWLNamedIndividual,
            data_property: OWLDataProperty) -> Set[Literal]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_inverse_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_object_property_domains(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_object_property_ranges(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_object_property_values(
            self, individual: OWLNamedIndividual,
            pe: OWLObjectPropertyExpression) -> Set[OWLNamedIndividual]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_root_ontology(self) -> OWLOntology:
        return self.ontology

    def get_unsatisfiable_classes(self) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def is_consistent(self) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def is_satisfiable(self, ce: OWLClassExpression) -> bool:
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_classes(self):
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_object_properties(self):
        return self.get_all_object_properties()

    def get_data_properties(self):
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_annotation_properties(self):
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_literals(self):
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

    def get_datatypes(self):
        """
        TODO: Implement and document
        """
        raise NotImplementedError()

