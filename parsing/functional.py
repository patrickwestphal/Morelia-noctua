from pyparsing import Literal, alphas, Word, OneOrMore, nums, Optional, \
    ZeroOrMore, alphanums, lineEnd, printables, Combine, White, Forward
from rdflib import Literal as RDFLiteral
from rdflib import URIRef, BNode

from model import OWLOntology
from model.axioms import OWLAxiom
from model.axioms.classaxiom import OWLSubClassOfAxiom, \
    OWLEquivalentClassesAxiom, OWLDisjointClassesAxiom, OWLDisjointUnionAxiom
from model.axioms.declarationaxiom import OWLClassDeclarationAxiom, \
    OWLDatatypeDeclarationAxiom, OWLObjectPropertyDeclarationAxiom, \
    OWLDataPropertyDeclarationAxiom, OWLAnnotationPropertyDeclarationAxiom, \
    OWLNamedIndividualDeclarationAxiom
from model.axioms.owlobjectpropertyaxiom import \
    OWLSubObjectPropertyOfAxiom, OWLEquivalentObjectPropertiesAxiom
from model.objects import HasIRI
from model.objects.annotation import OWLAnnotation
from model.objects.classexpression import OWLClass, OWLObjectIntersectionOf, \
    OWLObjectUnionOf, OWLObjectComplementOf, OWLObjectOneOf, \
    OWLObjectSomeValuesFrom, OWLObjectAllValuesFrom, OWLObjectHasValue, \
    OWLObjectHasSelf, OWLObjectMinCardinality, OWLObjectMaxCardinality, \
    OWLObjectExactCardinality, OWLDataSomeValuesFrom, OWLDataAllValuesFrom, \
    OWLDataHasValue, OWLDataMinCardinality, OWLDataMaxCardinality, \
    OWLDataExactCardinality, OWLClassExpression
from model.objects.datarange import OWLDataIntersectionOf, OWLDataUnionOf, \
    OWLDataComplementOf, OWLDatatype, OWLDataOneOf, OWLDatatypeRestriction
from model.objects.facet import OWLFacetRestriction
from model.objects.individual import OWLNamedIndividual, OWLAnonymousIndividual
from model.objects.property import OWLAnnotationProperty, OWLObjectProperty, \
    OWLDataProperty, OWLObjectInverseOf, OWLObjectPropertyExpression
from parsing import OWLParser


