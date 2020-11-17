import logging
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import requests

from model.axioms.assertionaxiom import OWLObjectPropertyAssertionAxiom, \
    OWLClassAssertionAxiom, OWLDataPropertyAssertionAxiom
from model.axioms.classaxiom import OWLSubClassOfAxiom
from model.axioms.declarationaxiom import OWLClassDeclarationAxiom, \
    OWLNamedIndividualDeclarationAxiom, OWLObjectPropertyDeclarationAxiom, \
    OWLDataPropertyDeclarationAxiom, OWLAnnotationPropertyDeclarationAxiom
from model.axioms.owlobjectpropertyaxiom import OWLObjectPropertyRangeAxiom, \
    OWLObjectPropertyDomainAxiom
from model.objects.classexpression import OWLClass, OWLClassExpression, \
    OWLObjectSomeValuesFrom
from parsing.functional import FunctionalSyntaxParser
from reasoning import OWLReasoner


def _translate_cls(cls: OWLClass):
    cls_element = Element('owl:Class')
    cls_element.set('IRI', str(cls.iri))

    return cls_element


def _translate_obj_some_values_from(ce: OWLObjectSomeValuesFrom):
    ex_restriction_element = Element('owl:ObjectSomeValuesFrom')
    role_element = SubElement(ex_restriction_element, 'owl:ObjectProperty')
    role_element.set('IRI', str(ce.property.iri))
    filler_element = _translate_class_expression(ce.filler)
    ex_restriction_element.append(filler_element)

    return ex_restriction_element


def _translate_class_expression(ce: OWLClassExpression):
    if isinstance(ce, OWLClass):
        return _translate_cls(ce)
    elif isinstance(ce, OWLObjectSomeValuesFrom):
        return _translate_obj_some_values_from(ce)
    else:
        raise NotImplementedError('Complex class expressions not supported, '
                                  'yet')


def _translate_owl_class_declaration_axiom(axiom: OWLClassDeclarationAxiom):
    axiom_element = Element('owl:Declaration')
    axiom_element.append(_translate_cls(axiom.cls))

    return axiom_element


def _translate_owl_subclass_of_axiom(axiom: OWLSubClassOfAxiom):
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
        axiom: OWLNamedIndividualDeclarationAxiom):
    # e.g.
    # <owl:NamedIndividual abbreviatedIRI="family:Mary"/>

    axiom_element = Element('owl:NamedIndividual')
    axiom_element.set('IRI', str(axiom.individual.iri))

    return axiom_element


def _translate_owl_obj_property_assertion_axiom(
        axiom: OWLObjectPropertyAssertionAxiom):

    axiom_element = Element('owl:ObjectPropertyAssertion')
    obj_prop_element = SubElement(axiom_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.owl_property.iri))

    subj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    subj_individual_element.set('IRI', str(axiom.subject_individual.iri))

    obj_individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    obj_individual_element.set('IRI', str(axiom.object_individual.iri))

    return axiom_element


def _translate_owl_data_property_assertion_axiom(
        axiom: OWLDataPropertyAssertionAxiom):

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


def _translate_owl_class_assertion_axiom(axiom: OWLClassAssertionAxiom):
    axiom_element = Element('owl:ClassAssertion')
    axiom_element.append(_translate_class_expression(axiom.class_expression))

    individual_element = SubElement(axiom_element, 'owl:NamedIndividual')
    # FIXME: Will cause an error if individual not named
    individual_element.set('IRI', str(axiom.individual.iri))

    return axiom_element


def _translate_owl_object_property_declaration_axiom(
        axiom: OWLObjectPropertyDeclarationAxiom):

    declaration_element = Element('owl:Declaration')
    obj_prop_element = SubElement(declaration_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.obj_property.iri))

    return declaration_element


def _translate_owl_data_property_declaration_axiom(
        axiom: OWLDataPropertyDeclarationAxiom):
    declaration_element = Element('owl:Declaration')
    data_prop_element = SubElement(declaration_element, 'owl:DataProperty')
    data_prop_element.set('IRI', str(axiom.data_property.iri))

    return declaration_element


def _translate_obj_property_range_axiom(axiom: OWLObjectPropertyRangeAxiom):
    obj_prop_range_element = Element('owl:ObjectPropertyRange')
    obj_prop_element = SubElement(obj_prop_range_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.object_property.iri))

    range_element = _translate_class_expression(axiom.range_ce)
    obj_prop_range_element.append(range_element)

    return obj_prop_range_element


def _translate_obj_property_domain_axiom(axiom: OWLObjectPropertyDomainAxiom):
    obj_prop_domain_element = Element('owl:ObjectPropertyDomain')
    obj_prop_element = SubElement(obj_prop_domain_element, 'owl:ObjectProperty')
    obj_prop_element.set('IRI', str(axiom.object_property.iri))

    domain_element = _translate_class_expression(axiom.domain)
    obj_prop_domain_element.append(domain_element)

    return obj_prop_domain_element


def _translate_owl_annotation_property_declaration(
        axiom: OWLAnnotationPropertyDeclarationAxiom):

    declaration_element = Element('owl:Declaration')

    ann_prop_element = SubElement(declaration_element, 'owl:AnnotationProperty')
    ann_prop_element.set('IRI', str(axiom.annotation_property.iri))

    return declaration_element


def translate_axiom(owl_axiom):
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

    def __init__(self, ontology, owllink_server_url):
        self.ontology = ontology
        self.server_url = owllink_server_url

        self.kb_uri = self._init_kb()

    @staticmethod
    def _get_kb_uri():
        return 'http://example.com/' + str(uuid.uuid4())

    @staticmethod
    def _init_request():
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

    def _make_class_expression(self, node: Element):
        if node.tag == '{http://www.w3.org/2002/07/owl#}Class':
            return OWLClass(node.get('IRI'))
        else:
            raise NotImplementedError(f'Node type {node.tag} not supported, '
                                      f'yet')

    def get_classes(self):
        request_element = self._init_request()
        get_all_classes = SubElement(request_element, 'GetAllClasses')
        get_all_classes.set('kb', self.kb_uri)

        response = requests.post(
            self.server_url,
            tostring(request_element))
        etree = fromstring(response.content)

        classes = set()
        for class_node in etree.findall('*/owl:Class', self._prefixes):
            classes.add(self._make_class_expression(class_node))

        return classes

    def get_subclasses(self, class_expression, direct=True):
        request_element = self._init_request()

        get_subclasses_element = SubElement(request_element, 'GetSubClasses')
        get_subclasses_element.set('direct', str(direct).lower())
        get_subclasses_element.set('kb', self.kb_uri)

        get_subclasses_element.append(
            _translate_class_expression(class_expression))

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

    def get_superclasses(self, class_expression, direct=False):
        request_element = self._init_request()

        get_subclasses_element = SubElement(request_element, 'GetSuperClasses')
        get_subclasses_element.set('direct', str(direct).lower())
        get_subclasses_element.set('kb', self.kb_uri)

        get_subclasses_element.append(
            _translate_class_expression(class_expression))

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

