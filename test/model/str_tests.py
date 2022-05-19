import unittest

from rdflib import Literal, XSD

from morelianoctua.model.objects.classexpression import OWLDataExactCardinality, OWLDataMaxCardinality, \
    OWLDataMinCardinality, OWLDataSomeValuesFrom, OWLDataHasValue, OWLDataAllValuesFrom, OWLObjectExactCardinality, \
    OWLClass, OWLObjectMaxCardinality, OWLObjectMinCardinality, OWLObjectHasSelf, OWLObjectHasValue, \
    OWLObjectAllValuesFrom, OWLObjectSomeValuesFrom, OWLObjectOneOf, OWLObjectComplementOf, OWLObjectUnionOf, \
    OWLObjectIntersectionOf
from morelianoctua.model.objects.datarange import OWLDatatype, OWLDataUnionOf, OWLDatatypeRestriction, OWLDataOneOf, \
    OWLDataComplementOf, OWLDataIntersectionOf
from morelianoctua.model.objects.facet import OWLFacetRestriction
from morelianoctua.model.objects.individual import OWLNamedIndividual, OWLAnonymousIndividual
from morelianoctua.model.objects.property import OWLAnnotationProperty, \
    OWLObjectProperty, OWLObjectInverseOf, OWLDataProperty


class TestStr(unittest.TestCase):
    def test_owl_annotation_property(self):
        expected_str = '<http://ex.com/ont/ann_prop_01>'
        ann_prop = OWLAnnotationProperty('http://ex.com/ont/ann_prop_01')

        self.assertEqual(expected_str, str(ann_prop))

    def test_owl_object_property(self):
        expected_str = '<http://ex.com/ont/obj_prop_01>'
        obj_prop = OWLObjectProperty('http://ex.com/ont/obj_prop_01')

        self.assertEqual(expected_str, str(obj_prop))

    def test_owl_object_inverse_of(self):
        expected_str = 'ObjectInverseOf(<http://ex.com/ont/obj_prop_01>)'
        obj_inverse_of = OWLObjectInverseOf(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'))

        self.assertEqual(expected_str, str(obj_inverse_of))

    def test_owl_data_property(self):
        expected_str = '<http://ex.com/ont/data_prop_01>'
        data_prop = OWLDataProperty('http://ex.com/ont/data_prop_01')

        self.assertEqual(expected_str, str(data_prop))

    def test_owl_named_individual(self):
        expected_str = '<http://ex.com/ont/indiv_01>'
        indiv = OWLNamedIndividual('http://ex.com/ont/indiv_01')

        self.assertEqual(expected_str, str(indiv))

    def test_owl_anonymous_individual(self):
        expected_str = '_:23'
        anon_indiv = OWLAnonymousIndividual('23')

        self.assertEqual(expected_str, str(anon_indiv))

    def test_owl_facet_restriction(self):
        expected_str = f'<{XSD}minInclusive> "23"^^<{XSD.int}>'
        facet_restriction = OWLFacetRestriction(
            XSD.minInclusive, Literal(23, None, XSD.int))

        self.assertEqual(expected_str, str(facet_restriction))

    def test_owl_datatype(self):
        expected_str = f'<{XSD.int}>'
        datatype = OWLDatatype(XSD.int)

        self.assertEqual(expected_str, str(datatype))

    def test_owl_data_intersection_of(self):
        data_intersection = OWLDataIntersectionOf(
            XSD.nonNegativeInteger,
            XSD.nonPositiveInteger
        )

        dranges_str = " ".join(
            [str(drange) for drange in data_intersection.operands])

        expected_str = \
            f'DataIntersectionOf({dranges_str})'

        self.assertEqual(expected_str, str(data_intersection))

    def test_owl_data_union_of(self):
        data_union = OWLDataUnionOf(
            XSD.nonNegativeInteger,
            XSD.nonPositiveInteger,
            XSD.string)

        union_strs = map(lambda drange: str(drange), data_union.operands)
        expected_str = \
            f'DataUnionOf({" ".join(union_strs)})'

        self.assertEqual(expected_str, str(data_union))

    def test_owl_data_complement_of(self):
        expected_str = f'DataComplementOf(<{XSD.nonNegativeInteger}>)'
        data_complement_of = OWLDataComplementOf(XSD.nonNegativeInteger)

        self.assertEqual(expected_str, str(data_complement_of))

    def test_owl_data_one_of(self):
        data_one_of = OWLDataOneOf(
            Literal(23, None, XSD.integer),
            Literal(42, None, XSD.integer),
            Literal("foo", None, XSD.string)
        )

        literals_str = " ".join(
            [f'"{l.value}"^^<{l.datatype}>' for l in data_one_of.operands])

        expected_str = f'DataOneOf({literals_str})'

        self.assertEqual(expected_str, str(data_one_of))

    def test_owl_datatype_restriction(self):
        dtype_restriction = OWLDatatypeRestriction(
            XSD.integer,
            {
                OWLFacetRestriction(
                    XSD.minInclusive, Literal(5, None, XSD.integer)),
                OWLFacetRestriction(
                    XSD.maxExclusive, Literal(10, None, XSD.integer))
             }
        )

        facet_restrs_str = " ".join(
            [str(fr) for fr in dtype_restriction.facet_restrictions])

        expected_str = \
            f'DatatypeRestriction(<{XSD.integer}> {facet_restrs_str})'

        self.assertEqual(expected_str, str(dtype_restriction))

    def test_owl_class(self):
        expected_str = '<http://ex.com/ont/Cls1>'
        cls = OWLClass('http://ex.com/ont/Cls1')

        self.assertEqual(expected_str, str(cls))

    def test_owl_object_intersection_of(self):
        obj_intersection = OWLObjectIntersectionOf(
            OWLClass('http://ex.com/ont/Cls1'),
            OWLObjectSomeValuesFrom(
                OWLObjectProperty('http://ex.com/ont/obj_prop'),
                OWLClass('http://ex.com/ont/Cls2')
            ),
            OWLClass('http://ex.com/ont/Cls3')
        )

        operands_str = ' '.join([str(o) for o in obj_intersection.operands])
        expected_str = f'ObjectIntersectionOf({operands_str})'

        self.assertEqual(expected_str, str(obj_intersection))

    def test_owl_object_union_of(self):
        obj_union = OWLObjectUnionOf(
            OWLClass('http://ex.com/int/Cls1'),
            OWLObjectSomeValuesFrom(
                OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
                OWLClass('http://ex.com/ont/Cls2')
            ),
            OWLClass('http://ex.com/ont/Cls3')
        )

        operands_str = ' '.join([str(o) for o in obj_union.operands])
        expected_str = f'ObjectUnionOf({operands_str})'

        self.assertEqual(expected_str, str(obj_union))

    def test_owl_object_complement_of(self):
        expected_str = \
            'ComplementOf(' \
            'ObjectSomeValuesFrom(' \
            '<http://ex.com/ont/obj_prop_01> <http://ex.com/ont/Cls1>))'

        obj_complement = OWLObjectComplementOf(
            OWLObjectSomeValuesFrom(
                OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
                OWLClass('http://ex.com/ont/Cls1')
            )
        )

        self.assertEqual(expected_str, str(obj_complement))

    def test_owl_object_one_of(self):
        obj_one_of = OWLObjectOneOf(
            OWLNamedIndividual('http://ex.com/ont/individual_01'),
            OWLNamedIndividual('http://ex.com/ont/individual_02'),
            OWLNamedIndividual('http://ex.com/ont/individual_03')
        )

        indivs_str = ' '.join([str(i) for i in obj_one_of.individuals])
        expected_str = f'ObjectOneOf({indivs_str})'

        self.assertEqual(expected_str, str(obj_one_of))

    def test_owl_object_some_values_from(self):
        expected_str = \
            'ObjectSomeValuesFrom(' \
            '<http://ex.com/ont/obj_prop_01> <http://ex.com/ont/Cls1>)'

        obj_some_values_from = OWLObjectSomeValuesFrom(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            OWLClass('http://ex.com/ont/Cls1')
        )

        self.assertEqual(expected_str, str(obj_some_values_from))

    def test_owl_object_all_values_from(self):
        expected_str = \
            'ObjectAllValuesFrom(' \
            '<http://ex.com/ont/obj_prop_01> <http://ex.com/ont/Cls1>)'

        obj_all_values_from = OWLObjectAllValuesFrom(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            OWLClass('http://ex.com/ont/Cls1')
        )

        self.assertEqual(expected_str, str(obj_all_values_from))

    def test_owl_object_has_value(self):
        expected_str = \
            'ObjectHasValue(' \
            '<http://ex.com/ont/obj_prop_01> <http://ex.com/ont/indiv_01>)'

        obj_has_value = OWLObjectHasValue(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            OWLNamedIndividual('http://ex.com/ont/indiv_01')
        )

        self.assertEqual(expected_str, str(obj_has_value))

    def test_owl_object_has_self(self):
        expected_str = 'ObjectHasSelf(<http://ex.com/ont/obj_prop_01>)'

        obj_has_self = OWLObjectHasSelf(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'))

        self.assertEqual(expected_str, str(obj_has_self))

    def test_owl_object_min_cardinality(self):
        expected_str = \
            'ObjectMinCardinality(' \
            '3 ' \
            '<http://ex.com/ont/obj_prop_01> ' \
            '<http://ex.com/ont/Cls01>)'

        obj_min_cardinality = OWLObjectMinCardinality(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            3,
            OWLClass('http://ex.com/ont/Cls01')
        )

        self.assertEqual(expected_str, str(obj_min_cardinality))

    def test_owl_object_max_cardinality(self):
        expected_str = \
            'ObjectMaxCardinality(' \
            '4 ' \
            '<http://ex.com/ont/obj_prop_01> ' \
            '<http://ex.com/ont/Cls01>)'

        obj_max_cardinality = OWLObjectMaxCardinality(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            4,
            OWLClass('http://ex.com/ont/Cls01')
        )

        self.assertEqual(expected_str, str(obj_max_cardinality))

    def test_owl_object_exact_cardinality(self):
        expected_str = \
            'ObjectExactCardinality(' \
            '2 ' \
            '<http://ex.com/ont/obj_prop_01> ' \
            '<http://ex.com/ont/Cls01>)'

        obj_exact_cardinality = OWLObjectExactCardinality(
            OWLObjectProperty('http://ex.com/ont/obj_prop_01'),
            2,
            OWLClass('http://ex.com/ont/Cls01')
        )

        self.assertEqual(expected_str, str(obj_exact_cardinality))

    def test_owl_data_some_values_from(self):
        expected_str = \
            f'DataSomeValuesFrom(' \
            f'<http://ex.com/ont/data_prop_01> <{XSD.integer}>)'

        data_some_values_from = OWLDataSomeValuesFrom(
            OWLDataProperty('http://ex.com/ont/data_prop_01'),
            XSD.integer
        )

        self.assertEqual(expected_str, str(data_some_values_from))

    def test_owl_data_all_values_from(self):
        expected_str = \
            f'DataAllValuesFrom(' \
            f'<http://ex.com/ont/data_prop_01> <{XSD.integer}>)'

        data_all_values_from = OWLDataAllValuesFrom(
            OWLDataProperty('http://ex.com/ont/data_prop_01'),
            XSD.integer)

        self.assertEqual(expected_str, str(data_all_values_from))

    def test_owl_data_has_value(self):
        expected_str = \
            f'DataHasValue(' \
            f'<http://ex.com/ont/data_prop_01> "23"^^<{XSD.integer}>)'

        data_has_value = OWLDataHasValue(
            OWLDataProperty('http://ex.com/ont/data_prop_01'),
            Literal(23, None, XSD.integer))

        self.assertEqual(expected_str, str(data_has_value))

    def test_owl_data_min_cardinality(self):
        expected_str = \
            f'DataMinCardinality(' \
            f'2 ' \
            f'<http://ex.com/ont/data_prop_01> ' \
            f'<{XSD.string}>)'

        data_min_cardinality = OWLDataMinCardinality(
            OWLDataProperty('http://ex.com/ont/data_prop_01'), 2, XSD.string)

        self.assertEqual(expected_str, str(data_min_cardinality))

    def test_owl_data_max_cardinality(self):
        expected_str = \
            f'DataMaxCardinality(' \
            f'4 ' \
            f'<http://ex.com/ont/data_prop_01> ' \
            f'<{XSD.string}>)'

        data_max_cardinality = OWLDataMaxCardinality(
            OWLDataProperty('http://ex.com/ont/data_prop_01'), 4, XSD.string)

        self.assertEqual(expected_str, str(data_max_cardinality))

    def test_owl_data_exact_cardinality(self):
        expected_str = \
            f'DataExactCardinality(' \
            f'2 ' \
            f'<http://ex.com/ont/data_prop_01> ' \
            f'<{XSD.string}>)'

        data_exact_cardinality = OWLDataExactCardinality(
            OWLDataProperty('http://ex.com/ont/data_prop_01'), 2, XSD.string)

        self.assertEqual(expected_str, str(data_exact_cardinality))
