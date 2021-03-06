import logging
import uuid
from typing import Set
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import requests
from rdflib import Literal, XSD

from morelianoctua.model import OWLOntology
from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.axioms.assertionaxiom import \
    OWLObjectPropertyAssertionAxiom, OWLDataPropertyAssertionAxiom, \
    OWLClassAssertionAxiom
from morelianoctua.model.axioms.classaxiom import OWLSubClassOfAxiom, OWLDisjointClassesAxiom
from morelianoctua.model.axioms.declarationaxiom import OWLClassDeclarationAxiom, \
    OWLNamedIndividualDeclarationAxiom, OWLObjectPropertyDeclarationAxiom, \
    OWLDataPropertyDeclarationAxiom, OWLAnnotationPropertyDeclarationAxiom
from morelianoctua.model.axioms.owldatapropertyaxiom import \
    OWLDataPropertyDomainAxiom, OWLDataPropertyRangeAxiom
from morelianoctua.model.axioms.owlobjectpropertyaxiom import \
    OWLObjectPropertyRangeAxiom, OWLObjectPropertyDomainAxiom
from morelianoctua.model.objects.classexpression import OWLClass, \
    OWLObjectSomeValuesFrom, OWLObjectAllValuesFrom, OWLDataSomeValuesFrom, \
    OWLDataAllValuesFrom, OWLDataHasValue, OWLObjectUnionOf, OWLClassExpression
from morelianoctua.model.objects.datarange import OWLDatatype, OWLDataRange
from morelianoctua.model.objects.individual import OWLIndividual, \
    OWLNamedIndividual
from morelianoctua.model.objects.property import OWLObjectProperty, \
    OWLAnnotationProperty, OWLDataProperty, OWLObjectPropertyExpression
from morelianoctua.parsing.functional import FunctionalSyntaxParser
from morelianoctua.reasoning import OWLReasoner


def _translate_cls(cls: OWLClass) -> Element:
    cls_element = Element('owl:Class')
    cls_element.set('IRI', str(cls.iri))

    return cls_element


def _translate_obj_some_values_from(ce: OWLObjectSomeValuesFrom) -> Element:
    ex_restriction_element = Element('owl:ObjectSomeValuesFrom')
    role_element = SubElement(ex_restriction_element, 'owl:ObjectProperty')
    role_element.set('IRI', str(ce.owl_property.iri))
    filler_element = _translate_class_expression(ce.filler)
    ex_restriction_element.append(filler_element)

    return ex_restriction_element


def _translate_obj_all_values_from(ce: OWLObjectAllValuesFrom) -> Element:
    univ_restriction_element = Element('owl:ObjectAllValuesFrom')
    role_element = SubElement(univ_restriction_element, 'owl:ObjectProperty')
    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_class_expression(ce.filler)
    univ_restriction_element.append(filler_element)

    return univ_restriction_element


def _translate_data_some_values_from(ce: OWLDataSomeValuesFrom) -> Element:
    ex_restriction_element = Element('owl:DataSomeValuesFrom')
    role_element = SubElement(ex_restriction_element, 'owl:DataProperty')
    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_data_range(ce.filler)
    ex_restriction_element.append(filler_element)

    return ex_restriction_element


def _translate_data_all_values_from(ce: OWLDataAllValuesFrom) -> Element:
    univ_restriction_element = Element('owl:DataAllValuesFrom')
    role_element = SubElement(univ_restriction_element, 'owl:DataProperty')
    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_data_range(ce.filler)
    univ_restriction_element.append(filler_element)

    return univ_restriction_element


def _translate_data_has_value(ce: OWLDataHasValue) -> Element:
    # e.g.:
    # <owl:DataHasValue>
    #   <owl:DataProperty IRI="http://dl-learner.org/ont#dataprop2"/>
    #   <owl:Literal
    #       xml:lang="en"
    #       datatypeIRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#langString"
    #     >foo</owl:Literal>
    # </owl:DataHasValue>
    #
    # <owl:DataHasValue>
    #   <owl:DataProperty IRI="http://dl-learner.org/ont#dataprop"/>
    #   <owl:Literal
    #       datatypeIRI="http://www.w3.org/2001/XMLSchema#int">42</owl:Literal>
    # </owl:DataHasValue>

    has_value_element = Element('owl:DataHasValue')
    role_element = SubElement(has_value_element, 'owl:DataProperty')
    role_element.set('IRI', str(ce.owl_property.iri))

    value_element = SubElement(has_value_element, 'owl:Literal')
    literal: Literal = ce.value

    value_element.text = str(literal.value)

    if literal.language:
        value_element.set('xml:lang', literal.language)

    if literal.datatype:
        value_element.set('datatypeIRI', str(literal.datatype))

    return has_value_element


