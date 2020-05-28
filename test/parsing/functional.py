import unittest

from rdflib import URIRef, Literal, XSD, BNode

import model
from model import OWLOntology
from model.axioms.classaxiom import OWLSubClassOfAxiom, \
    OWLEquivalentClassesAxiom
from model.objects.annotation import OWLAnnotation
from model.objects.classexpression import OWLClass, OWLObjectIntersectionOf, \
    OWLObjectUnionOf, OWLObjectComplementOf, OWLObjectOneOf, \
    OWLObjectSomeValuesFrom, OWLObjectAllValuesFrom, OWLObjectHasValue, \
    OWLObjectHasSelf, OWLObjectMinCardinality, OWLObjectMaxCardinality, \
    OWLObjectExactCardinality, OWLDataSomeValuesFrom, OWLDataAllValuesFrom, \
    OWLDataHasValue, OWLDataMinCardinality, OWLDataMaxCardinality, \
    OWLDataExactCardinality
from model.objects.datarange import OWLDataIntersectionOf, OWLDataComplementOf, \
    OWLDatatype, OWLDataOneOf, OWLDatatypeRestriction
from model.objects.facet import OWLFacetRestriction
from model.objects.individual import OWLAnonymousIndividual, OWLNamedIndividual
from model.objects.property import OWLAnnotationProperty, OWLObjectInverseOf, \
    OWLObjectProperty, OWLDataProperty
from parsing.functional import FunctionalSyntaxParser


