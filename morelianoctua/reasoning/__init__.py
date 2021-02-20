from abc import ABC, abstractmethod
from typing import Set

from rdflib import Literal

from morelianoctua.model import OWLOntology
from morelianoctua.model.axioms import OWLAxiom
from morelianoctua.model.objects.classexpression import OWLClass, \
    OWLClassExpression
from morelianoctua.model.objects.individual import OWLNamedIndividual
from morelianoctua.model.objects.property import OWLDataProperty, \
    OWLObjectPropertyExpression


class OWLReasoner(ABC):
    """
    Method descriptions copied from OWL API Java Docs (and adapted accordingly)
    """
    @abstractmethod
    def get_data_property_domains(
            self,
            data_property: OWLDataProperty,
            direct: bool = False) -> Set[OWLClass]:
        """
        Gets the named classes that are the direct or indirect domains of this
        property with respect to the imports closure of the root ontology.
        """

    @abstractmethod
    def get_data_property_values(
            self,
            individual: OWLNamedIndividual,
            data_property: OWLDataProperty) -> Set[Literal]:
        """
        Gets the data property values for the specified individual and data
        property expression.
        """

    @abstractmethod
    def get_different_individuals(
            self,
            individual: OWLNamedIndividual) -> Set[OWLNamedIndividual]:
        """
        Gets the individuals which are entailed to be different from the
        specified individual.
        """

    @abstractmethod
    def get_disjoint_classes(self, ce: OWLClassExpression) -> Set[OWLClass]:
        """
        Gets the classes that are disjoint with the specified class expression
        ce.
        """

    @abstractmethod
    def get_disjoint_data_properties(
            self,
            data_property: OWLDataProperty) -> Set[OWLDataProperty]:
        """
        Gets the data properties that are disjoint with the specified data
        property.
        """

    @abstractmethod
    def get_disjoint_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        Gets the object property expressions that are disjoint with the
        specified object property expression pe.
        """

    @abstractmethod
    def get_equivalent_classes(self, ce: OWLClassExpression) -> Set[OWLClass]:
        """
        Gets the set of named classes that are equivalent to the specified
        class expression with respect to the set of reasoner axioms.
        """

    @abstractmethod
    def get_equivalent_data_properties(
            self,
            data_property: OWLDataProperty) -> Set[OWLDataProperty]:
        """
        Gets the set of named data properties that are equivalent to the
        specified data property.
        """

    @abstractmethod
    def get_equivalent_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        Gets the set of object property expressions that are equivalent to the
        specified object property expression with respect to the set of
        reasoner axioms.
        """

    @abstractmethod
    def get_instances(
            self,
            ce: OWLClassExpression, direct: bool = False) -> Set[OWLNamedIndividual]:
        """
        Gets the individuals which are instances of the specified class
        expression.
        """

    @abstractmethod
    def get_inverse_object_properties(
            self,
            pe: OWLObjectPropertyExpression) -> Set[OWLObjectPropertyExpression]:
        """
        Gets the set of object property expressions that are the inverses of
        the specified object property expression.
        """

    @abstractmethod
    def get_object_property_domains(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        Gets the named classes that are the direct or indirect domains of this
        property.
        """

    @abstractmethod
    def get_object_property_ranges(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        Gets the named classes that are the direct or indirect ranges of this
        property.
        """

    @abstractmethod
    def get_object_property_values(
            self,
            individual: OWLNamedIndividual,
            pe: OWLObjectPropertyExpression) -> Set[OWLNamedIndividual]:
        """
        Gets the object property values for the specified individual and object
        property expression.
        """

    @abstractmethod
    def get_root_ontology(self) -> OWLOntology:
        """
        Gets the "root" ontology that is loaded into this reasoner.
        """

    @abstractmethod
    def get_same_individuals(
            self,
            individual: OWLNamedIndividual) -> Set[OWLNamedIndividual]:
        """
        Gets the individuals that are the same as the specified individual.
        """

    @abstractmethod
    def get_sub_classes(
            self,
            ce: OWLClassExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        Gets the set of named classes that are the direct or indirect
        subclasses of the specified class expression with respect to the
        reasoner axioms.
        """

    @abstractmethod
    def get_sub_data_properties(
            self,
            data_property: OWLDataProperty,
            direct: bool = False) -> Set[OWLDataProperty]:
        """
        Gets the set of named data properties that are direct or indirect
        subproperties of the specified data property expression with respect to
        the reasoner axioms.
        """

    @abstractmethod
    def get_sub_object_properties(
            self,
            pe: OWLObjectPropertyExpression,
            direct: bool = False) -> Set[OWLObjectPropertyExpression]:
        """
        Gets the set of object property expressions that are direct or indirect
        subproperties of the specified object property expression with respec
        to the reasoner axioms.
        """

    @abstractmethod
    def get_super_classes(
            self,
            ce: OWLClassExpression,
            direct: bool = False) -> Set[OWLClass]:
        """
        Gets the set of named classes that are direct or indirect super classes
        of the specified class expression with respect to the reasoner axioms.
        """

    @abstractmethod
    def get_super_data_properties(
            self,
            data_property: OWLDataProperty,
            direct: bool = True) -> Set[OWLDataProperty]:
        """
        Gets the set of named data properties that are direct or indirect super
        properties of the specified data property with respect to the reasoner
        axioms.
        """

    @abstractmethod
    def get_super_object_properties(self, pe: OWLObjectPropertyExpression, direct: bool = False) -> Set[OWLObjectPropertyExpression]:
        """
        Gets the set of object property expressions that are direct or indirect
        super properties of the specified object property expression with
        respect to the reasoner axioms.
        """

    @abstractmethod
    def get_types(self, individual: OWLNamedIndividual, direct: bool = False) -> Set[OWLClass]:
        """
        Gets the named classes which are (potentially direct) types of the
        specified named individual.
        """

    @abstractmethod
    def get_unsatisfiable_classes(self) -> Set[OWLClass]:
        """
        A convenience method that obtains the classes in the signature of the
        root ontology that are unsatisfiable.
        """

    @abstractmethod
    def is_consistent(self) -> bool:
        """
        Determines if the set of reasoner axioms is consistent.
        """

    @abstractmethod
    def is_entailed(self, axiom: OWLAxiom) -> bool:
        """
        A convenience method that determines if the specified axiom is entailed
        by the set of reasoner axioms.
        """
    @abstractmethod
    def is_satisfiable(self, ce: OWLClassExpression) -> bool:
        """
        A convenience method that determines if the specified class expression
        is satisfiable with respect to the reasoner axioms.
        """

    @abstractmethod
    def get_classes(self):
        pass

    @abstractmethod
    def get_object_properties(self):
        pass

    @abstractmethod
    def get_data_properties(self):
        pass

    @abstractmethod
    def get_annotation_properties(self):
        pass

    @abstractmethod
    def get_literals(self):
        pass

    @abstractmethod
    def get_datatypes(self):
        pass
