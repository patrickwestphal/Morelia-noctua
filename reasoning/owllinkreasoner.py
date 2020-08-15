import logging
import uuid
from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import requests

from model.axioms.classaxiom import OWLSubClassOfAxiom
from model.axioms.declarationaxiom import OWLClassDeclarationAxiom
from model.objects.classexpression import OWLClass, OWLClassExpression
from reasoning import OWLReasoner


def _translate_cls(cls: OWLClass):
    cls_element = Element('owl:Class')
    cls_element.set('IRI', str(cls.iri))

    return cls_element


def _translate_class_expression(ce: OWLClassExpression):
    if isinstance(ce, OWLClass):
        return _translate_cls(ce)
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


def translate_axiom(owl_axiom):
    translators = {
        OWLClassDeclarationAxiom: _translate_owl_class_declaration_axiom,
        OWLSubClassOfAxiom: _translate_owl_subclass_of_axiom
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

    def get_superclasses(self, class_expression):
        raise NotImplementedError()