class TestFunctionalSyntaxParser(unittest.TestCase):
    def test_iri(self):
        iri_str_1 = '<http://example.com#foo?bar>'
        iri_1 = URIRef('http://example.com#foo?bar')
        iri_str_2 = 'ex:foo'
        iri_2 = URIRef('http://example.com#foo')
        iri_str_3 = ":foo"
        iri_3 = URIRef('http://ex.org#foo')
        iri_str_4 = 'foo'
        iri_4 = URIRef('http://ex.org#foo')

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://ex.org#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(iri_1, parser.iri.parseString(iri_str_1)[0])
        self.assertEqual(iri_2, parser.iri.parseString(iri_str_2)[0])
        self.assertEqual(iri_3, parser.iri.parseString(iri_str_3)[0])
        self.assertEqual(iri_4, parser.iri.parseString(iri_str_4)[0])

    def test_literal(self):
        lit_str_1 = '"this is a plain literal"'
        lit_1 = Literal('this is a plain literal')
        lit_str_2 = '"Das ist ein deutsches Literal"@de'
        lit_2 = Literal('Das ist ein deutsches Literal', 'de')
        lit_str_3 = '"this is a typed literal"^^xsd:string'
        lit_3 = Literal('this is a typed literal', None, XSD.string)
        lit_str_4 = '"this is a typed literal"^^' \
                    '<http://www.w3.org/2001/XMLSchema#string>'
        lit_4 = lit_3
        lit_str_5 = '"23"'
        lit_5 = Literal('23')
        lit_str_6 = '"23"^^xsd:int'
        lit_6 = Literal('23', None, XSD.int)
        lit_str_7 = '"23"^^<http://www.w3.org/2001/XMLSchema#int>'
        lit_7 = lit_6

        prefixes = {'xsd': 'http://www.w3.org/2001/XMLSchema#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(lit_1, parser.literal.parseString(lit_str_1)[0])
        self.assertEqual(lit_2, parser.literal.parseString(lit_str_2)[0])
        self.assertEqual(lit_3, parser.literal.parseString(lit_str_3)[0])
        self.assertEqual(lit_4, parser.literal.parseString(lit_str_4)[0])
        self.assertEqual(lit_5, parser.literal.parseString(lit_str_5)[0])
        self.assertEqual(lit_6, parser.literal.parseString(lit_str_6)[0])
        self.assertEqual(lit_7, parser.literal.parseString(lit_str_7)[0])

    def test_annotation(self):
        ann_str_1 = 'Annotation(rdfs:comment "Lalalala")'
        ann_1 = OWLAnnotation(
            OWLAnnotationProperty(
                'http://www.w3.org/2000/01/rdf-schema#comment'),
            Literal('Lalalala'))

        ann_str_2 = 'Annotation(rdfs:comment "Lalalala"@de)'
        ann_2 = OWLAnnotation(
            OWLAnnotationProperty(
                'http://www.w3.org/2000/01/rdf-schema#comment'),
            Literal('Lalalala', 'de'))

        ann_str_3 = 'Annotation(ex:foo ex:some_res)'
        ann_3 = OWLAnnotation(
            OWLAnnotationProperty('http://example.com#foo'),
            URIRef('http://example.com#some_res'))

        ann_str_4 = 'Annotation(ex:foo _:anon23)'
        ann_4 = OWLAnnotation(
            OWLAnnotationProperty('http://example.com#foo'),
            OWLAnonymousIndividual('anon23'))

        prefixes = {
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'ex': 'http://example.com#'}

        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(ann_1, parser.annotation.parseString(ann_str_1)[0])
        self.assertEqual(ann_2, parser.annotation.parseString(ann_str_2)[0])
        self.assertEqual(ann_3, parser.annotation.parseString(ann_str_3)[0])
        self.assertEqual(ann_4, parser.annotation.parseString(ann_str_4)[0])

    def test_anonymous_individual(self):
        individual_str_1 = '_:23'
        individual_1 = OWLAnonymousIndividual(BNode('23'))

        individual_str_2 = '_:abc'
        individual_2 = OWLAnonymousIndividual(BNode('abc'))

        parser = FunctionalSyntaxParser()

        self.assertEqual(
            individual_1,
            parser.anonymous_individual.parseString(individual_str_1)[0])
        self.assertEqual(
            individual_2,
            parser.anonymous_individual.parseString(individual_str_2)[0])

    def test_owl_class(self):
        cls_str_1 = '<http://example.com#SomeCls>'
        cls_str_2 = 'ex:SomeCls'
        cls_str_3 = ':SomeCls'
        cls_str_4 = 'SomeCls'

        expected_cls = OWLClass('http://example.com#SomeCls')

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(expected_cls, parser.class_.parseString(cls_str_1)[0])
        self.assertEqual(expected_cls, parser.class_.parseString(cls_str_2)[0])
        self.assertEqual(expected_cls, parser.class_.parseString(cls_str_3)[0])
        self.assertEqual(expected_cls, parser.class_.parseString(cls_str_4)[0])

    def test_object_intersection_of(self):
        intersection_str_1 = \
            'ObjectIntersectionOf(' \
            '<http://example.com#SomeCls1> ' \
            '<http://example.com#SomeCls2> ' \
            '<http://example.com#SomeCls3> ' \
            '<http://example.com#SomeCls4>)'

        intersection_str_2 = \
            'ObjectIntersectionOf(SomeCls1 :SomeCls2 ex:SomeCls3 SomeCls4)'

        intersection = OWLObjectIntersectionOf(
            OWLClass('http://example.com#SomeCls1'),
            OWLClass('http://example.com#SomeCls2'),
            OWLClass('http://example.com#SomeCls3'),
            OWLClass('http://example.com#SomeCls4'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            intersection,
            parser.object_intersection_of.parseString(intersection_str_1)[0])

        self.assertEqual(
            intersection,
            parser.object_intersection_of.parseString(intersection_str_2)[0])

    def test_object_union_of(self):
        union_str_1 = \
            'ObjectUnionOf(' \
            '<http://example.com#SomeCls1> ' \
            '<http://example.com#SomeCls2> ' \
            '<http://example.com#SomeCls3> ' \
            '<http://example.com#SomeCls4>)'

        union_str_2 = \
            'ObjectUnionOf(SomeCls1 :SomeCls2 ex:SomeCls3 SomeCls4)'

        union = OWLObjectUnionOf(
            OWLClass('http://example.com#SomeCls1'),
            OWLClass('http://example.com#SomeCls2'),
            OWLClass('http://example.com#SomeCls3'),
            OWLClass('http://example.com#SomeCls4'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            union,
            parser.object_union_of.parseString(union_str_1)[0])

        self.assertEqual(
            union,
            parser.object_union_of.parseString(union_str_2)[0])

    def test_obj_complement_of(self):
        compl_of_str_1 = 'ObjectComplementOf(<http://example.com#SomeCls1>)'
        compl_of_str_2 = 'ObjectComplementOf(:SomeCls1)'
        compl_of_str_3 = \
            'ObjectComplementOf(' \
            'ObjectUnionOf(SomeCls1 :SomeCls2 ex:SomeCls3 SomeCls4))'

        complement_1 = OWLObjectComplementOf(
            OWLClass('http://example.com#SomeCls1'))

        union = OWLObjectUnionOf(
            OWLClass('http://example.com#SomeCls1'),
            OWLClass('http://example.com#SomeCls2'),
            OWLClass('http://example.com#SomeCls3'),
            OWLClass('http://example.com#SomeCls4'))
        complement_2 = OWLObjectComplementOf(union)

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            complement_1,
            parser.object_complement_of.parseString(compl_of_str_1)[0])
        self.assertEqual(
            complement_1,
            parser.object_complement_of.parseString(compl_of_str_2)[0])
        self.assertEqual(
            complement_2,
            parser.object_complement_of.parseString(compl_of_str_3)[0])

    def test_object_one_of(self):
        obj_one_of_str_1 =\
            'ObjectOneOf(' \
            '<http://example.com#indiv_a> ' \
            '<http://example.com#indiv_b> ' \
            '<http://example.com#indiv_b> ' \
            '<http://example.com#indiv_c> ' \
            '<http://example.com#indiv_d>)'

        obj_one_of_str_2 = \
            'ObjectOneOf(' \
            'ex:indiv_a ex:indiv_b ex:indiv_b ex:indiv_c ex:indiv_d)'

        obj_one_of_str_3 = \
            'ObjectOneOf(indiv_a indiv_b indiv_b indiv_c indiv_d)'

        obj_one_of_1 = OWLObjectOneOf(
            OWLNamedIndividual('http://example.com#indiv_a'),
            OWLNamedIndividual('http://example.com#indiv_b'),
            OWLNamedIndividual('http://example.com#indiv_c'),
            OWLNamedIndividual('http://example.com#indiv_d'))

        obj_one_of_str_4 = \
            'ObjectOneOf(' \
            '_:23 ' \
            'indiv_a ' \
            'indiv_b ' \
            'indiv_b ' \
            'indiv_c ' \
            'indiv_d ' \
            '_:42 ' \
            '_:abcd)'

        obj_one_of_2 = OWLObjectOneOf(
            OWLAnonymousIndividual(BNode('23')),
            OWLNamedIndividual('http://example.com#indiv_a'),
            OWLNamedIndividual('http://example.com#indiv_b'),
            OWLNamedIndividual('http://example.com#indiv_c'),
            OWLNamedIndividual('http://example.com#indiv_d'),
            OWLAnonymousIndividual('_:42'),
            OWLAnonymousIndividual(BNode('abcd')))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_one_of_1, parser.object_one_of.parseString(obj_one_of_str_1)[0])
        self.assertEqual(
            obj_one_of_1, parser.object_one_of.parseString(obj_one_of_str_2)[0])
        self.assertEqual(
            obj_one_of_1, parser.object_one_of.parseString(obj_one_of_str_3)[0])
        self.assertEqual(
            obj_one_of_2, parser.object_one_of.parseString(obj_one_of_str_4)[0])

    def test_inverse_obj_property(self):
        inv_obj_prop_str_1 = 'ObjectInverseOf(<http://example.com#obj_prop>)'
        inv_obj_prop_str_2 = 'ObjectInverseOf(:obj_prop)'
        inv_obj_prop_str_3 = 'ObjectInverseOf(obj_prop)'
        inv_obj_prop_str_4 = 'ObjectInverseOf(ex:obj_prop)'

        inv_obj_prop_1 = OWLObjectInverseOf(
            OWLObjectProperty('http://example.com#obj_prop'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            inv_obj_prop_1,
            parser.inverse_obj_prop.parseString(inv_obj_prop_str_1)[0])
        self.assertEqual(
            inv_obj_prop_1,
            parser.inverse_obj_prop.parseString(inv_obj_prop_str_2)[0])
        self.assertEqual(
            inv_obj_prop_1,
            parser.inverse_obj_prop.parseString(inv_obj_prop_str_3)[0])
        self.assertEqual(
            inv_obj_prop_1,
            parser.inverse_obj_prop.parseString(inv_obj_prop_str_4)[0])

    def test_obj_some_values_from(self):
        obj_some_vals_from_str_1 = \
            'ObjectSomeValuesFrom( ' \
            '<http://example.com#obj_prop> <http://example.com#Cls32> )'
        obj_some_vals_from_str_2 = 'ObjectSomeValuesFrom(obj_prop Cls32)'
        obj_some_vals_from_str_3 = 'ObjectSomeValuesFrom(:obj_prop :Cls32)'
        obj_some_vals_from_str_4 = 'ObjectSomeValuesFrom(ex:obj_prop ex:Cls32)'

        obj_some_vals_from_1 = OWLObjectSomeValuesFrom(
            OWLObjectProperty('http://example.com#obj_prop'),
            OWLClass('http://example.com#Cls32'))

        obj_some_vals_from_str_5 = \
            'ObjectSomeValuesFrom(' \
            'ex:obj_prop ObjectIntersectionOf(ex:Cls32 ex:Cls33 ex:Cls34 ))'
        obj_some_vals_from_2 = \
            OWLObjectSomeValuesFrom(
                OWLObjectProperty('http://example.com#obj_prop'),
                OWLObjectIntersectionOf(
                    OWLClass('http://example.com#Cls32'),
                    OWLClass('http://example.com#Cls33'),
                    OWLClass('http://example.com#Cls34')))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_some_vals_from_1,
            parser.object_some_values_from.parseString(
                obj_some_vals_from_str_1)[0])
        self.assertEqual(
            obj_some_vals_from_1,
            parser.object_some_values_from.parseString(
                obj_some_vals_from_str_2)[0])
        self.assertEqual(
            obj_some_vals_from_1,
            parser.object_some_values_from.parseString(
                obj_some_vals_from_str_3)[0])
        self.assertEqual(
            obj_some_vals_from_1,
            parser.object_some_values_from.parseString(
                obj_some_vals_from_str_4)[0])

        self.assertEqual(
            obj_some_vals_from_2,
            parser.object_some_values_from.parseString(
                obj_some_vals_from_str_5)[0])

    def test_obj_all_vals_from(self):
        obj_all_vals_from_str_1 = \
            'ObjectAllValuesFrom( ' \
            '<http://example.com#obj_prop> <http://example.com#Cls32> )'
        obj_all_vals_from_str_2 = 'ObjectAllValuesFrom(obj_prop Cls32)'
        obj_all_vals_from_str_3 = 'ObjectAllValuesFrom(:obj_prop :Cls32)'
        obj_all_vals_from_str_4 = 'ObjectAllValuesFrom(ex:obj_prop ex:Cls32)'

        obj_all_vals_from_1 = OWLObjectAllValuesFrom(
            OWLObjectProperty('http://example.com#obj_prop'),
            OWLClass('http://example.com#Cls32'))

        obj_all_vals_from_str_5 = \
            'ObjectAllValuesFrom(' \
            'ex:obj_prop ObjectOneOf(ex:indivA ex:indivB ex:indivC))'
        obj_all_vals_from_2 = \
            OWLObjectAllValuesFrom(
                OWLObjectProperty('http://example.com#obj_prop'),
                OWLObjectOneOf(
                    OWLNamedIndividual('http://example.com#indivA'),
                    OWLNamedIndividual('http://example.com#indivB'),
                    OWLNamedIndividual('http://example.com#indivC')))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_all_vals_from_1,
            parser.object_all_values_from.parseString(
                obj_all_vals_from_str_1)[0])
        self.assertEqual(
            obj_all_vals_from_1,
            parser.object_all_values_from.parseString(
                obj_all_vals_from_str_2)[0])
        self.assertEqual(
            obj_all_vals_from_1,
            parser.object_all_values_from.parseString(
                obj_all_vals_from_str_3)[0])
        self.assertEqual(
            obj_all_vals_from_1,
            parser.object_all_values_from.parseString(
                obj_all_vals_from_str_4)[0])

        self.assertEqual(
            obj_all_vals_from_2,
            parser.object_all_values_from.parseString(
                obj_all_vals_from_str_5)[0])

    def test_obj_has_value(self):
        obj_has_val_str_1 = \
            'ObjectHasValue(' \
            '<http://example.com#obj_prop> ' \
            '<http://example.com#indivA> )'

        obj_has_val_str_2 = 'ObjectHasValue(ex:obj_prop ex:indivA)'
        obj_has_val_str_3 = 'ObjectHasValue(obj_prop indivA)'

        obj_has_value_1 = OWLObjectHasValue(
            OWLObjectProperty('http://example.com#obj_prop'),
            OWLNamedIndividual('http://example.com#indivA'))

        obj_has_val_str_4 = 'ObjectHasValue(obj_prop _:23)'

        obj_has_value_2 = OWLObjectHasValue(
            OWLObjectProperty('http://example.com#obj_prop'),
            OWLAnonymousIndividual('23'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_has_value_1,
            parser.object_has_value.parseString(obj_has_val_str_1)[0])

        self.assertEqual(
            obj_has_value_1,
            parser.object_has_value.parseString(obj_has_val_str_2)[0])

        self.assertEqual(
            obj_has_value_1,
            parser.object_has_value.parseString(obj_has_val_str_3)[0])

        self.assertEqual(
            obj_has_value_2,
            parser.object_has_value.parseString(obj_has_val_str_4)[0])

    def test_obj_has_self(self):
        obj_has_self_str_1 = 'ObjectHasSelf(<http://example.com#obj_prop>)'
        obj_has_self_str_2 = 'ObjectHasSelf(ex:obj_prop)'
        obj_has_self_str_3 = 'ObjectHasSelf(obj_prop)'

        obj_has_self_1 = \
            OWLObjectHasSelf(OWLObjectProperty('http://example.com#obj_prop'))

        obj_has_self_str_4 = \
            'ObjectHasSelf(ObjectInverseOf(<http://example.com#obj_prop>))'
        obj_has_self_str_5 = 'ObjectHasSelf(ObjectInverseOf(ex:obj_prop))'
        obj_has_self_str_6 = 'ObjectHasSelf(ObjectInverseOf(obj_prop))'

        obj_has_self_2 = \
            OWLObjectHasSelf(
                OWLObjectInverseOf(
                    OWLObjectProperty('http://example.com#obj_prop')))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_has_self_1,
            parser.object_has_self.parseString(obj_has_self_str_1)[0])

        self.assertEqual(
            obj_has_self_1,
            parser.object_has_self.parseString(obj_has_self_str_2)[0])

        self.assertEqual(
            obj_has_self_1,
            parser.object_has_self.parseString(obj_has_self_str_3)[0])

        self.assertEqual(
            obj_has_self_2,
            parser.object_has_self.parseString(obj_has_self_str_4)[0])

        self.assertEqual(
            obj_has_self_2,
            parser.object_has_self.parseString(obj_has_self_str_5)[0])

        self.assertEqual(
            obj_has_self_2,
            parser.object_has_self.parseString(obj_has_self_str_6)[0])

    def test_obj_min_cardinality(self):
        obj_min_cardinality_str_1 = \
            'ObjectMinCardinality(23 <http://example.com#obj_prop>)'
        obj_min_cardinality_str_2 = 'ObjectMinCardinality(23 ex:obj_prop)'
        obj_min_cardinality_str_3 = 'ObjectMinCardinality(23 obj_prop)'

        obj_min_cardinality_1 = \
            OWLObjectMinCardinality(
                OWLObjectProperty('http://example.com#obj_prop'), 23)

        obj_min_cardinality_str_4 = \
            'ObjectMinCardinality(' \
            '23 <http://example.com#obj_prop> <http://example.com#SomeCls>)'
        obj_min_cardinality_str_5 = \
            'ObjectMinCardinality(23 ex:obj_prop ex:SomeCls)'
        obj_min_cardinality_str_6 = 'ObjectMinCardinality(23 obj_prop SomeCls)'

        obj_min_cardinality_2 = \
            OWLObjectMinCardinality(
                OWLObjectProperty('http://example.com#obj_prop'),
                23,
                OWLClass('http://example.com#SomeCls'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_min_cardinality_1,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_1)[0])

        self.assertEqual(
            obj_min_cardinality_1,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_2)[0])

        self.assertEqual(
            obj_min_cardinality_1,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_3)[0])

        self.assertEqual(
            obj_min_cardinality_2,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_4)[0])

        self.assertEqual(
            obj_min_cardinality_2,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_5)[0])

        self.assertEqual(
            obj_min_cardinality_2,
            parser.object_min_cardinality.parseString(
                obj_min_cardinality_str_6)[0])

    def test_obj_max_cardinality(self):
        obj_max_cardinality_str_1 = \
            'ObjectMaxCardinality(23 <http://example.com#obj_prop>)'
        obj_max_cardinality_str_2 = 'ObjectMaxCardinality(23 ex:obj_prop)'
        obj_max_cardinality_str_3 = 'ObjectMaxCardinality(23 obj_prop)'

        obj_max_cardinality_1 = \
            OWLObjectMaxCardinality(
                OWLObjectProperty('http://example.com#obj_prop'), 23)

        obj_max_cardinality_str_4 = \
            'ObjectMaxCardinality(' \
            '23 <http://example.com#obj_prop> <http://example.com#SomeCls>)'
        obj_max_cardinality_str_5 = \
            'ObjectMaxCardinality(23 ex:obj_prop ex:SomeCls)'
        obj_max_cardinality_str_6 = 'ObjectMaxCardinality(23 obj_prop SomeCls)'

        obj_max_cardinality_2 = \
            OWLObjectMaxCardinality(
                OWLObjectProperty('http://example.com#obj_prop'),
                23,
                OWLClass('http://example.com#SomeCls'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_max_cardinality_1,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_1)[0])

        self.assertEqual(
            obj_max_cardinality_1,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_2)[0])

        self.assertEqual(
            obj_max_cardinality_1,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_3)[0])

        self.assertEqual(
            obj_max_cardinality_2,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_4)[0])

        self.assertEqual(
            obj_max_cardinality_2,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_5)[0])

        self.assertEqual(
            obj_max_cardinality_2,
            parser.object_max_cardinality.parseString(
                obj_max_cardinality_str_6)[0])

    def test_obj_exact_cardinality(self):
        obj_exact_cardinality_str_1 = \
            'ObjectExactCardinality(23 <http://example.com#obj_prop>)'
        obj_exact_cardinality_str_2 = 'ObjectExactCardinality(23 ex:obj_prop)'
        obj_exact_cardinality_str_3 = 'ObjectExactCardinality(23 obj_prop)'

        obj_exact_cardinality_1 = \
            OWLObjectExactCardinality(
                OWLObjectProperty('http://example.com#obj_prop'), 23)

        obj_exact_cardinality_str_4 = \
            'ObjectExactCardinality(' \
            '23 <http://example.com#obj_prop> <http://example.com#SomeCls>)'
        obj_exact_cardinality_str_5 = \
            'ObjectExactCardinality(23 ex:obj_prop ex:SomeCls)'
        obj_exact_cardinality_str_6 = \
            'ObjectExactCardinality(23 obj_prop SomeCls)'

        obj_exact_cardinality_2 = \
            OWLObjectExactCardinality(
                OWLObjectProperty('http://example.com#obj_prop'),
                23,
                OWLClass('http://example.com#SomeCls'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            obj_exact_cardinality_1,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_1)[0])

        self.assertEqual(
            obj_exact_cardinality_1,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_2)[0])

        self.assertEqual(
            obj_exact_cardinality_1,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_3)[0])

        self.assertEqual(
            obj_exact_cardinality_2,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_4)[0])

        self.assertEqual(
            obj_exact_cardinality_2,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_5)[0])

        self.assertEqual(
            obj_exact_cardinality_2,
            parser.object_exact_cardinality.parseString(
                obj_exact_cardinality_str_6)[0])

    def test_data_intersection_of(self):
        data_intersection_str_1 = \
            'DataIntersectionOf(' \
            '<http://example.com#dtype1> ' \
            '<http://example.com#dtype2> ' \
            '<http://example.com#dtype3> ' \
            '<http://example.com#dtype4>)'

        data_intersection_str_2 =\
            'DataIntersectionOf(ex:dtype1 ex:dtype2 ex:dtype3 ex:dtype4)'
        data_intersection_str_3 =\
            'DataIntersectionOf(dtype1 dtype2 dtype3 dtype4)'

        data_intersection_1 = \
            OWLDataIntersectionOf(
                OWLDatatype('http://example.com#dtype1'),
                OWLDatatype('http://example.com#dtype2'),
                OWLDatatype('http://example.com#dtype3'),
                OWLDatatype('http://example.com#dtype4'))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_intersection_1,
            parser.data_intersection_of.parseString(data_intersection_str_1)[0])

        self.assertEqual(
            data_intersection_1,
            parser.data_intersection_of.parseString(data_intersection_str_2)[0])

        self.assertEqual(
            data_intersection_1,
            parser.data_intersection_of.parseString(data_intersection_str_3)[0])

    def test_data_complement_of(self):
        data_complement_str_1 = 'DataComplementOf(<http://example.com#dtype1>)'
        data_complement_str_2 = 'DataComplementOf(ex:dtype1)'
        data_complement_str_3 = 'DataComplementOf(dtype1)'

        data_complement_1 = \
            OWLDataComplementOf(OWLDatatype('http://example.com#dtype1'))

        data_complement_str_4 = \
            'DataComplementOf(' \
            'DataIntersectionOf(ex:dtype1 ex:dtype2 ex:dtype3 ex:dtype4))'

        data_complement_2 = \
            OWLDataComplementOf(
                OWLDataIntersectionOf(
                    OWLDatatype('http://example.com#dtype1'),
                    OWLDatatype('http://example.com#dtype2'),
                    OWLDatatype('http://example.com#dtype3'),
                    OWLDatatype('http://example.com#dtype4')))

        prefixes = {
            'ex': 'http://example.com#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_complement_1,
            parser.data_complement_of.parseString(data_complement_str_1)[0])

        self.assertEqual(
            data_complement_1,
            parser.data_complement_of.parseString(data_complement_str_2)[0])

        self.assertEqual(
            data_complement_1,
            parser.data_complement_of.parseString(data_complement_str_3)[0])

        self.assertEqual(
            data_complement_2,
            parser.data_complement_of.parseString(data_complement_str_4)[0])

    def test_data_one_of(self):
        data_one_of_str_1 = \
            'DataOneOf("23"^^xsd:int "42"^^xsd:int "23.45"^^xsd:double)'

        data_one_of_1 = OWLDataOneOf(
            Literal(23, None, XSD.int),
            Literal(42, None, XSD.int),
            Literal(23.45, None, XSD.double))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_one_of_1,
            parser.data_one_of.parseString(data_one_of_str_1)[0])

    def test_datatype_restriction(self):
        datatype_restriction_str_1 = \
            'DatatypeRestriction(<http://www.w3.org/2001/XMLSchema#string> ' \
            '<http://www.w3.org/2001/XMLSchema#minLength> ' \
            '"5"^^<http://www.w3.org/2001/XMLSchema#int> ' \
            '<http://www.w3.org/2001/XMLSchema#maxLength> ' \
            '"9"^^<http://www.w3.org/2001/XMLSchema#int>)'

        datatype_restriction_str_2 = \
            'DatatypeRestriction(xsd:string ' \
            'xsd:minLength "5"^^xsd:int xsd:maxLength "9"^^xsd:int)'

        datatype_restriction_1 = OWLDatatypeRestriction(
            OWLDatatype(XSD.string),
            {
                OWLFacetRestriction(
                    model.objects.facet.MIN_LENGTH, Literal(5, None, XSD.int)),
                OWLFacetRestriction(
                    model.objects.facet.MAX_LENGTH, Literal(9, None, XSD.int))
            })

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            datatype_restriction_1,
            parser.datatype_restriction.parseString(
                datatype_restriction_str_1)[0])

        self.assertEqual(
            datatype_restriction_1,
            parser.datatype_restriction.parseString(
                datatype_restriction_str_2)[0])

    def test_data_some_values_from(self):
        data_some_values_from_str_1 = \
            'DataSomeValuesFrom(' \
            '<http://example.com#dprop01> ' \
            '<http://www.w3.org/2001/XMLSchema#int>)'

        data_some_values_from_str_2 = 'DataSomeValuesFrom(ex:dprop01 xsd:int)'
        data_some_values_from_str_3 = 'DataSomeValuesFrom(dprop01 xsd:int)'

        data_some_values_from_1 = OWLDataSomeValuesFrom(
            OWLDataProperty('http://example.com#dprop01'),
            OWLDatatype(XSD.int))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_some_values_from_1,
            parser.data_some_values_from.parseString(
                data_some_values_from_str_1)[0])

        self.assertEqual(
            data_some_values_from_1,
            parser.data_some_values_from.parseString(
                data_some_values_from_str_2)[0])

        self.assertEqual(
            data_some_values_from_1,
            parser.data_some_values_from.parseString(
                data_some_values_from_str_3)[0])

    def test_data_all_values_from(self):
        data_all_values_from_str_1 = \
            'DataAllValuesFrom(' \
            '<http://example.com#dprop01> ' \
            '<http://www.w3.org/2001/XMLSchema#int>)'

        data_all_values_from_str_2 = 'DataAllValuesFrom(ex:dprop01 xsd:int)'
        data_all_values_from_str_3 = 'DataAllValuesFrom(dprop01 xsd:int)'

        data_all_values_from_1 = OWLDataAllValuesFrom(
            OWLDataProperty('http://example.com#dprop01'),
            OWLDatatype(XSD.int))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_all_values_from_1,
            parser.data_all_values_from.parseString(
                data_all_values_from_str_1)[0])

        self.assertEqual(
            data_all_values_from_1,
            parser.data_all_values_from.parseString(
                data_all_values_from_str_2)[0])

        self.assertEqual(
            data_all_values_from_1,
            parser.data_all_values_from.parseString(
                data_all_values_from_str_3)[0])

    def test_data_has_value(self):
        data_has_value_str_1 = \
            'DataHasValue(' \
            '<http://example.com#dprop1> ' \
            '"23"^^<http://www.w3.org/2001/XMLSchema#int>)'

        data_has_value_str_2 = 'DataHasValue(ex:dprop1 "23"^^xsd:int)'
        data_has_value_str_3 = 'DataHasValue(dprop1 "23"^^xsd:int)'

        data_has_value_1 = OWLDataHasValue(
            OWLDataProperty('http://example.com#dprop1'),
            Literal(23, None, XSD.int))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_has_value_1,
            parser.data_has_value.parseString(data_has_value_str_1)[0])

        self.assertEqual(
            data_has_value_1,
            parser.data_has_value.parseString(data_has_value_str_2)[0])

        self.assertEqual(
            data_has_value_1,
            parser.data_has_value.parseString(data_has_value_str_3)[0])

    def test_data_min_cardinality(self):
        data_min_cardinality_str_1 = \
            'DataMinCardinality(23 <http://example.com#dprop1>)'

        data_min_cardinality_str_2 = 'DataMinCardinality(23 ex:dprop1)'
        data_min_cardinality_str_3 = 'DataMinCardinality(23 dprop1)'

        data_min_cardinality_1 = OWLDataMinCardinality(
            OWLDataProperty('http://example.com#dprop1'), 23)

        data_min_cardinality_str_4 = \
            'DataMinCardinality(23 ' \
            '<http://example.com#dprop1> ' \
            '<http://www.w3.org/2001/XMLSchema#date>)'

        data_min_cardinality_str_5 = 'DataMinCardinality(23 ex:dprop1 xsd:date)'
        data_min_cardinality_str_6 = 'DataMinCardinality(23 dprop1 xsd:date)'

        data_min_cardinality_2 = OWLDataMinCardinality(
            OWLDataProperty('http://example.com#dprop1'),
            23,
            OWLDatatype(XSD.date))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_min_cardinality_1,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_1)[0])

        self.assertEqual(
            data_min_cardinality_1,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_2)[0])

        self.assertEqual(
            data_min_cardinality_1,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_3)[0])

        self.assertEqual(
            data_min_cardinality_2,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_4)[0])

        self.assertEqual(
            data_min_cardinality_2,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_5)[0])

        self.assertEqual(
            data_min_cardinality_2,
            parser.data_min_cardinality.parseString(
                data_min_cardinality_str_6)[0])

    def test_data_max_cardinality(self):
        data_max_cardinality_str_1 = \
            'DataMaxCardinality(23 <http://example.com#dprop1>)'

        data_max_cardinality_str_2 = 'DataMaxCardinality(23 ex:dprop1)'
        data_max_cardinality_str_3 = 'DataMaxCardinality(23 dprop1)'

        data_max_cardinality_1 = OWLDataMaxCardinality(
            OWLDataProperty('http://example.com#dprop1'), 23)

        data_max_cardinality_str_4 = \
            'DataMaxCardinality(23 ' \
            '<http://example.com#dprop1> ' \
            '<http://www.w3.org/2001/XMLSchema#date>)'

        data_max_cardinality_str_5 = 'DataMaxCardinality(23 ex:dprop1 xsd:date)'
        data_max_cardinality_str_6 = 'DataMaxCardinality(23 dprop1 xsd:date)'

        data_max_cardinality_2 = OWLDataMaxCardinality(
            OWLDataProperty('http://example.com#dprop1'),
            23,
            OWLDatatype(XSD.date))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_max_cardinality_1,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_1)[0])

        self.assertEqual(
            data_max_cardinality_1,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_2)[0])

        self.assertEqual(
            data_max_cardinality_1,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_3)[0])

        self.assertEqual(
            data_max_cardinality_2,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_4)[0])

        self.assertEqual(
            data_max_cardinality_2,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_5)[0])

        self.assertEqual(
            data_max_cardinality_2,
            parser.data_max_cardinality.parseString(
                data_max_cardinality_str_6)[0])

    def test_data_exact_cardinality(self):
        data_exact_cardinality_str_1 = \
            'DataExactCardinality(23 <http://example.com#dprop1>)'

        data_exact_cardinality_str_2 = 'DataExactCardinality(23 ex:dprop1)'
        data_exact_cardinality_str_3 = 'DataExactCardinality(23 dprop1)'

        data_exact_cardinality_1 = OWLDataExactCardinality(
            OWLDataProperty('http://example.com#dprop1'), 23)

        data_exact_cardinality_str_4 = \
            'DataExactCardinality(23 ' \
            '<http://example.com#dprop1> ' \
            '<http://www.w3.org/2001/XMLSchema#date>)'

        data_exact_cardinality_str_5 = \
            'DataExactCardinality(23 ex:dprop1 xsd:date)'
        data_exact_cardinality_str_6 = \
            'DataExactCardinality(23 dprop1 xsd:date)'

        data_exact_cardinality_2 = OWLDataExactCardinality(
            OWLDataProperty('http://example.com#dprop1'),
            23,
            OWLDatatype(XSD.date))

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            data_exact_cardinality_1,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_1)[0])

        self.assertEqual(
            data_exact_cardinality_1,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_2)[0])

        self.assertEqual(
            data_exact_cardinality_1,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_3)[0])

        self.assertEqual(
            data_exact_cardinality_2,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_4)[0])

        self.assertEqual(
            data_exact_cardinality_2,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_5)[0])

        self.assertEqual(
            data_exact_cardinality_2,
            parser.data_exact_cardinality.parseString(
                data_exact_cardinality_str_6)[0])

    def test_sub_class_of_axiom(self):
        sub_cls_of_str_1 = \
            'SubClassOf(<http://example.com#Cls1> <http://example.com#Cls2>)'
        sub_cls_of_str_2 = 'SubClassOf(ex:Cls1 ex:Cls2)'
        sub_cls_of_str_3 = 'SubClassOf(Cls1 Cls2)'

        sub_cls = OWLClass('http://example.com#Cls1')
        super_cls = OWLClass('http://example.com#Cls2')

        sub_cls_of_1 = OWLSubClassOfAxiom(sub_cls, super_cls)

        annotations = {
            OWLAnnotation(
                OWLAnnotationProperty('http://example.com#annProp1'),
                Literal('Some literal', 'en')),
            OWLAnnotation(
                OWLAnnotationProperty('http://example.com#annProp2'),
                URIRef('http://example.com#some_uri'))}

        sub_cls_of_2 = OWLSubClassOfAxiom(sub_cls, super_cls, annotations)

        sub_cls_of_str_4 = \
            'SubClassOf(' \
            'Annotation(<http://example.com#annProp1> "Some literal"@en) ' \
            'Annotation(' \
            '<http://example.com#annProp2> <http://example.com#some_uri>) ' \
            '<http://example.com#Cls1> <http://example.com#Cls2>)'

        sub_cls_of_str_5 = \
            'SubClassOf(' \
            'Annotation(ex:annProp1 "Some literal"@en) ' \
            'Annotation(ex:annProp2 ex:some_uri) ' \
            'ex:Cls1 ex:Cls2)'

        sub_cls_of_str_6 = \
            'SubClassOf(' \
            'Annotation(annProp1 "Some literal"@en) ' \
            'Annotation(annProp2 some_uri) ' \
            'Cls1 Cls2)'

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            sub_cls_of_1,
            parser.sub_class_of.parseString(sub_cls_of_str_1)[0])

        self.assertEqual(
            sub_cls_of_1,
            parser.sub_class_of.parseString(sub_cls_of_str_2)[0])

        self.assertEqual(
            sub_cls_of_1,
            parser.sub_class_of.parseString(sub_cls_of_str_3)[0])

        self.assertEqual(
            sub_cls_of_2,
            parser.sub_class_of.parseString(sub_cls_of_str_4)[0])

        self.assertEqual(
            sub_cls_of_2,
            parser.sub_class_of.parseString(sub_cls_of_str_5)[0])

        self.assertEqual(
            sub_cls_of_2,
            parser.sub_class_of.parseString(sub_cls_of_str_6)[0])

    def test_equivalent_classes_axiom(self):
        equivalent_classes_str_1 = \
            'EquivalentClasses(' \
            '<http://example.com#Cls1> ' \
            'DataSomeValuesFrom(<http://example.com#dprop1> ' \
            'DatatypeRestriction(<http://www.w3.org/2001/XMLSchema#integer> ' \
            '<http://www.w3.org/2001/XMLSchema#maxExclusive> ' \
            '"20"^^<http://www.w3.org/2001/XMLSchema#integer>)))'

        equivalent_classes_str_2 = \
            'EquivalentClasses(' \
            'ex:Cls1 ' \
            'DataSomeValuesFrom(ex:dprop1 ' \
            'DatatypeRestriction(xsd:integer ' \
            'xsd:maxExclusive "20"^^xsd:integer)))'

        equivalent_classes_str_3 = \
            'EquivalentClasses(' \
            'Cls1 ' \
            'DataSomeValuesFrom(dprop1 ' \
            'DatatypeRestriction(xsd:integer ' \
            'xsd:maxExclusive "20"^^xsd:integer)))'

        equivalent_classes_1 = OWLEquivalentClassesAxiom({
            OWLClass('http://example.com#Cls1'),
            OWLDataSomeValuesFrom(
                OWLDataProperty('http://example.com#dprop1'),
                OWLDatatypeRestriction(
                    OWLDatatype(XSD.integer),
                    {
                        OWLFacetRestriction(
                            XSD.maxExclusive,
                            Literal(20, None, XSD.integer))}))})

        equivalent_classes_str_4 = \
            'EquivalentClasses(' \
            'Annotation(<http://example.com#ann> "some annotation"@en)' \
            '<http://example.com#Cls1> ' \
            'DataSomeValuesFrom(<http://example.com#dprop1> ' \
            'DatatypeRestriction(<http://www.w3.org/2001/XMLSchema#integer> ' \
            '<http://www.w3.org/2001/XMLSchema#maxExclusive> ' \
            '"20"^^<http://www.w3.org/2001/XMLSchema#integer>)))'

        equivalent_classes_2 = OWLEquivalentClassesAxiom({
            OWLClass('http://example.com#Cls1'),
            OWLDataSomeValuesFrom(
                OWLDataProperty('http://example.com#dprop1'),
                OWLDatatypeRestriction(
                    OWLDatatype(XSD.integer),
                    {
                        OWLFacetRestriction(
                            XSD.maxExclusive,
                            Literal(20, None, XSD.integer))
                    }))}, {
            OWLAnnotation(
                OWLAnnotationProperty('http://example.com#ann'),
                Literal('some annotation', 'en'))})

        prefixes = {
            'ex': 'http://example.com#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            OWLOntology.default_prefix_dummy: 'http://example.com#'}
        parser = FunctionalSyntaxParser(prefixes=prefixes)

        self.assertEqual(
            equivalent_classes_1,
            parser.equivalent_classes.parseString(equivalent_classes_str_1)[0])

        self.assertEqual(
            equivalent_classes_1,
            parser.equivalent_classes.parseString(equivalent_classes_str_2)[0])

        self.assertEqual(
            equivalent_classes_1,
            parser.equivalent_classes.parseString(equivalent_classes_str_3)[0])

        self.assertEqual(
            equivalent_classes_2,
            parser.equivalent_classes.parseString(equivalent_classes_str_4)[0])