def _translate_object_union_of(ce: OWLObjectUnionOf) -> Element:
    # e.g.:
    # <owl:ObjectUnionOf>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls1"/>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls2"/>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls3"/>
    # </owl:ObjectUnionOf>

    union_of_element = Element('owl:ObjectUnionOf')

    for union_ce in ce.operands:
        union_element = _translate_class_expression(union_ce)
        union_of_element.append(union_element)

    return union_of_element


def _translate_datatype(datatype: OWLDatatype) -> Element:
    # <owl:Datatype abbreviatedIRI="xsd:int"/>
    dtype_element = Element('owl:Datatype')
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
    elif isinstance(ce, OWLObjectAllValuesFrom):
        return _translate_obj_all_values_from(ce)
    elif isinstance(ce, OWLDataAllValuesFrom):
        return _translate_data_all_values_from(ce)
    elif isinstance(ce, OWLDataHasValue):
        return _translate_data_has_value(ce)
    elif isinstance(ce, OWLObjectUnionOf):
        return _translate_object_union_of(ce)
    else:
        raise NotImplementedError(f'Complex class expressions of type '
                                  f'{type(ce)} not supported, yet')


def _translate_owl_class_declaration_axiom(
        axiom: OWLClassDeclarationAxiom) -> Element:

    axiom_element = Element('owl:Declaration')
    axiom_element.append(_translate_cls(axiom.cls))

    return axiom_element


def _translate_owl_subclass_of_axiom(axiom: OWLSubClassOfAxiom) -> Element:
    axiom_element = Element('owl:SubClassOf')

    if isinstance(axiom.sub_class, OWLClass):
        sub_cls_element = SubElement(axiom_element, 'owl:Class')
        sub_cls_element.set('IRI', str(axiom.sub_class.iri))

    else:
        sub_cls_element = _translate_class_expression(axiom.sub_class)
        axiom_element.append(sub_cls_element)

    if isinstance(axiom.super_class, OWLClass):
        super_cls_element = SubElement(axiom_element, 'owl:Class')
        super_cls_element.set('IRI', str(axiom.super_class.iri))

    else:
        super_cls_element = _translate_class_expression(axiom.super_class)
        axiom_element.append(super_cls_element)

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

    # e.g.:
    # <owl:DataPropertyAssertion>
    #   <owl:DataProperty IRI="http://dl-learner.org/dprop01"/>
    #   <owl:NamedIndividual IRI="http://dl-learner.org/d285"/>
    #   <owl:Literal datatypeIRI="http://www.w3.org/2001/XMLSchema#boolean">
    #       false
    #   </owl:Literal>
    # </owl:DataPropertyAssertion>

    axiom_element = Element('owl:DataPropertyAssertion')
    obj_prop_element = SubElement(axiom_element, 'owl:DataProperty')
    obj_prop_element.set('IRI', str(axiom.owl_property.iri))

    subj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    subj_individual_element.set('IRI', str(axiom.subject_individual.iri))

    value_literal_element = SubElement(axiom_element, 'owl:Literal')
    value_literal_element.text = str(axiom.value)
    if axiom.value.datatype:
        value_literal_element.set('datatypeIRI', axiom.value.datatype)

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
    obj_prop_element.set('IRI', str(axiom.object_property.iri))

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

    # e.g.:
    # <owl:DataPropertyRange>
    #   <owl:DataProperty IRI="http://dl-learner.org/ont#someDataProperty"/>
    #   <owl:Datatype abbreviatedIRI="xsd:int"/>
    # </owl:DataPropertyRange>
    data_prop_range_element = Element('owl:DataPropertyRange')
    data_prop_element = SubElement(data_prop_range_element, 'owl:DataProperty')
    data_prop_element.set('IRI', str(axiom.data_property.iri))

    range_element = _translate_data_range(axiom.data_range)
    data_prop_range_element.append(range_element)

    return data_prop_range_element