class FunctionalSyntaxParser(OWLParser):
    """
    Definition from
    https://www.w3.org/TR/owl2-syntax/#Canonical_Parsing_of_OWL_2_Ontologies:

    ontologyDocument := { prefixDeclaration } Ontology
    prefixDeclaration := 'Prefix' '(' prefixName '=' fullIRI ')'
    Ontology :=
        'Ontology' '(' [ ontologyIRI [ versionIRI ] ]
           directlyImportsDocuments
           ontologyAnnotations
           axioms
        ')'
    ontologyIRI := IRI
    versionIRI := IRI
    directlyImportsDocuments := { 'Import' '(' IRI ')' }
    axioms := { Axiom }
    """
    def __init__(self, prefixes=None):
        # helper literals
        self.open_paren = Literal('(')
        self.close_paren = Literal(')')
        self.open_angle = Literal('<')
        self.close_angle = Literal('>')
        self.equals = Literal('=')
        self.colon = Literal(':')
        self.dot = Literal('.')
        self.dash = Literal('-')
        self.underscore = Literal('_')
        self.slash = Literal('/')
        self.hsh = Literal('#')
        self.question_mark = Literal('?')
        self.double_circum = Literal('^^')
        self.at = Literal('@')
        self.percent = Literal('%')
        self.double_quotes = Literal('"')

        self.non_negative_integer = Word(nums)

        # local part
        # FIXME: this is highly simplified!
        self.pn_local = Word(alphanums + '_', alphanums + '-_.')

        self.pn_prefix = Word(alphas, alphanums + '_-.')
        self.prefix_name = Optional(self.pn_prefix) + self.colon

        # FIXME: this is just to get started; not a correct expression for IRIs!
        self.full_iri = (
            self.open_angle.suppress() +
            OneOrMore(
                Word(alphanums) |
                self.colon |
                self.dash |
                self.slash |
                self.dot |
                self.hsh |
                self.question_mark |
                self.underscore |
                self.percent) +
            self.close_angle.suppress())\
            .addParseAction(lambda parsed: URIRef(''.join(parsed)))

        self.prefix_decl = \
            self.prefix_name + \
            self.equals.suppress() + \
            self.full_iri

        self.prefix_declaration = (
            Literal('Prefix').suppress() +
            self.open_paren.suppress() +
            self.prefix_decl +
            self.close_paren.suppress() +
            lineEnd.suppress()).addParseAction(self._create_prefix)

        self.prefix_declarations = \
            ZeroOrMore(self.prefix_declaration)\
            .addParseAction(self._concat_prefixes)

        self.abbreviated_iri = \
            ~ Literal('_') + \
            Combine(Optional(self.prefix_name) + self.pn_local)\
            .addParseAction(self._create_full_iri)

        self.iri = self.full_iri | self.abbreviated_iri
        self.ontology_iri = self.iri
        self.version_iri = self.iri

        self.comment = (
            self.hsh +
            ZeroOrMore(Word(printables), lineEnd) +
            lineEnd).suppress()

        # FIXME: Imports are ignored
        self.directly_imports_documents = Optional(
            Literal('Import') +
            self.open_paren +
            self.iri +
            self.close_paren).suppress()

        self.node_id = '_:' + Word(alphanums)

        self.quoted_string = (
            self.double_quotes.suppress() +
            ZeroOrMore(Word(alphanums + "'-_.:,;*+?`´=)(&%$§!<>|")) +
            self.double_quotes.suppress()
        ).setName('quoted_string').addParseAction(
            lambda parsed: ' '.join(parsed))

        self.lexical_form = self.quoted_string

        self.datatype = (
            (self.full_iri | self.abbreviated_iri) +
            ~ self.open_paren
        ).setName('datatype').addParseAction(
            lambda parsed: OWLDatatype(parsed[0]))

        # typedLiteral := lexicalForm '^^' Datatype
        self.typed_literal = \
            self.lexical_form + self.double_circum.suppress() + self.datatype

        # stringLiteralNoLanguage := quotedString
        self.string_literal_no_language = self.quoted_string

        self.language_tag = self.at.suppress() + Word(alphanums)  # FIXME

        # stringLiteralWithLanguage := quotedString languageTag
        self.string_literal_with_language = \
            self.quoted_string + self.language_tag

        # Literal := typedLiteral | stringLiteralNoLanguage |
        #               stringLiteralWithLanguage
        self.literal = (
            self.typed_literal |
            self.string_literal_with_language |
            self.string_literal_no_language
        ).setName('owl_literal').addParseAction(self._create_literal)

        self.data_range = Forward()

        # DataIntersectionOf :=
        #         'DataIntersectionOf' '(' DataRange DataRange { DataRange } ')'
        self.data_intersection_of = (
            Literal('DataIntersectionOf').suppress() +
            self.open_paren.suppress() +
            self.data_range +
            self.data_range +
            ZeroOrMore(self.data_range) +
            self.close_paren.suppress()
        ).setName('data_intersection_of').addParseAction(
            lambda parsed: OWLDataIntersectionOf(*parsed))

        # DataUnionOf := 'DataUnionOf' '(' DataRange DataRange { DataRange } ')'
        self.data_union_of = (
            Literal('DataUnionOf').suppress() +
            self.open_paren.suppress() +
            self.data_range +
            self.data_range +
            ZeroOrMore(self.data_range) +
            self.close_paren.suppress()
        ).setName('data_union').addParseAction(
            lambda parsed: OWLDataUnionOf(*parsed))

        # DataComplementOf := 'DataComplementOf' '(' DataRange ')'
        self.data_complement_of = (
            Literal('DataComplementOf').suppress() +
            self.open_paren.suppress() +
            self.data_range +
            self.close_paren.suppress()
        ).setName('data_complement_of').addParseAction(
            lambda parsed: OWLDataComplementOf(parsed[0]))

        # DataOneOf := 'DataOneOf' '(' Literal { Literal } ')'
        self.data_one_of = (
            Literal('DataOneOf').suppress() +
            self.open_paren.suppress() +
            self.literal +
            ZeroOrMore(self.literal) +
            self.close_paren.suppress()
        ).setName('data_one_of').addParseAction(
            lambda parsed: OWLDataOneOf(*parsed))

        self.constraining_facet = (
            (self.full_iri | self.abbreviated_iri) + ~ self.open_paren
        ).setName('constraining_facet').addParseAction(
            lambda parsed: URIRef(parsed[0]))

        # DatatypeRestriction :=
        #    'DatatypeRestriction' '(' Datatype constrainingFacet
        #            restrictionValue { constrainingFacet restrictionValue } ')'
        self.datatype_restriction = (
            Literal('DatatypeRestriction').suppress() +
            self.open_paren.suppress() +
            self.datatype +
            self.constraining_facet +
            self.literal +  # the restriction value
            ZeroOrMore(self.constraining_facet + self.literal) +
            self.close_paren.suppress()
        ).setName('datatype_restriction').addParseAction(
            self._create_dtype_restriction)

        # DataRange := Datatype | DataIntersectionOf | DataUnionOf |
        #   DataComplementOf | DataOneOf | DatatypeRestriction
        self.data_range << (
            self.datatype |
            self.data_intersection_of |
            self.data_union_of |
            self.data_complement_of |
            self.data_one_of |
            self.datatype_restriction
        ).setName('data_range')

        self.anonymous_individual = (
            '_:' + Word(alphanums)
        ).setName('anon_indiv').addParseAction(
            lambda parsed: OWLAnonymousIndividual(BNode(parsed[1])))

        self.annotation_value = (
                self.anonymous_individual |
                self.iri |
                self.literal).setName('ann_value')

        self.annotation_property = (
            self.full_iri | self.abbreviated_iri
        ).setName('ann_prop').addParseAction(
            lambda parsed: OWLAnnotationProperty(parsed[0]))

        self.annotation = (
            Literal('Annotation').suppress() +
            self.open_paren.suppress() +
            self.annotation_property +
            self.annotation_value +
            self.close_paren.suppress()
        ).setName('annotation').addParseAction(self._create_annotation)

        # ontologyAnnotations := { Annotation }
        self.ontology_annotations = ZeroOrMore(self.annotation)
        self.empty_line = White() + lineEnd

        self.axiom_annotations = ZeroOrMore(self.annotation)

        # the ~self.open_paren is needed to remedy the case that, e.g.
        # ObjectUnionOf was recognized as abbreviated class IRI
        self.class_ = (
            self.full_iri | self.abbreviated_iri + ~self.open_paren
        ).setName('class').addParseAction(lambda parsed: OWLClass(parsed[0]))

        self.obj_prop = (
            ~ Literal('ObjectInverseOf') +
            (self.full_iri | self.abbreviated_iri)
        ).setName('obj_prop').addParseAction(
            lambda parsed: OWLObjectProperty(parsed[0]))

        self.data_prop = (
            self.full_iri | self.abbreviated_iri
        ).setName('data_prop').addParseAction(
            lambda parsed: OWLDataProperty(parsed[0]))

        self.ann_prop = (
            self.full_iri | self.abbreviated_iri
        ).setName('ann_prop').addParseAction(
            lambda parsed: OWLAnnotationProperty(parsed[0]))

        self.named_indiv = (
            self.full_iri | self.abbreviated_iri
        ).setName('named_individual').addParseAction(
            lambda parsed: OWLNamedIndividual(parsed[0]))

        self.individual = self.named_indiv | self.anonymous_individual

        # InverseObjectProperty := 'ObjectInverseOf' '(' ObjectProperty ')'
        self.inverse_obj_prop = (
            Literal('ObjectInverseOf').suppress() +
            self.open_paren.suppress() +
            self.obj_prop +
            self.close_paren.suppress()
        ).addParseAction(lambda obj_props: OWLObjectInverseOf(obj_props[0]))

        # ObjectPropertyExpression := ObjectProperty | InverseObjectProperty
        self.object_property_expression = (
            self.obj_prop | self.inverse_obj_prop
        ).setName('obj_prop_expr')

        # DataPropertyExpression := DataProperty
        self.data_property_expression = (
            self.full_iri | self.abbreviated_iri
        ).setName('data_prop_expr').addParseAction(
            lambda parsed: OWLDataProperty(parsed[0]))

        # Entity :=
        #   'Class' '(' Class ')' |
        #   'Datatype' '(' Datatype ')' |
        #   'ObjectProperty' '(' ObjectProperty ')' |
        #   'DataProperty' '(' DataProperty ')' |
        #   'AnnotationProperty' '(' AnnotationProperty ')' |
        #   'NamedIndividual' '(' NamedIndividual ')'
        self.entity = (
            Literal('Class').suppress() +
            self.open_paren.suppress() +
            self.class_ +
            self.close_paren.suppress()
        ) | (
            Literal('Datatype').suppress() +
            self.open_paren.suppress() +
            self.datatype +
            self.close_paren.suppress()
        ) | (
            Literal('ObjectProperty').suppress() +
            self.open_paren.suppress() +
            self.obj_prop +
            self.close_paren.suppress()
        ) | (
            Literal('DataProperty').suppress() +
            self.open_paren.suppress() +
            self.data_prop +
            self.close_paren.suppress()
        ) | (
            Literal('AnnotationProperty').suppress() +
            self.open_paren.suppress() +
            self.ann_prop +
            self.close_paren.suppress()
        ) | (
            Literal('NamedIndividual').suppress() +
            self.open_paren.suppress() +
            self.named_indiv +
            self.close_paren.suppress()
        )

        # Declaration := 'Declaration' '(' axiomAnnotations Entity ')'
        self.declaration = (
            Literal('Declaration').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.entity +
            self.close_paren.suppress()
        ).addParseAction(self._create_declaration_axiom)

        self.class_expression = Forward()

        # ObjectIntersectionOf :=
        #   'ObjectIntersectionOf' '(' ClassExpression ClassExpression
        #                              { ClassExpression } ')'
        self.object_intersection_of = (
            Literal('ObjectIntersectionOf').suppress() +
            self.open_paren.suppress() +
            self.class_expression +
            self.class_expression +
            ZeroOrMore(self.class_expression) +
            self.close_paren.suppress()
        ).setName('obj_intersection_of').addParseAction(
            lambda cls_exprs: OWLObjectIntersectionOf(*cls_exprs))

        # ObjectUnionOf := 'ObjectUnionOf' '(' ClassExpression ClassExpression
        #                                      { ClassExpression } ')'
        self.object_union_of = (
            Literal('ObjectUnionOf').suppress() +
            self.open_paren.suppress() +
            self.class_expression +
            self.class_expression +
            ZeroOrMore(self.class_expression) +
            self.close_paren.suppress()
        ).setName('obj:union_of').addParseAction(
            lambda cls_expressions: OWLObjectUnionOf(*cls_expressions))

        # ObjectComplementOf := 'ObjectComplementOf' '(' ClassExpression ')'
        self.object_complement_of = (
            Literal('ObjectComplementOf').suppress() +
            self.open_paren.suppress() +
            self.class_expression +
            self.close_paren.suppress()
        ).setName('obj_complement_of').addParseAction(
            lambda cls_expr: OWLObjectComplementOf(cls_expr[0]))

        # ObjectOneOf := 'ObjectOneOf' '(' Individual { Individual }')'
        self.object_one_of = (
            Literal('ObjectOneOf').suppress() +
            self.open_paren.suppress() +
            self.individual +
            ZeroOrMore(self.individual) +
            self.close_paren.suppress()
        ).setName('obj_one_of').addParseAction(
            lambda individuals: OWLObjectOneOf(*individuals))

        # ObjectSomeValuesFrom :=
        #   'ObjectSomeValuesFrom' '(' ObjectPropertyExpression
        #                              ClassExpression ')'
        self.object_some_values_from = (
            Literal('ObjectSomeValuesFrom').suppress() +
            self.open_paren.suppress() +
            self.object_property_expression +
            self.class_expression +
            self.close_paren.suppress()
        ).setName('obj_some_vals_from').addParseAction(
            lambda parsed: OWLObjectSomeValuesFrom(parsed[0], parsed[1]))

        # ObjectAllValuesFrom :=
        # 'ObjectAllValuesFrom' '(' ObjectPropertyExpression ClassExpression ')'
        self.object_all_values_from = (
            Literal('ObjectAllValuesFrom').suppress() +
            self.open_paren.suppress() +
            self.object_property_expression +
            self.class_expression +
            self.close_paren.suppress()
        ).setName('obj_all_vals_from').addParseAction(
            lambda parsed: OWLObjectAllValuesFrom(parsed[0], parsed[1]))

        # ObjectHasValue := 'ObjectHasValue' '(' ObjectPropertyExpression
        #                                        Individual ')'
        self.object_has_value = (
            Literal('ObjectHasValue').suppress() +
            self.open_paren.suppress() +
            self.object_property_expression +
            self.individual +
            self.close_paren.suppress()
        ).setName('obj_has_value').addParseAction(
            lambda parsed: OWLObjectHasValue(parsed[0], parsed[1]))

        # ObjectHasSelf := 'ObjectHasSelf' '(' ObjectPropertyExpression ')'
        self.object_has_self = (
            Literal('ObjectHasSelf').suppress() +
            self.open_paren.suppress() +
            self.object_property_expression +
            self.close_paren.suppress()
        ).setName('obj_has_self').addParseAction(
            lambda parsed: OWLObjectHasSelf(parsed[0]))

        # ObjectMinCardinality :=
        #  ObjectMinCardinality' '(' nonNegativeInteger ObjectPropertyExpression
        #                              [ ClassExpression ] ')'
        self.object_min_cardinality = (
            Literal('ObjectMinCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.object_property_expression +
            Optional(self.class_expression) +
            self.close_paren.suppress()
        ).setName('obj_min_cardinality').addParseAction(
            self._create_obj_min_cardinality_expression)

        # ObjectMaxCardinality :=
        #   'ObjectMaxCardinality' '(' nonNegativeInteger
        #                       ObjectPropertyExpression [ ClassExpression ] ')'
        self.object_max_cardinality = (
            Literal('ObjectMaxCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.object_property_expression +
            Optional(self.class_expression) +
            self.close_paren.suppress()
        ).setName('obj_max_cardinality').addParseAction(
            self._create_obj_max_cardinality)

        # ObjectExactCardinality :=
        #   'ObjectExactCardinality' '(' nonNegativeInteger
        #                       ObjectPropertyExpression [ ClassExpression ] ')'
        self.object_exact_cardinality = (
            Literal('ObjectExactCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.object_property_expression +
            Optional(self.class_expression) +
            self.close_paren.suppress()
        ).setName('obj_exact_cardinality').addParseAction(
            self._create_obj_exact_cardinality)

        # DataSomeValuesFrom :=
        #   'DataSomeValuesFrom' '(' DataPropertyExpression
        #                            { DataPropertyExpression } DataRange ')'
        self.data_some_values_from = (
            Literal('DataSomeValuesFrom').suppress() +
            self.open_paren.suppress() +
            self.data_property_expression +
            # ZeroOrMore(self.data_property_expression) +
            self.data_range +
            self.close_paren.suppress()
        ).setName('data_some_values_from').addParseAction(
            lambda parsed: OWLDataSomeValuesFrom(parsed[0], parsed[1]))

        # DataAllValuesFrom :=
        #   'DataAllValuesFrom' '(' DataPropertyExpression
        #                           { DataPropertyExpression } DataRange ')'
        self.data_all_values_from = (
            Literal('DataAllValuesFrom').suppress() +
            self.open_paren.suppress() +
            self.data_property_expression +
            # ZeroOrMore(self.data_property_expression) +
            self.data_range +
            self.close_paren.suppress()
        ).setName('data_all_values_from').addParseAction(
            lambda parsed: OWLDataAllValuesFrom(parsed[0], parsed[1]))

        # DataHasValue := 'DataHasValue' '(' DataPropertyExpression Literal ')'
        self.data_has_value = (
            Literal('DataHasValue').suppress() +
            self.open_paren.suppress() +
            self.data_property_expression +
            self.literal +
            self.close_paren.suppress()
        ).setName('data_has_value').addParseAction(
            lambda parsed: OWLDataHasValue(parsed[0], parsed[1]))

        # DataMinCardinality :=
        #     'DataMinCardinality' '(' nonNegativeInteger DataPropertyExpression
        #                                [ DataRange ] ')'
        self.data_min_cardinality = (
            Literal('DataMinCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.data_property_expression +
            Optional(self.data_range)
        ).setName('data_min_cardinality').addParseAction(
            self._create_data_min_cardinality)

        # DataMaxCardinality :=
        #    'DataMaxCardinality' '(' nonNegativeInteger DataPropertyExpression
        #                             [ DataRange ] ')'
        self.data_max_cardinality = (
            Literal('DataMaxCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.data_property_expression +
            Optional(self.data_range) +
            self.close_paren.suppress()
        ).setName('data_max_cardinality').addParseAction(
            self._create_data_max_cardinality)

        # DataExactCardinality :=
        #   'DataExactCardinality' '(' nonNegativeInteger DataPropertyExpression
        #                               [ DataRange ] ')'
        self.data_exact_cardinality = (
            Literal('DataExactCardinality').suppress() +
            self.open_paren.suppress() +
            self.non_negative_integer +
            self.data_property_expression +
            Optional(self.data_range) +
            self.close_paren.suppress()
        ).setName('data_exact_cardinality').addParseAction(
            self._create_data_exact_cardinality)

        # ClassExpression :=
        #     Class | ObjectIntersectionOf | ObjectUnionOf |
        #     ObjectComplementOf | ObjectOneOf | ObjectSomeValuesFrom |
        #     ObjectAllValuesFrom | ObjectHasValue | ObjectHasSelf |
        #     ObjectMinCardinality | ObjectMaxCardinality |
        #     ObjectExactCardinality | DataSomeValuesFrom | DataAllValuesFrom |
        #     DataHasValue | DataMinCardinality | DataMaxCardinality |
        #     DataExactCardinality
        self.class_expression << (
            self.class_ |
            self.object_union_of |
            self.object_intersection_of |
            self.object_complement_of |
            self.object_one_of |
            self.object_some_values_from |
            self.object_all_values_from |
            self.object_has_value |
            self.object_has_self |
            self.object_min_cardinality |
            self.object_max_cardinality |
            self.object_exact_cardinality |
            self.data_some_values_from |
            self.data_all_values_from |
            self.data_has_value |
            self.data_min_cardinality |
            self.data_max_cardinality |
            self.data_exact_cardinality
        )

        # SubClassOf := 'SubClassOf' '(' axiomAnnotations subClassExpression
        #                                superClassExpression ')'
        self.sub_class_of = (
            Literal('SubClassOf').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.class_expression +
            self.class_expression +
            self.close_paren.suppress()
        ).addParseAction(self._create_sub_cls_of_axiom)

        # EquivalentClasses :=
        #       'EquivalentClasses' '(' axiomAnnotations ClassExpression
        #                               ClassExpression { ClassExpression } ')'
        self.equivalent_classes = (
            Literal('EquivalentClasses').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.class_expression +
            self.class_expression +
            ZeroOrMore(self.class_expression) +
            self.close_paren.suppress()
        ).addParseAction(self._create_equivalent_classes_axiom)

        # DisjointClasses :=
        #       'DisjointClasses' '(' axiomAnnotations ClassExpression
        #                             ClassExpression { ClassExpression } ')'
        self.disjoint_classes = (
            Literal('DisjointClasses').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.class_expression +
            self.class_expression +
            ZeroOrMore(self.class_expression) +
            self.close_paren.suppress()
        ).addParseAction(self._create_disjoint_classes_axiom)

        # DisjointClassExpressions :=
        #       ClassExpression ClassExpression { ClassExpression }
        self.disjoint_class_expressions = \
            self.class_expression + \
            self.class_expression + \
            ZeroOrMore(self.class_expression)

        # DisjointUnion :=
        #    'DisjointUnion' '(' axiomAnnotations Class
        #                        disjointClassExpressions ')'
        self.disjoint_union = (
            Literal('DisjointUnion').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.class_ +
            self.disjoint_class_expressions +
            self.close_paren.suppress()
        ).addParseAction(self._create_disjoint_union_axiom)

        # ClassAxiom := SubClassOf | EquivalentClasses | DisjointClasses |
        #   DisjointUnion
        self.class_axiom = \
            self.sub_class_of | \
            self.equivalent_classes | \
            self.disjoint_classes | \
            self.disjoint_union

        # SubObjectPropertyOf :=
        # 'SubObjectPropertyOf' '(' axiomAnnotations subObjectPropertyExpression
        #                           superObjectPropertyExpression ')'
        self.sub_object_property_of = (
            Literal('SubObjectPropertyOf').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.object_property_expression +
            self.object_property_expression +
            self.close_paren.suppress()
        ).addParseAction(self._create_sub_obj_prop_of_axiom)

        # EquivalentObjectProperties: =
        #    'EquivalentObjectProperties' '(' axiomAnnotations
        #                      ObjectPropertyExpression ObjectPropertyExpression
        #                      { ObjectPropertyExpression } ')'
        self.equivalent_object_properties = (
            Literal('EquivalentObjectProperties').suppress() +
            self.open_paren.suppress() +
            self.axiom_annotations +
            self.object_property_expression +
            self.object_property_expression +
            ZeroOrMore(self.object_property_expression) +
            self.close_paren.suppress()
        ).addParseAction(self._create_equivalent_obj_props_axiom)

        # ObjectPropertyAxiom :=
        #   SubObjectPropertyOf | EquivalentObjectProperties |
        #   DisjointObjectProperties | InverseObjectProperties |
        #   ObjectPropertyDomain | ObjectPropertyRange |
        #   FunctionalObjectProperty | InverseFunctionalObjectProperty |
        #   ReflexiveObjectProperty | IrreflexiveObjectProperty |
        #   SymmetricObjectProperty | AsymmetricObjectProperty |
        #   TransitiveObjectProperty
        self.object_property_axiom = \
            self.sub_object_property_of | \
            self.equivalent_object_properties  #| \
            # self.disjoint_object_properties | \
            # self.inverse_object_properties | \
            # self.object_property_domain | \
            # self.object_property_range | \
            # self.functional_object_property | \
            # self.inverse_functional_object_property | \
            # self.reflexive_object_property | \
            # self.irreflexive_object_property | \
            # self.symmetric_object_property | \
            # self.asymmetric_object_property | \
            # self.transitive_object_property

        # Axiom := Declaration | ClassAxiom | ObjectPropertyAxiom |
        #   DataPropertyAxiom | DatatypeDefinition | HasKey | Assertion |
        #   AnnotationAxiom
        self.axiom = \
            self.declaration | \
            self.class_axiom | \
            self.object_property_axiom #| \
            # self.data_property_axiom | \
            # self.datatype_definition | \
            # self.has_key | \
            # self.assertion | \
            # self.annotation_axiom

        self.axioms = ZeroOrMore(self.axiom | self.comment | self.empty_line)

        self.ontology =\
            Literal('Ontology').suppress() + \
            self.open_paren.suppress() + \
            ZeroOrMore(self.comment) + \
            Optional(self.ontology_iri + Optional(self.version_iri)) + \
            ZeroOrMore(self.comment) + \
            Optional(self.directly_imports_documents) + \
            ZeroOrMore(self.comment) + \
            Optional(self.ontology_annotations) + \
            ZeroOrMore(self.comment) + \
            self.axioms + \
            self.close_paren.suppress()

        self.ontology_document = (
            ZeroOrMore(self.comment) +
            self.prefix_declarations +
            ZeroOrMore(self.comment) +
            self.ontology
        ).addParseAction(self._create_ontology)

        if prefixes is None:
            self._prefixes = dict()
        else:
            self._prefixes = prefixes

    @staticmethod
    def _create_ontology(parsed):
        parts = parsed[:]

        # default values
        prefixes = {}
        ontology_iri = None
        ontology_version_iri = None
        annotations = []
        axioms = set()

        for part in parts:
            if isinstance(part, dict):
                prefixes = part

            elif isinstance(part, OWLAxiom):
                axioms.add(part)

            elif isinstance(part, URIRef):
                if ontology_iri is None:
                    ontology_iri = part
                else:
                    ontology_version_iri = part

            elif isinstance(part, OWLAnnotation):
                annotations.append(part)

            else:
                raise RuntimeError()

        return OWLOntology(
            prefixes,
            axioms,
            ontology_iri=ontology_iri,
            version_iri=ontology_version_iri,
            annotations=annotations)

    @staticmethod
    def _create_dtype_restriction(parsed):
        dtype = parsed.pop(0)
        facet_restrictions = set()

        while len(parsed) > 0:
            facet = parsed.pop(0)
            restriction_value = parsed.pop(0)
            facet_restrictions.add(
                OWLFacetRestriction(facet, restriction_value))

        return OWLDatatypeRestriction(dtype, facet_restrictions)

    @staticmethod
    def _create_disjoint_classes_axiom(parsed):
        disjoint_classes = set()
        annotations = set()

        for part in parsed:
            if isinstance(part, OWLClassExpression):
                disjoint_classes.add(part)
            elif isinstance(part, OWLAnnotation):
                annotations.add(part)
            else:
                raise RuntimeError(
                    f'Got unexpected object in DisjointClasses axiom: {part}')

        if len(annotations) == 0:
            return OWLDisjointClassesAxiom(disjoint_classes)
        else:
            return OWLDisjointClassesAxiom(disjoint_classes, annotations)

    @staticmethod
    def _create_equivalent_obj_props_axiom(parsed):
        annotations = set()
        obj_props = set()

        for part in parsed:
            if isinstance(part, OWLAnnotation):
                annotations.add(part)
            elif isinstance(part, OWLObjectPropertyExpression):
                obj_props.add(part)
            else:
                raise RuntimeError(
                    f'Got unexpected object in EquivalentObjectProperties '
                    f'axiom: {part}')

        if len(annotations) == 0:
            return OWLEquivalentObjectPropertiesAxiom(obj_props)
        else:
            return OWLEquivalentObjectPropertiesAxiom(obj_props, annotations)

    @staticmethod
    def _create_sub_obj_prop_of_axiom(parsed):
        annotations = set()
        sub_prop = None

        while True:
            part = parsed.pop(0)

            if isinstance(part, OWLAnnotation):
                annotations.add(part)
            elif isinstance(part, OWLObjectProperty):
                sub_prop = part
                break
            else:
                raise RuntimeError(
                    f'Got unexpected object in SubObjectPropertyOf axiom: '
                    f'{part}')

        assert len(parsed) == 1

        super_prop = parsed.pop()

        if len(annotations) == 0:
            return OWLSubObjectPropertyOfAxiom(sub_prop, super_prop)
        else:
            return OWLSubObjectPropertyOfAxiom(
                sub_prop, super_prop, annotations)

    @staticmethod
    def _create_disjoint_union_axiom(parsed):
        class_expressions = set()
        annotations = set()

        owl_class = None

        for part in parsed:
            if isinstance(part, OWLClass) and owl_class is None:
                owl_class = part
            elif isinstance(part, OWLClassExpression):
                class_expressions.add(part)
            elif isinstance(part, OWLAnnotation):
                annotations.add(part)
            else:
                raise RuntimeError(
                    f'Got unexpected object in DisjointUnion axiom: {part}')

        if len(annotations) == 0:
            return OWLDisjointUnionAxiom(owl_class, class_expressions)
        else:
            return OWLDisjointUnionAxiom(
                owl_class, class_expressions, annotations)

    @staticmethod
    def _create_equivalent_classes_axiom(parsed):
        equiv_classes = set()
        annotations = set()

        for part in parsed:
            if isinstance(part, OWLClassExpression):
                equiv_classes.add(part)
            elif isinstance(part, OWLAnnotation):
                annotations.add(part)
            else:
                raise RuntimeError(
                    f'Got unexpected object in EquivalentClasses axiom: {part}')

        if len(annotations) == 0:
            return OWLEquivalentClassesAxiom(equiv_classes)
        else:
            return OWLEquivalentClassesAxiom(equiv_classes, annotations)

    @staticmethod
    def _create_sub_cls_of_axiom(parsed):
        annotations = set()
        sub_cls = None
        super_cls = None

        while len(parsed) > 0:
            obj = parsed.pop(0)

            if isinstance(obj, OWLAnnotation):
                annotations.add(obj)
            else:
                if sub_cls is None:
                    sub_cls = obj
                else:
                    super_cls = obj

        assert sub_cls is not None
        assert super_cls is not None

        if len(annotations) == 0:  # without annotations
            return OWLSubClassOfAxiom(sub_cls, super_cls)
        else:
            return OWLSubClassOfAxiom(sub_cls, super_cls, annotations)

    @staticmethod
    def _create_obj_exact_cardinality(parsed):
        if len(parsed) == 2:  # no filler class given
            return OWLObjectExactCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLObjectExactCardinality(
                parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_obj_max_cardinality(parsed):
        if len(parsed) == 2:  # no filler class given
            return OWLObjectMaxCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLObjectMaxCardinality(parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_obj_min_cardinality_expression(parsed):
        if len(parsed) == 2:  # no filler class given
            return OWLObjectMinCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLObjectMinCardinality(parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_data_exact_cardinality(parsed):
        if len(parsed) == 2:  # no filler data range given
            return OWLDataExactCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLDataExactCardinality(parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_data_max_cardinality(parsed):
        if len(parsed) == 2:  # no filler data range given
            return OWLDataMaxCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLDataMaxCardinality(parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_data_min_cardinality(parsed):
        if len(parsed) == 2:  # no filler data range given
            return OWLDataMinCardinality(parsed[1], int(parsed[0]))
        else:
            return OWLDataMinCardinality(parsed[1], int(parsed[0]), parsed[2])

    @staticmethod
    def _create_declaration_axiom(parsed):
        annotations = []
        declared_entity = None

        for part in parsed:
            if isinstance(part, OWLAnnotation):
                annotations.append(part)
            else:
                declared_entity = part

        if isinstance(declared_entity, OWLClass):
            return OWLClassDeclarationAxiom(declared_entity, annotations)

        elif isinstance(declared_entity, OWLDatatype):
            return OWLDatatypeDeclarationAxiom(declared_entity, annotations)

        elif isinstance(declared_entity, OWLObjectProperty):
            return OWLObjectPropertyDeclarationAxiom(
                declared_entity, annotations)

        elif isinstance(declared_entity, OWLDataProperty):
            return OWLDataPropertyDeclarationAxiom(declared_entity, annotations)

        elif isinstance(declared_entity, OWLAnnotationProperty):
            return OWLAnnotationPropertyDeclarationAxiom(
                declared_entity, annotations)

        elif isinstance(declared_entity, OWLNamedIndividual):
            return OWLNamedIndividualDeclarationAxiom(
                declared_entity, annotations)

        else:
            raise RuntimeError(f'Unknown declaration type for '
                               f'{declared_entity}')

    @staticmethod
    def _create_literal(parsed):
        if len(parsed) == 1:
            return RDFLiteral(parsed[0])

        elif len(parsed) == 2:
            lexical_val, lang_or_type = parsed

            if isinstance(lang_or_type, URIRef) \
                    or isinstance(lang_or_type, HasIRI):
                return RDFLiteral(lexical_val, None, lang_or_type.iri)
            else:
                return RDFLiteral(lexical_val, lang_or_type)

        else:
            raise RuntimeError(
                f'Found literal with language tag and type: {parsed}')

    @staticmethod
    def _create_annotation(parsed):
        ann_prop, ann_value = parsed

        return OWLAnnotation(ann_prop, ann_value)

    def _create_full_iri(self, parsed):
        parts = parsed[0].split(':')
        parts = [p for p in parts if not p == '']

        if len(parts) == 1:
            uri_part1 = self._prefixes[OWLOntology.default_prefix_dummy]
            uri_part2 = parts[0]
        else:
            uri_part1 = self._prefixes[parts[0]]
            uri_part2 = parts[1]

        return URIRef(uri_part1 + uri_part2)

    @staticmethod
    def _create_prefix(parsed):
        res = [t for t in parsed[:] if not t == ':']
        if len(res) == 1:
            res = [OWLOntology.default_prefix_dummy] + res

        prefixes = {res[0]: res[1]}

        return prefixes

    def _concat_prefixes(self, prefixes):
        res = prefixes.pop()

        for prefix in prefixes:
            res.update(prefix)

        self._prefixes = res
        return res

    def __dbg__(self, parsed):
        """Used as hook to enter the debugger during development"""
        # import pdb; pdb.set_trace()
        a = 23
        return parsed

    def parse_file(self, file_path):
        return self.ontology_document.parseFile(file_path, True)[0]