def _translate_disjoint_classes_axiom(
        axiom: OWLDisjointClassesAxiom) -> Element:
    # e.g.:
    # <owl:DisjointClasses>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls1"/>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls2"/>
    #   <owl:Class IRI="http://dl-learner.org/ont#Cls3"/>
    # </owl:DisjointClasses>

    disjoint_classes_element = Element('owl:DisjointClasses')

    for ce in axiom.class_expressions:
        ce_element = _translate_class_expression(ce)
        disjoint_classes_element.append(ce_element)

    return disjoint_classes_element


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
        OWLDisjointClassesAxiom:
            _translate_disjoint_classes_axiom,
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
    # Reasoner and KB management

    def get_description(self):
        raise NotImplementedError()

    def create_kb(self):
        raise NotImplementedError()

    def get_prefixes(self):
        raise NotImplementedError()

    def get_settings(self):
        raise NotImplementedError()

    def set(self):
        raise NotImplementedError()

    def release_kb(self):
        request_element = self._init_request()
        release_kb_element = SubElement(request_element, 'ReleaseKB')
        release_kb_element.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))

        # response.content:
        # <?xml version="1.0" encoding="utf-8"?>
        # <!DOCTYPE ResponseMessage>
        # <ResponseMessage
        #         xmlns="http://www.owllink.org/owllink#"
        #         xml:base="http://www.w3.org/2002/07/owl#"
        #         xmlns:owl="http://www.w3.org/2002/07/owl#"
        #         xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #     <OK/>
        # </ResponseMessage>

    def tell(self):
        raise NotImplementedError()

    def load_ontologies(self):
        raise NotImplementedError()

    def classify(self):
        raise NotImplementedError()

    def realize(self):
        raise NotImplementedError()

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

        # <ResponseMessage xmlns="http://www.owllink.org/owllink#"
        #      xml:base="http://www.owllink.org/owllink"
        #      xmlns:owl="http://www.w3.org/2002/07/owl#"
        #      xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #     <SetOfObjectProperties>
        #         <owl:ObjectProperty IRI="http://dl-learner.org/ont/objProp1"/>
        #         <owl:ObjectProperty IRI="http://dl-learner.org/ont/objProp2"/>
        #         <owl:ObjectProperty IRI="http://dl-learner.org/ont/objProp3"/>
        #     </SetOfObjectProperties>
        # </ResponseMessage>
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
        request_element = self._init_request()

        get_all_datatypes = SubElement(request_element, 'GetAllDatatypes')
        get_all_datatypes.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        # <?xml version="1.0" encoding="UTF-8"?>
        # <ResponseMessage xmlns="http://www.owllink.org/owllink#"
        #      xml:base="http://www.owllink.org/owllink"
        #      xmlns:owl="http://www.w3.org/2002/07/owl#"
        #      xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #     <SetOfDatatypes>
        #         <owl:Datatype abbreviatedIRI="xsd:string"/>
        #         <owl:Datatype abbreviatedIRI="xsd:nonNegativeInteger"/>
        #         <owl:Datatype abbreviatedIRI="xsd:int"/>
        #     </SetOfDatatypes>
        # </ResponseMessage>
        datatypes = set()
        for datatype_node in etree.findall('*/owl:Datatype', self._prefixes):
            dtype_iri = datatype_node.get('IRI')
            if dtype_iri is None:
                dtype_iri = datatype_node.get('abbreviatedIRI')
                prefix, local_part = dtype_iri.split(':', 1)

                namespace = self._prefixes.get(prefix)
                if namespace is None:
                    if prefix.lower() == 'xsd':
                        namespace = str(XSD)
                    else:
                        raise Exception(f'Unknown prefix {prefix}')

                dtype_iri = namespace + local_part
            datatypes.add(OWLDatatype(dtype_iri))

        return datatypes

    def get_all_data_properties(self) -> Set[OWLDataProperty]:
        request_element = self._init_request()

        get_all_data_properties_element = \
            SubElement(request_element, 'GetAllDataProperties')
        get_all_data_properties_element.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        # <ResponseMessage xmlns="http://www.owllink.org/owllink#"
        #      xml:base="http://www.owllink.org/owllink"
        #      xmlns:owl="http://www.w3.org/2002/07/owl#"
        #      xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #     <SetOfDataProperties>
        #         <owl:DataProperty IRI="http://dl-learner.org/ont/dprop1"/>
        #         <owl:DataProperty IRI="http://dl-learner.org/ont/dprop2"/>
        #         <owl:DataProperty IRI="http://dl-learner.org/ont/dprop3"/>
        #     </SetOfDataProperties>
        # </ResponseMessage>

        data_properties = set()
        for dprop_node in etree.findall('*/owl:DataProperty', self._prefixes):
            data_properties.add(OWLDataProperty(dprop_node.get('IRI')))

        return data_properties

    def is_kb_satisfiable(self) -> bool:
        """
        TODO: Implement and document
        """
        request_element = self._init_request()

        is_satisfiable_element = SubElement(request_element, 'IsKBSatisfiable')
        is_satisfiable_element.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        # <ResponseMessage xmlns="http://www.owllink.org/owllink#"
        #      xml:base="http://www.owllink.org/owllink"
        #      xmlns:owl="http://www.w3.org/2002/07/owl#"
        #      xmlns:xsd="http://www.w3.org/2001/XMLSchema#">
        #     <BooleanResponse result="false"/>
        # </ResponseMessage>

        response_elem = \
            etree.find('.//{http://www.owllink.org/owllink#}BooleanResponse')

        is_satisfiable = response_elem.attrib['result'].lower() == 'true'

        return is_satisfiable

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
            direct: bool = False) -> Set[OWLClassExpression]:
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

    def get_classes(self) -> Set[OWLClass]:
        """
        TODO: Implement and document
        """
        return self.get_all_classes()

    def get_object_properties(self):
        return self.get_all_object_properties()

    def get_data_properties(self) -> Set[OWLDataProperty]:
        return self.get_all_data_properties()

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

    def close(self):
        self.release_kb()
