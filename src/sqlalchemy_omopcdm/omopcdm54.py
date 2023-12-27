import datetime
import decimal
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class OMOPCDMModelBase(DeclarativeBase):
    """
    Base for OMOP Common Data Model v5.4 Models
    https://ohdsi.github.io/CommonDataModel/cdm54.html
    """

    pass


class Cohort(OMOPCDMModelBase):
    """
    The COHORT table contains records of subjects that satisfy a given set of
    criteria for a duration of time. The definition of the cohort is contained
    within the COHORT_DEFINITION table. It is listed as part of the RESULTS
    schema because it is a table that users of the database as well as tools
    such as ATLAS need to be able to write to. The CDM and Vocabulary tables
    are all read-only so it is suggested that the COHORT and COHORT_DEFINTION
    tables are kept in a separate schema to alleviate confusion.

    ETL Conventions

    Cohorts typically include patients diagnosed with a specific condition,
    patients exposed to a particular drug, but can also be Providers who have
    performed a specific Procedure. Cohort records must have a Start Date and
    an End Date, but the End Date may be set to Start Date or could have an
    applied censor date using the Observation Period Start Date. Cohort records
    must contain a Subject Id, which can refer to the Person, Provider, Visit
    record or Care Site though they are most often Person Ids. The Cohort
    Definition will define the type of subject through the subject concept id.
    A subject can belong (or not belong) to a cohort at any moment in time. A
    subject can only have one record in the cohort table for any moment of
    time, i.e. it is not possible for a person to contain multiple records
    indicating cohort membership that are overlapping in time

    https://ohdsi.github.io/CommonDataModel/cdm54.html#COHORT
    """

    __tablename__ = "cohort"
    __table_args__ = (
        PrimaryKeyConstraint(
            "cohort_definition_id",
            "subject_id",
            "cohort_start_date",
            "cohort_end_date",
            name="eh_composite_pk_cohort",
        ),
    )
    cohort_definition_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    cohort_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)


class Concept(OMOPCDMModelBase):
    """
    The Standardized Vocabularies contains records, or Concepts, that uniquely
    identify each fundamental unit of meaning used to express clinical
    information in all domain tables of the CDM. Concepts are derived from
    vocabularies, which represent clinical information across a domain (e.g.
    conditions, drugs, procedures) through the use of codes and associated
    descriptions. Some Concepts are designated Standard Concepts, meaning these
    Concepts can be used as normative expressions of a clinical entity within
    the OMOP Common Data Model and within standardized analytics. Each Standard
    Concept belongs to one domain, which defines the location where the Concept
    would be expected to occur within data tables of the CDM.

    Concepts can represent broad categories (like 'Cardiovascular disease'),
    detailed clinical elements ('Myocardial infarction of the anterolateral
    wall') or modifying characteristics and attributes that define Concepts at
    various levels of detail (severity of a disease, associated morphology,
    etc.).

    Records in the Standardized Vocabularies tables are derived from national
    or international vocabularies such as SNOMED-CT, RxNorm, and LOINC, or
    custom Concepts defined to cover various aspects of observational data
    analysis.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONCEPT
    """

    __tablename__ = "concept"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_class_id"],
            ["concept_class.concept_class_id"],
            name="fpk_concept_concept_class_id",
        ),
        ForeignKeyConstraint(
            ["domain_id"], ["domain.domain_id"], name="fpk_concept_domain_id"
        ),
        ForeignKeyConstraint(
            ["vocabulary_id"],
            ["vocabulary.vocabulary_id"],
            name="fpk_concept_vocabulary_id",
        ),
        PrimaryKeyConstraint("concept_id", name="xpk_concept"),
        Index("idx_concept_class_id", "concept_class_id"),
        Index("idx_concept_code", "concept_code"),
        Index("idx_concept_concept_id", "concept_id"),
        Index("idx_concept_domain_id", "domain_id"),
        Index("idx_concept_vocabluary_id", "vocabulary_id"),
    )
    concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_name: Mapped[str] = mapped_column(String(255))
    domain_id: Mapped[str] = mapped_column(String(20))
    vocabulary_id: Mapped[str] = mapped_column(String(20))
    concept_class_id: Mapped[str] = mapped_column(String(20))
    concept_code: Mapped[str] = mapped_column(String(50))
    valid_start_date: Mapped[datetime.date] = mapped_column(Date)
    valid_end_date: Mapped[datetime.date] = mapped_column(Date)
    standard_concept: Mapped[Optional[str]] = mapped_column(String(1))
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1))
    concept_class: Mapped["ConceptClass"] = relationship(
        "ConceptClass", foreign_keys=[concept_class_id]
    )
    domain: Mapped["Domain"] = relationship("Domain", foreign_keys=[domain_id])
    vocabulary: Mapped["Vocabulary"] = relationship(
        "Vocabulary", foreign_keys=[vocabulary_id]
    )


class ConceptClass(OMOPCDMModelBase):
    """
    The CONCEPT_CLASS table is a reference table, which includes a list of the
    classifications used to differentiate Concepts within a given Vocabulary.
    This reference table is populated with a single record for each Concept
    Class.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONCEPT_CLASS
    """

    __tablename__ = "concept_class"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_class_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_class_concept_class_concept_id",
        ),
        PrimaryKeyConstraint("concept_class_id", name="xpk_concept_class"),
        Index("idx_concept_class_class_id", "concept_class_id"),
    )
    concept_class_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    concept_class_name: Mapped[str] = mapped_column(String(255))
    concept_class_concept_id: Mapped[int] = mapped_column(Integer)
    concept_class_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[concept_class_concept_id]
    )


class Domain(OMOPCDMModelBase):
    """
    The DOMAIN table includes a list of OMOP-defined Domains the Concepts of
    the Standardized Vocabularies can belong to. A Domain defines the set of
    allowable Concepts for the standardized fields in the CDM tables. For
    example, the "Condition" Domain contains Concepts that describe a condition
    of a patient, and these Concepts can only be stored in the
    condition_concept_id field of the CONDITION_OCCURRENCE and CONDITION_ERA
    tables. This reference table is populated with a single record for each
    Domain and includes a descriptive name for the Domain.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DOMAIN
    """

    __tablename__ = "domain"
    __table_args__ = (
        ForeignKeyConstraint(
            ["domain_concept_id"],
            ["concept.concept_id"],
            name="fpk_domain_domain_concept_id",
        ),
        PrimaryKeyConstraint("domain_id", name="xpk_domain"),
        Index("idx_domain_domain_id", "domain_id"),
    )
    domain_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    domain_name: Mapped[str] = mapped_column(String(255))
    domain_concept_id: Mapped[int] = mapped_column(Integer)
    domain_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[domain_concept_id]
    )


class Vocabulary(OMOPCDMModelBase):
    """
    The VOCABULARY table includes a list of the Vocabularies collected from
    various sources or created de novo by the OMOP community. This reference
    table is populated with a single record for each Vocabulary source and
    includes a descriptive name and other associated attributes for the
    Vocabulary.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#VOCABULARY
    """

    __tablename__ = "vocabulary"
    __table_args__ = (
        ForeignKeyConstraint(
            ["vocabulary_concept_id"],
            ["concept.concept_id"],
            name="fpk_vocabulary_vocabulary_concept_id",
        ),
        PrimaryKeyConstraint("vocabulary_id", name="xpk_vocabulary"),
        Index("idx_vocabulary_vocabulary_id", "vocabulary_id"),
    )
    vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    vocabulary_name: Mapped[str] = mapped_column(String(255))
    vocabulary_concept_id: Mapped[int] = mapped_column(Integer)
    vocabulary_reference: Mapped[Optional[str]] = mapped_column(String(255))
    vocabulary_version: Mapped[Optional[str]] = mapped_column(String(255))
    vocabulary_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[vocabulary_concept_id]
    )


class CdmSource(OMOPCDMModelBase):
    """
    The CDM_SOURCE table contains detail about the source database and the
    process used to transform the data into the OMOP Common Data Model.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CDM_SOURCE
    """

    __tablename__ = "cdm_source"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cdm_version_concept_id"],
            ["concept.concept_id"],
            name="fpk_cdm_source_cdm_version_concept_id",
        ),
        PrimaryKeyConstraint(
            "cdm_source_name",
            "cdm_source_abbreviation",
            "cdm_holder",
            "source_release_date",
            "cdm_release_date",
            "cdm_version_concept_id",
            "vocabulary_version",
            name="eh_composite_pk_cdm_source",
        ),
    )
    cdm_source_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    cdm_source_abbreviation: Mapped[str] = mapped_column(String(25), primary_key=True)
    cdm_holder: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_release_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    cdm_release_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    cdm_version_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vocabulary_version: Mapped[str] = mapped_column(String(20), primary_key=True)
    source_description: Mapped[Optional[str]] = mapped_column(Text)
    source_documentation_reference: Mapped[Optional[str]] = mapped_column(String(255))
    cdm_etl_reference: Mapped[Optional[str]] = mapped_column(String(255))
    cdm_version: Mapped[Optional[str]] = mapped_column(String(10))
    cdm_version_concept: Mapped["Concept"] = relationship("Concept")


class CohortDefinition(OMOPCDMModelBase):
    """
    The COHORT_DEFINITION table contains records defining a Cohort derived from
    the data through the associated description and syntax and upon
    instantiation (execution of the algorithm) placed into the COHORT table.
    Cohorts are a set of subjects that satisfy a given combination of inclusion
    criteria for a duration of time. The COHORT_DEFINITION table provides a
    standardized structure for maintaining the rules governing the inclusion of
    a subject into a cohort, and can store operational programming code to
    instantiate the cohort within the OMOP Common Data Model.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#COHORT_DEFINITION
    """

    __tablename__ = "cohort_definition"
    __table_args__ = (
        ForeignKeyConstraint(
            ["definition_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_cohort_definition_definition_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["subject_concept_id"],
            ["concept.concept_id"],
            name="fpk_cohort_definition_subject_concept_id",
        ),
        PrimaryKeyConstraint(
            "cohort_definition_id",
            "cohort_definition_name",
            "definition_type_concept_id",
            "subject_concept_id",
            name="eh_composite_pk_cohort_definition",
        ),
    )
    cohort_definition_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_definition_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    definition_type_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_definition_description: Mapped[Optional[str]] = mapped_column(Text)
    cohort_definition_syntax: Mapped[Optional[str]] = mapped_column(Text)
    cohort_initiation_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    definition_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[definition_type_concept_id]
    )
    subject_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[subject_concept_id]
    )


class ConceptAncestor(OMOPCDMModelBase):
    """
    The CONCEPT_ANCESTOR table is designed to simplify observational analysis
    by providing the complete hierarchical relationships between Concepts. Only
    direct parent-child relationships between Concepts are stored in the
    CONCEPT_RELATIONSHIP table. To determine higher level ancestry connections,
    all individual direct relationships would have to be navigated at analysis
    time. The CONCEPT_ANCESTOR table includes records for all parent-child
    relationships, as well as grandparent-grandchild relationships and those of
    any other level of lineage. Using the CONCEPT_ANCESTOR table allows for
    querying for all descendants of a hierarchical concept. For example, drug
    ingredients and drug products are all descendants of a drug class ancestor.

    This table is entirely derived from the CONCEPT, CONCEPT_RELATIONSHIP and
    RELATIONSHIP tables.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONCEPT_ANCESTOR
    """

    __tablename__ = "concept_ancestor"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ancestor_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_ancestor_ancestor_concept_id",
        ),
        ForeignKeyConstraint(
            ["descendant_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_ancestor_descendant_concept_id",
        ),
        PrimaryKeyConstraint(
            "ancestor_concept_id",
            "descendant_concept_id",
            "min_levels_of_separation",
            "max_levels_of_separation",
            name="eh_composite_pk_concept_ancestor",
        ),
        Index("idx_concept_ancestor_id_1", "ancestor_concept_id"),
        Index("idx_concept_ancestor_id_2", "descendant_concept_id"),
    )
    ancestor_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    descendant_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    min_levels_of_separation: Mapped[int] = mapped_column(Integer, primary_key=True)
    max_levels_of_separation: Mapped[int] = mapped_column(Integer, primary_key=True)
    ancestor_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ancestor_concept_id]
    )
    descendant_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[descendant_concept_id]
    )


class ConceptSynonym(OMOPCDMModelBase):
    """
    The CONCEPT_SYNONYM table is used to store alternate names and descriptions
    for Concepts.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONCEPT_SYNONYM
    """

    __tablename__ = "concept_synonym"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_synonym_concept_id",
        ),
        ForeignKeyConstraint(
            ["language_concept_id"],
            ["concept.concept_id"],
            name="fpk_concept_synonym_language_concept_id",
        ),
        PrimaryKeyConstraint(
            "concept_id",
            "concept_synonym_name",
            "language_concept_id",
            name="eh_composite_pk_concept_synonym",
        ),
        Index("idx_concept_synonym_id", "concept_id"),
    )
    concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_synonym_name: Mapped[str] = mapped_column(String(1000), primary_key=True)
    language_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id])
    language_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[language_concept_id]
    )


class Cost(OMOPCDMModelBase):
    """
    The COST table captures records containing the cost of any medical event
    recorded in one of the OMOP clinical event tables such as DRUG_EXPOSURE,
    PROCEDURE_OCCURRENCE, VISIT_OCCURRENCE, VISIT_DETAIL, DEVICE_OCCURRENCE,
    OBSERVATION or MEASUREMENT.

    Each record in the cost table account for the amount of money transacted
    for the clinical event. So, the COST table may be used to represent both
    receivables (charges) and payments (paid), each transaction type
    represented by its COST_CONCEPT_ID. The COST_TYPE_CONCEPT_ID field will use
    concepts in the Standardized Vocabularies to designate the source
    (provenance) of the cost data. A reference to the health plan information
    in the PAYER_PLAN_PERIOD table is stored in the record for information used
    for the adjudication system to determine the persons benefit for the
    clinical event.

    User Guide

    When dealing with summary costs, the cost of the goods or services the
    provider provides is often not known directly, but derived from the
    hospital charges multiplied by an average cost-to-charge ratio.

    ETL Conventions

    One cost record is generated for each response by a payer. In a claims
    databases, the payment and payment terms reported by the payer for the
    goods or services billed will generate one cost record. If the source data
    has payment information for more than one payer (i.e. primary insurance and
    secondary insurance payment for one entity), then a cost record is created
    for each reporting payer. Therefore, it is possible for one procedure to
    have multiple cost records for each payer, but typically it contains one or
    no record per entity. Payer reimbursement cost records will be identified
    by using the PAYER_PLAN_ID field. Drug costs are composed of ingredient
    cost (the amount charged by the wholesale distributor or manufacturer), the
    dispensing fee (the amount charged by the pharmacy and the sales tax).

    https://ohdsi.github.io/CommonDataModel/cdm54.html#COST
    """

    __tablename__ = "cost"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cost_domain_id"], ["domain.domain_id"], name="fpk_cost_cost_domain_id"
        ),
        ForeignKeyConstraint(
            ["cost_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_cost_cost_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["currency_concept_id"],
            ["concept.concept_id"],
            name="fpk_cost_currency_concept_id",
        ),
        ForeignKeyConstraint(
            ["drg_concept_id"], ["concept.concept_id"], name="fpk_cost_drg_concept_id"
        ),
        ForeignKeyConstraint(
            ["revenue_code_concept_id"],
            ["concept.concept_id"],
            name="fpk_cost_revenue_code_concept_id",
        ),
        PrimaryKeyConstraint("cost_id", name="xpk_cost"),
        Index("idx_cost_event_id", "cost_event_id"),
    )
    cost_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cost_event_id: Mapped[int] = mapped_column(Integer)
    cost_domain_id: Mapped[str] = mapped_column(String(20))
    cost_type_concept_id: Mapped[int] = mapped_column(Integer)
    currency_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    total_charge: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    total_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    total_paid: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_payer: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_patient: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_copay: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_coinsurance: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_patient_deductible: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_by_primary: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_ingredient_cost: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    paid_dispensing_fee: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    payer_plan_period_id: Mapped[Optional[int]] = mapped_column(Integer)
    amount_allowed: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    revenue_code_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    revenue_code_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    drg_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    drg_source_value: Mapped[Optional[str]] = mapped_column(String(3))
    cost_domain: Mapped["Domain"] = relationship("Domain")
    cost_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[cost_type_concept_id]
    )
    currency_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[currency_concept_id]
    )
    drg_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drg_concept_id]
    )
    revenue_code_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[revenue_code_concept_id]
    )


class DrugStrength(OMOPCDMModelBase):
    """
    The DRUG_STRENGTH table contains structured content about the amount or
    concentration and associated units of a specific ingredient contained
    within a particular drug product. This table is supplemental information to
    support standardized analysis of drug utilization.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DRUG_STRENGTH
    """

    __tablename__ = "drug_strength"
    __table_args__ = (
        ForeignKeyConstraint(
            ["amount_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_amount_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["denominator_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_denominator_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["drug_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_drug_concept_id",
        ),
        ForeignKeyConstraint(
            ["ingredient_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_ingredient_concept_id",
        ),
        ForeignKeyConstraint(
            ["numerator_unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_strength_numerator_unit_concept_id",
        ),
        PrimaryKeyConstraint(
            "drug_concept_id",
            "ingredient_concept_id",
            "valid_start_date",
            "valid_end_date",
            name="eh_composite_pk_drug_strength",
        ),
        Index("idx_drug_strength_id_1", "drug_concept_id"),
        Index("idx_drug_strength_id_2", "ingredient_concept_id"),
    )
    drug_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    amount_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    amount_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    numerator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    numerator_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    denominator_value: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    denominator_unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    box_size: Mapped[Optional[int]] = mapped_column(Integer)
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1))
    amount_unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[amount_unit_concept_id]
    )
    denominator_unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[denominator_unit_concept_id]
    )
    drug_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_concept_id]
    )
    ingredient_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ingredient_concept_id]
    )
    numerator_unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[numerator_unit_concept_id]
    )


class FactRelationship(OMOPCDMModelBase):
    """
    The FACT_RELATIONSHIP table contains records about the relationships
    between facts stored as records in any table of the CDM. Relationships can
    be defined between facts from the same domain, or different domains.
    Examples of Fact Relationships include: Person relationships
    (parent-child), care site relationships (hierarchical organizational
    structure of facilities within a health system), indication relationship
    (between drug exposures and associated conditions), usage relationships (of
    devices during the course of an associated procedure), or facts derived
    from one another (measurements derived from an associated specimen).

    ETL Conventions

    All relationships are directional, and each relationship is represented
    twice symmetrically within the FACT_RELATIONSHIP table. For example, two
    persons if person_id = 1 is the mother of person_id = 2 two records are in
    the FACT_RELATIONSHIP table (all strings in fact concept_id records in the
    Concept table: - Person, 1, Person, 2, parent of - Person, 2, Person, 1,
    child of

    https://ohdsi.github.io/CommonDataModel/cdm54.html#FACT_RELATIONSHIP
    """

    __tablename__ = "fact_relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["domain_concept_id_1"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_domain_concept_id_1",
        ),
        ForeignKeyConstraint(
            ["domain_concept_id_2"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_domain_concept_id_2",
        ),
        ForeignKeyConstraint(
            ["relationship_concept_id"],
            ["concept.concept_id"],
            name="fpk_fact_relationship_relationship_concept_id",
        ),
        PrimaryKeyConstraint(
            "domain_concept_id_1",
            "fact_id_1",
            "domain_concept_id_2",
            "fact_id_2",
            "relationship_concept_id",
            name="eh_composite_pk_fact_relationship",
        ),
        Index("idx_fact_relationship_id1", "domain_concept_id_1"),
        Index("idx_fact_relationship_id2", "domain_concept_id_2"),
        Index("idx_fact_relationship_id3", "relationship_concept_id"),
    )
    domain_concept_id_1: Mapped[int] = mapped_column(Integer, primary_key=True)
    fact_id_1: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain_concept_id_2: Mapped[int] = mapped_column(Integer, primary_key=True)
    fact_id_2: Mapped[int] = mapped_column(Integer, primary_key=True)
    relationship_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[domain_concept_id_1]
    )
    concept_: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[domain_concept_id_2]
    )
    relationship_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[relationship_concept_id]
    )


class Location(OMOPCDMModelBase):
    """
    The LOCATION table represents a generic way to capture physical location or
    address information of Persons and Care Sites.

    User Guide

    The current iteration of the LOCATION table is US centric. Until a major
    release to correct this, certain fields can be used to represent different
    international values.  - STATE can also be used for province or district-
    ZIP is also the postal code or postcode - COUNTY can also be used to
    represent region

    ETL Conventions

    Each address or Location is unique and is present only once in the table.
    Locations do not contain names, such as the name of a hospital. In order to
    construct a full address that can be used in the postal service, the
    address information from the Location needs to be combined with information
    from the Care Site.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#LOCATION
    """

    __tablename__ = "location"
    __table_args__ = (
        ForeignKeyConstraint(
            ["country_concept_id"],
            ["concept.concept_id"],
            name="fpk_location_country_concept_id",
        ),
        PrimaryKeyConstraint("location_id", name="xpk_location"),
        Index("idx_location_id_1", "location_id"),
    )
    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    address_1: Mapped[Optional[str]] = mapped_column(String(50))
    address_2: Mapped[Optional[str]] = mapped_column(String(50))
    city: Mapped[Optional[str]] = mapped_column(String(50))
    state: Mapped[Optional[str]] = mapped_column(String(2))
    zip: Mapped[Optional[str]] = mapped_column(String(9))
    county: Mapped[Optional[str]] = mapped_column(String(20))
    location_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    country_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    country_source_value: Mapped[Optional[str]] = mapped_column(String(80))
    latitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    longitude: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    country_concept: Mapped["Concept"] = relationship("Concept")


class Metadata(OMOPCDMModelBase):
    """
    The METADATA table contains metadata information about a dataset that has
    been transformed to the OMOP Common Data Model.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#METADATA
    """

    __tablename__ = "metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["metadata_concept_id"],
            ["concept.concept_id"],
            name="fpk_metadata_metadata_concept_id",
        ),
        ForeignKeyConstraint(
            ["metadata_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_metadata_metadata_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"],
            ["concept.concept_id"],
            name="fpk_metadata_value_as_concept_id",
        ),
        PrimaryKeyConstraint("metadata_id", name="xpk_metadata"),
        Index("idx_metadata_concept_id_1", "metadata_concept_id"),
    )
    metadata_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    metadata_concept_id: Mapped[int] = mapped_column(Integer)
    metadata_type_concept_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(250))
    value_as_string: Mapped[Optional[str]] = mapped_column(String(250))
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    metadata_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    metadata_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    metadata_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[metadata_concept_id]
    )
    metadata_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[metadata_type_concept_id]
    )
    value_as_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )


class NoteNlp(OMOPCDMModelBase):
    """
    The NOTE_NLP table encodes all output of NLP on clinical notes. Each row
    represents a single extracted term from a note.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#NOTE_NLP
    """

    __tablename__ = "note_nlp"
    __table_args__ = (
        ForeignKeyConstraint(
            ["note_nlp_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_nlp_note_nlp_concept_id",
        ),
        ForeignKeyConstraint(
            ["note_nlp_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_nlp_note_nlp_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["section_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_nlp_section_concept_id",
        ),
        PrimaryKeyConstraint("note_nlp_id", name="xpk_note_nlp"),
        Index("idx_note_nlp_concept_id_1", "note_nlp_concept_id"),
        Index("idx_note_nlp_note_id_1", "note_id"),
    )
    note_nlp_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    note_id: Mapped[int] = mapped_column(Integer)
    lexical_variant: Mapped[str] = mapped_column(String(250))
    nlp_date: Mapped[datetime.date] = mapped_column(Date)
    section_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    snippet: Mapped[Optional[str]] = mapped_column(String(250))
    offset: Mapped[Optional[str]] = mapped_column(String(50))
    note_nlp_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    note_nlp_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    nlp_system: Mapped[Optional[str]] = mapped_column(String(250))
    nlp_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    term_exists: Mapped[Optional[str]] = mapped_column(String(1))
    term_temporal: Mapped[Optional[str]] = mapped_column(String(50))
    term_modifiers: Mapped[Optional[str]] = mapped_column(String(2000))
    note_nlp_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_nlp_concept_id]
    )
    note_nlp_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_nlp_source_concept_id]
    )
    section_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[section_concept_id]
    )


class Relationship(OMOPCDMModelBase):
    """
    The RELATIONSHIP table provides a reference list of all types of
    relationships that can be used to associate any two concepts in the
    CONCEPT_RELATIONSHP table.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#RELATIONSHIP
    """

    __tablename__ = "relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["relationship_concept_id"],
            ["concept.concept_id"],
            name="fpk_relationship_relationship_concept_id",
        ),
        PrimaryKeyConstraint("relationship_id", name="xpk_relationship"),
        Index("idx_relationship_rel_id", "relationship_id"),
    )
    relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    relationship_name: Mapped[str] = mapped_column(String(255))
    is_hierarchical: Mapped[str] = mapped_column(String(1))
    defines_ancestry: Mapped[str] = mapped_column(String(1))
    reverse_relationship_id: Mapped[str] = mapped_column(String(20))
    relationship_concept_id: Mapped[int] = mapped_column(Integer)
    relationship_concept: Mapped["Concept"] = relationship("Concept")


class SourceToConceptMap(OMOPCDMModelBase):
    """
    The source to concept map table is a legacy data structure within the OMOP
    Common Data Model, recommended for use in ETL processes to maintain local
    source codes which are not available as Concepts in the Standardized
    Vocabularies, and to establish mappings for each source code into a
    Standard Concept as target_concept_ids that can be used to populate the
    Common Data Model tables. The SOURCE_TO_CONCEPT_MAP table is no longer
    populated with content within the Standardized Vocabularies published to
    the OMOP community.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#SOURCE_TO_CONCEPT_MAP
    """

    __tablename__ = "source_to_concept_map"
    __table_args__ = (
        ForeignKeyConstraint(
            ["source_concept_id"],
            ["concept.concept_id"],
            name="fpk_source_to_concept_map_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["target_concept_id"],
            ["concept.concept_id"],
            name="fpk_source_to_concept_map_target_concept_id",
        ),
        ForeignKeyConstraint(
            ["target_vocabulary_id"],
            ["vocabulary.vocabulary_id"],
            name="fpk_source_to_concept_map_target_vocabulary_id",
        ),
        PrimaryKeyConstraint(
            "source_code",
            "source_concept_id",
            "source_vocabulary_id",
            "target_concept_id",
            "target_vocabulary_id",
            "valid_start_date",
            "valid_end_date",
            name="eh_composite_pk_source_to_concept_map",
        ),
        Index("idx_source_to_concept_map_1", "source_vocabulary_id"),
        Index("idx_source_to_concept_map_2", "target_vocabulary_id"),
        Index("idx_source_to_concept_map_3", "target_concept_id"),
        Index("idx_source_to_concept_map_c", "source_code"),
    )
    source_code: Mapped[str] = mapped_column(String(50), primary_key=True)
    source_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    target_concept_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    source_code_description: Mapped[Optional[str]] = mapped_column(String(255))
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1))
    source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[source_concept_id]
    )
    target_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[target_concept_id]
    )
    target_vocabulary: Mapped["Vocabulary"] = relationship("Vocabulary")


class CareSite(OMOPCDMModelBase):
    """
    The CARE_SITE table contains a list of uniquely identified institutional
    (physical or organizational) units where healthcare delivery is practiced
    (offices, wards, hospitals, clinics, etc.).

    ETL Conventions

    Care site is a unique combination of location_id and
    place_of_service_source_value. Care site does not take into account the
    provider (human) information such a specialty. Many source data do not make
    a distinction between individual and institutional providers. The CARE_SITE
    table contains the institutional providers. If the source, instead of
    uniquely identifying individual Care Sites, only provides limited
    information such as Place of Service, generic or "pooled" Care Site records
    are listed in the CARE_SITE table. There can be hierarchical and business
    relationships between Care Sites. For example, wards can belong to clinics
    or departments, which can in turn belong to hospitals, which in turn can
    belong to hospital systems, which in turn can belong to HMOs.The
    relationships between Care Sites are defined in the FACT_RELATIONSHIP
    table.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CARE_SITE
    """

    __tablename__ = "care_site"
    __table_args__ = (
        ForeignKeyConstraint(
            ["location_id"], ["location.location_id"], name="fpk_care_site_location_id"
        ),
        ForeignKeyConstraint(
            ["place_of_service_concept_id"],
            ["concept.concept_id"],
            name="fpk_care_site_place_of_service_concept_id",
        ),
        PrimaryKeyConstraint("care_site_id", name="xpk_care_site"),
        Index("idx_care_site_id_1", "care_site_id"),
    )
    care_site_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    care_site_name: Mapped[Optional[str]] = mapped_column(String(255))
    place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    place_of_service_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped["Location"] = relationship("Location")
    place_of_service_concept: Mapped["Concept"] = relationship("Concept")


class ConceptRelationship(OMOPCDMModelBase):
    """
    The CONCEPT_RELATIONSHIP table contains records that define direct
    relationships between any two Concepts and the nature or type of the
    relationship. Each type of a relationship is defined in the RELATIONSHIP
    table.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONCEPT_RELATIONSHIP
    """

    __tablename__ = "concept_relationship"
    __table_args__ = (
        ForeignKeyConstraint(
            ["concept_id_1"],
            ["concept.concept_id"],
            name="fpk_concept_relationship_concept_id_1",
        ),
        ForeignKeyConstraint(
            ["concept_id_2"],
            ["concept.concept_id"],
            name="fpk_concept_relationship_concept_id_2",
        ),
        ForeignKeyConstraint(
            ["relationship_id"],
            ["relationship.relationship_id"],
            name="fpk_concept_relationship_relationship_id",
        ),
        PrimaryKeyConstraint(
            "concept_id_1",
            "concept_id_2",
            "relationship_id",
            "valid_start_date",
            "valid_end_date",
            name="eh_composite_pk_concept_relationship",
        ),
        Index("idx_concept_relationship_id_1", "concept_id_1"),
        Index("idx_concept_relationship_id_2", "concept_id_2"),
        Index("idx_concept_relationship_id_3", "relationship_id"),
    )
    concept_id_1: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_id_2: Mapped[int] = mapped_column(Integer, primary_key=True)
    relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    valid_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    valid_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    invalid_reason: Mapped[Optional[str]] = mapped_column(String(1))
    concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id_1])
    concept_: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id_2])
    relationship_: Mapped["Relationship"] = relationship("Relationship")


class Provider(OMOPCDMModelBase):
    """
    The PROVIDER table contains a list of uniquely identified healthcare
    providers. These are individuals providing hands-on healthcare to patients,
    such as physicians, nurses, midwives, physical therapists etc.

    User Guide

    Many sources do not make a distinction between individual and institutional
    providers. The PROVIDER table contains the individual providers. If the
    source, instead of uniquely identifying individual providers, only provides
    limited information such as specialty, generic or 'pooled' Provider records
    are listed in the PROVIDER table.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#PROVIDER
    """

    __tablename__ = "provider"
    __table_args__ = (
        ForeignKeyConstraint(
            ["care_site_id"],
            ["care_site.care_site_id"],
            name="fpk_provider_care_site_id",
        ),
        ForeignKeyConstraint(
            ["gender_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_gender_concept_id",
        ),
        ForeignKeyConstraint(
            ["gender_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_gender_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["specialty_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_specialty_concept_id",
        ),
        ForeignKeyConstraint(
            ["specialty_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_provider_specialty_source_concept_id",
        ),
        PrimaryKeyConstraint("provider_id", name="xpk_provider"),
        Index("idx_provider_id_1", "provider_id"),
    )
    provider_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[Optional[str]] = mapped_column(String(255))
    npi: Mapped[Optional[str]] = mapped_column(String(20))
    dea: Mapped[Optional[str]] = mapped_column(String(20))
    specialty_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
    year_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
    gender_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    provider_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    specialty_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    specialty_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    gender_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site: Mapped["CareSite"] = relationship("CareSite")
    gender_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[gender_concept_id]
    )
    gender_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[gender_source_concept_id]
    )
    specialty_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specialty_concept_id]
    )
    specialty_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specialty_source_concept_id]
    )


class Person(OMOPCDMModelBase):
    """
    This table serves as the central identity management for all Persons in the
    database. It contains records that uniquely identify each person or
    patient, and some demographic information.

    User Guide

    All records in this table are independent Persons.

    ETL Conventions

    All Persons in a database needs one record in this table, unless they fail
    data quality requirements specified in the ETL. Persons with no Events
    should have a record nonetheless. If more than one data source contributes
    Events to the database, Persons must be reconciled, if possible, across the
    sources to create one single record per Person. The content of the
    BIRTH_DATETIME must be equivalent to the content of BIRTH_DAY, BIRTH_MONTH
    and BIRTH_YEAR.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#PERSON
    """

    __tablename__ = "person"
    __table_args__ = (
        ForeignKeyConstraint(
            ["care_site_id"], ["care_site.care_site_id"], name="fpk_person_care_site_id"
        ),
        ForeignKeyConstraint(
            ["ethnicity_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_ethnicity_concept_id",
        ),
        ForeignKeyConstraint(
            ["ethnicity_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_ethnicity_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["gender_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_gender_concept_id",
        ),
        ForeignKeyConstraint(
            ["gender_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_gender_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["location_id"], ["location.location_id"], name="fpk_person_location_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_person_provider_id"
        ),
        ForeignKeyConstraint(
            ["race_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_race_concept_id",
        ),
        ForeignKeyConstraint(
            ["race_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_person_race_source_concept_id",
        ),
        PrimaryKeyConstraint("person_id", name="xpk_person"),
        Index("idx_gender", "gender_concept_id"),
        Index("idx_person_id", "person_id"),
    )
    person_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender_concept_id: Mapped[int] = mapped_column(Integer)
    year_of_birth: Mapped[int] = mapped_column(Integer)
    race_concept_id: Mapped[int] = mapped_column(Integer)
    ethnicity_concept_id: Mapped[int] = mapped_column(Integer)
    month_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
    day_of_birth: Mapped[Optional[int]] = mapped_column(Integer)
    birth_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
    person_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    gender_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    gender_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    race_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    race_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    ethnicity_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    ethnicity_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site: Mapped["CareSite"] = relationship("CareSite")
    ethnicity_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ethnicity_concept_id]
    )
    ethnicity_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[ethnicity_source_concept_id]
    )
    gender_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[gender_concept_id]
    )
    gender_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[gender_source_concept_id]
    )
    location: Mapped["Location"] = relationship("Location")
    provider: Mapped["Provider"] = relationship("Provider")
    race_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[race_concept_id]
    )
    race_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[race_source_concept_id]
    )


class ConditionEra(OMOPCDMModelBase):
    """
    A Condition Era is defined as a span of time when the Person is assumed to
    have a given condition. Similar to Drug Eras, Condition Eras are
    chronological periods of Condition Occurrence. Combining individual
    Condition Occurrences into a single Condition Era serves two purposes:

    ETL Conventions

    Each Condition Era corresponds to one or many Condition Occurrence records
    that form a continuous interval. The condition_concept_id field contains
    Concepts that are identical to those of the CONDITION_OCCURRENCE table
    records that make up the Condition Era. In contrast to Drug Eras, Condition
    Eras are not aggregated to contain Conditions of different hierarchical
    layers. The SQl Script for generating CONDITION_ERA records can be found
    here The Condition Era Start Date is the start date of the first Condition
    Occurrence. The Condition Era End Date is the end date of the last
    Condition Occurrence. Condition Eras are built with a Persistence Window of
    30 days, meaning, if no occurrence of the same condition_concept_id happens
    within 30 days of any one occurrence, it will be considered the
    condition_era_end_date.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONDITION_ERA
    """

    __tablename__ = "condition_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["condition_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_era_condition_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_condition_era_person_id"
        ),
        PrimaryKeyConstraint("condition_era_id", name="xpk_condition_era"),
        Index("idx_condition_era_concept_id_1", "condition_concept_id"),
        Index("idx_condition_era_person_id_1", "person_id"),
    )
    condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer)
    condition_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    condition_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    condition_occurrence_count: Mapped[Optional[int]] = mapped_column(Integer)
    condition_concept: Mapped["Concept"] = relationship("Concept")
    person: Mapped["Person"] = relationship("Person")


class Death(OMOPCDMModelBase):
    """
    The death domain contains the clinical event for how and when a Person
    dies. A person can have up to one record if the source system contains
    evidence about the Death, such as: Condition in an administrative claim,
    status of enrollment into a health plan, or explicit record in EHR data.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DEATH
    """

    __tablename__ = "death"
    __table_args__ = (
        ForeignKeyConstraint(
            ["cause_concept_id"],
            ["concept.concept_id"],
            name="fpk_death_cause_concept_id",
        ),
        ForeignKeyConstraint(
            ["cause_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_death_cause_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["death_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_death_death_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_death_person_id"
        ),
        PrimaryKeyConstraint("person_id", "death_date", name="eh_composite_pk_death"),
        Index("idx_death_person_id_1", "person_id"),
    )
    person_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    death_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    death_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    death_type_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    cause_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    cause_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    cause_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    cause_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[cause_concept_id]
    )
    cause_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[cause_source_concept_id]
    )
    death_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[death_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")


class DoseEra(OMOPCDMModelBase):
    """
    A Dose Era is defined as a span of time when the Person is assumed to be
    exposed to a constant dose of a specific active ingredient.

    ETL Conventions

    Dose Eras will be derived from records in the DRUG_EXPOSURE table and the
    Dose information from the DRUG_STRENGTH table using a standardized
    algorithm. Dose Form information is not taken into account. So, if the
    patient changes between different formulations, or different manufacturers
    with the same formulation, the Dose Era is still spanning the entire time
    of exposure to the Ingredient.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DOSE_ERA
    """

    __tablename__ = "dose_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"],
            ["concept.concept_id"],
            name="fpk_dose_era_drug_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_dose_era_person_id"
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_dose_era_unit_concept_id",
        ),
        PrimaryKeyConstraint("dose_era_id", name="xpk_dose_era"),
        Index("idx_dose_era_concept_id_1", "drug_concept_id"),
        Index("idx_dose_era_person_id_1", "person_id"),
    )
    dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    unit_concept_id: Mapped[int] = mapped_column(Integer)
    dose_value: Mapped[decimal.Decimal] = mapped_column(Numeric)
    dose_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    dose_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )


class DrugEra(OMOPCDMModelBase):
    """
    A Drug Era is defined as a span of time when the Person is assumed to be
    exposed to a particular active ingredient. A Drug Era is not the same as a
    Drug Exposure: Exposures are individual records corresponding to the source
    when Drug was delivered to the Person, while successive periods of Drug
    Exposures are combined under certain rules to produce continuous Drug Eras.

    ETL Conventions

    The SQL script for generating DRUG_ERA records can be found here.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DRUG_ERA
    """

    __tablename__ = "drug_era"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_era_drug_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_drug_era_person_id"
        ),
        PrimaryKeyConstraint("drug_era_id", name="xpk_drug_era"),
        Index("idx_drug_era_concept_id_1", "drug_concept_id"),
        Index("idx_drug_era_person_id_1", "person_id"),
    )
    drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    drug_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    drug_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_exposure_count: Mapped[Optional[int]] = mapped_column(Integer)
    gap_days: Mapped[Optional[int]] = mapped_column(Integer)
    drug_concept: Mapped["Concept"] = relationship("Concept")
    person: Mapped["Person"] = relationship("Person")


class Episode(OMOPCDMModelBase):
    """
    The EPISODE table aggregates lower-level clinical events (VISIT_OCCURRENCE,
    DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, DEVICE_EXPOSURE) into a higher-level
    abstraction representing clinically and analytically relevant disease
    phases,outcomes and treatments. The EPISODE_EVENT table connects qualifying
    clinical events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE,
    DEVICE_EXPOSURE) to the appropriate EPISODE entry. For example cancers
    including their development over time, their treatment, and final
    resolution.

    User Guide

    Valid Episode Concepts belong to the 'Episode' domain. For cancer episodes
    please see [article], for non-cancer episodes please see [article]. If your
    source data does not have all episodes that are relevant to the therapeutic
    area, write only those you can easily derive from the data. It is
    understood that that table is not currently expected to be comprehensive.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#EPISODE
    """

    __tablename__ = "episode"
    __table_args__ = (
        ForeignKeyConstraint(
            ["episode_concept_id"],
            ["concept.concept_id"],
            name="fpk_episode_episode_concept_id",
        ),
        ForeignKeyConstraint(
            ["episode_object_concept_id"],
            ["concept.concept_id"],
            name="fpk_episode_episode_object_concept_id",
        ),
        ForeignKeyConstraint(
            ["episode_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_episode_episode_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["episode_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_episode_episode_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_episode_person_id"
        ),
        PrimaryKeyConstraint("episode_id", name="xpk_episode"),
    )
    episode_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    episode_concept_id: Mapped[int] = mapped_column(Integer)
    episode_start_date: Mapped[datetime.date] = mapped_column(Date)
    episode_object_concept_id: Mapped[int] = mapped_column(Integer)
    episode_type_concept_id: Mapped[int] = mapped_column(Integer)
    episode_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    episode_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    episode_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    episode_parent_id: Mapped[Optional[int]] = mapped_column(Integer)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer)
    episode_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    episode_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    episode_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[episode_concept_id]
    )
    episode_object_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[episode_object_concept_id]
    )
    episode_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[episode_source_concept_id]
    )
    episode_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[episode_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")


class ObservationPeriod(OMOPCDMModelBase):
    """
    This table contains records which define spans of time during which two
    conditions are expected to hold: (i) Clinical Events that happened to the
    Person are recorded in the Event tables, and (ii) absense of records
    indicate such Events did not occur during this span of time.

    User Guide

    For each Person, one or more OBSERVATION_PERIOD records may be present, but
    they will not overlap or be back to back to each other. Events may exist
    outside all of the time spans of the OBSERVATION_PERIOD records for a
    patient, however, absence of an Event outside these time spans cannot be
    construed as evidence of absence of an Event. Incidence or prevalence rates
    should only be calculated for the time of active OBSERVATION_PERIOD
    records. When constructing cohorts, outside Events can be used for
    inclusion criteria definition, but without any guarantee for the
    performance of these criteria. Also, OBSERVATION_PERIOD records can be as
    short as a single day, greatly disturbing the denominator of any rate
    calculation as part of cohort characterizations. To avoid that, apply
    minimal observation time as a requirement for any cohort definition.

    ETL Conventions

    Each Person needs to have at least one OBSERVATION_PERIOD record, which
    should represent time intervals with a high capture rate of Clinical
    Events. Some source data have very similar concepts, such as enrollment
    periods in insurance claims data. In other source data such as most EHR
    systems these time spans need to be inferred under a set of assumptions. It
    is the discretion of the ETL developer to define these assumptions. In many
    ETL solutions the start date of the first occurrence or the first high
    quality occurrence of a Clinical Event (Condition, Drug, Procedure, Device,
    Measurement, Visit) is defined as the start of the OBSERVATION_PERIOD
    record, and the end date of the last occurrence of last high quality
    occurrence of a Clinical Event, or the end of the database period becomes
    the end of the OBSERVATOIN_PERIOD for each Person. If a Person only has a
    single Clinical Event the OBSERVATION_PERIOD record can be as short as one
    day. Depending on these definitions it is possible that Clinical Events
    fall outside the time spans defined by OBSERVATION_PERIOD records. Family
    history or history of Clinical Events generally are not used to generate
    OBSERVATION_PERIOD records around the time they are referring to. Any two
    overlapping or adjacent OBSERVATION_PERIOD records have to be merged into
    one.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#OBSERVATION_PERIOD
    """

    __tablename__ = "observation_period"
    __table_args__ = (
        ForeignKeyConstraint(
            ["period_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_period_period_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_observation_period_person_id"
        ),
        PrimaryKeyConstraint("observation_period_id", name="xpk_observation_period"),
        Index("idx_observation_period_id_1", "person_id"),
    )
    observation_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    observation_period_start_date: Mapped[datetime.date] = mapped_column(Date)
    observation_period_end_date: Mapped[datetime.date] = mapped_column(Date)
    period_type_concept_id: Mapped[int] = mapped_column(Integer)
    period_type_concept: Mapped["Concept"] = relationship("Concept")
    person: Mapped["Person"] = relationship("Person")


class PayerPlanPeriod(OMOPCDMModelBase):
    """
    The PAYER_PLAN_PERIOD table captures details of the period of time that a
    Person is continuously enrolled under a specific health Plan benefit
    structure from a given Payer. Each Person receiving healthcare is typically
    covered by a health benefit plan, which pays for (fully or partially), or
    directly provides, the care. These benefit plans are provided by payers,
    such as health insurances or state or government agencies. In each plan the
    details of the health benefits are defined for the Person or her family,
    and the health benefit Plan might change over time typically with
    increasing utilization (reaching certain cost thresholds such as
    deductibles), plan availability and purchasing choices of the Person. The
    unique combinations of Payer organizations, health benefit Plans and time
    periods in which they are valid for a Person are recorded in this table.

    User Guide

    A Person can have multiple, overlapping, Payer_Plan_Periods in this table.
    For example, medical and drug coverage in the US can be represented by two
    Payer_Plan_Periods. The details of the benefit structure of the Plan is
    rarely known, the idea is just to identify that the Plans are different.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#PAYER_PLAN_PERIOD
    """

    __tablename__ = "payer_plan_period"
    __table_args__ = (
        ForeignKeyConstraint(
            ["payer_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_payer_concept_id",
        ),
        ForeignKeyConstraint(
            ["payer_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_payer_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_payer_plan_period_person_id"
        ),
        ForeignKeyConstraint(
            ["plan_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_plan_concept_id",
        ),
        ForeignKeyConstraint(
            ["plan_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_plan_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["sponsor_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_sponsor_concept_id",
        ),
        ForeignKeyConstraint(
            ["sponsor_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_sponsor_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["stop_reason_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_stop_reason_concept_id",
        ),
        ForeignKeyConstraint(
            ["stop_reason_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_payer_plan_period_stop_reason_source_concept_id",
        ),
        PrimaryKeyConstraint("payer_plan_period_id", name="xpk_payer_plan_period"),
        Index("idx_period_person_id_1", "person_id"),
    )
    payer_plan_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    payer_plan_period_start_date: Mapped[datetime.date] = mapped_column(Date)
    payer_plan_period_end_date: Mapped[datetime.date] = mapped_column(Date)
    payer_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    payer_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    payer_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    plan_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    plan_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    plan_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    sponsor_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    sponsor_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    sponsor_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    family_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    stop_reason_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    stop_reason_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    stop_reason_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    payer_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[payer_concept_id]
    )
    payer_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[payer_source_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    plan_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[plan_concept_id]
    )
    plan_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[plan_source_concept_id]
    )
    sponsor_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[sponsor_concept_id]
    )
    sponsor_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[sponsor_source_concept_id]
    )
    stop_reason_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[stop_reason_concept_id]
    )
    stop_reason_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[stop_reason_source_concept_id]
    )


class Specimen(OMOPCDMModelBase):
    """
    The specimen domain contains the records identifying biological samples
    from a person.

    ETL Conventions

    Anatomic site is coded at the most specific level of granularity possible,
    such that higher level classifications can be derived using the
    Standardized Vocabularies.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#SPECIMEN
    """

    __tablename__ = "specimen"
    __table_args__ = (
        ForeignKeyConstraint(
            ["anatomic_site_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_anatomic_site_concept_id",
        ),
        ForeignKeyConstraint(
            ["disease_status_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_disease_status_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_specimen_person_id"
        ),
        ForeignKeyConstraint(
            ["specimen_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_specimen_concept_id",
        ),
        ForeignKeyConstraint(
            ["specimen_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_specimen_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_specimen_unit_concept_id",
        ),
        PrimaryKeyConstraint("specimen_id", name="xpk_specimen"),
        Index("idx_specimen_concept_id_1", "specimen_concept_id"),
        Index("idx_specimen_person_id_1", "person_id"),
    )
    specimen_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    specimen_concept_id: Mapped[int] = mapped_column(Integer)
    specimen_type_concept_id: Mapped[int] = mapped_column(Integer)
    specimen_date: Mapped[datetime.date] = mapped_column(Date)
    specimen_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    anatomic_site_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    disease_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    specimen_source_id: Mapped[Optional[str]] = mapped_column(String(50))
    specimen_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    anatomic_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    disease_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    anatomic_site_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[anatomic_site_concept_id]
    )
    disease_status_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[disease_status_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    specimen_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specimen_concept_id]
    )
    specimen_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[specimen_type_concept_id]
    )
    unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )


class VisitOccurrence(OMOPCDMModelBase):
    """
    This table contains Events where Persons engage with the healthcare system
    for a duration of time. They are often also called "Encounters". Visits are
    defined by a configuration of circumstances under which they occur, such as
    (i) whether the patient comes to a healthcare institution, the other way
    around, or the interaction is remote, (ii) whether and what kind of trained
    medical staff is delivering the service during the Visit, and (iii) whether
    the Visit is transient or for a longer period involving a stay in bed.

    User Guide

    The configuration defining the Visit are described by Concepts in the Visit
    Domain, which form a hierarchical structure, but rolling up to generally
    familiar Visits adopted in most healthcare systems worldwide:

    The Visit duration, or 'length of stay', is defined as VISIT_END_DATE -
    VISIT_START_DATE. For all Visits this is <1 day, except Inpatient Visits
    and Non-hospital institution Visits. The CDM also contains the VISIT_DETAIL
    table where additional information about the Visit is stored, for example,
    transfers between units during an inpatient Visit.

    ETL Conventions

    Visits can be derived easily if the source data contain coding systems for
    Place of Service or Procedures, like CPT codes for well visits. In those
    cases, the codes can be looked up and mapped to a Standard Visit Concept.
    Otherwise, Visit Concepts have to be identified in the ETL process. This
    table will contain concepts in the Visit domain. These concepts are
    arranged in a hierarchical structure to facilitate cohort definitions by
    rolling up to generally familiar Visits adopted in most healthcare systems
    worldwide. Visits can be adjacent to each other, i.e. the end date of one
    can be identical with the start date of the other. As a consequence, more
    than one-day Visits or their descendants can be recorded for the same day.
    Multi-day visits must not overlap, i.e. share days other than start and end
    days. It is often the case that some logic should be written for how to
    define visits and how to assign Visit_Concept_Id. For example, in US claims
    outpatient visits that appear to occur within the time period of an
    inpatient visit can be rolled into one with the same Visit_Occurrence_Id.
    In EHR data inpatient visits that are within one day of each other may be
    strung together to create one visit. It will all depend on the source data
    and how encounter records should be translated to visit occurrences.
    Providers can be associated with a Visit through the PROVIDER_ID field, or
    indirectly through PROCEDURE_OCCURRENCE records linked both to the VISIT
    and PROVIDER tables.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#VISIT_OCCURRENCE
    """

    __tablename__ = "visit_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["admitted_from_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_admitted_from_concept_id",
        ),
        ForeignKeyConstraint(
            ["care_site_id"],
            ["care_site.care_site_id"],
            name="fpk_visit_occurrence_care_site_id",
        ),
        ForeignKeyConstraint(
            ["discharged_to_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_discharged_to_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_visit_occurrence_person_id"
        ),
        ForeignKeyConstraint(
            ["preceding_visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_visit_occurrence_preceding_visit_occurrence_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_visit_occurrence_provider_id",
        ),
        ForeignKeyConstraint(
            ["visit_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_occurrence_visit_type_concept_id",
        ),
        PrimaryKeyConstraint("visit_occurrence_id", name="xpk_visit_occurrence"),
        Index("idx_visit_concept_id_1", "visit_concept_id"),
        Index("idx_visit_person_id_1", "person_id"),
    )
    visit_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    visit_concept_id: Mapped[int] = mapped_column(Integer)
    visit_start_date: Mapped[datetime.date] = mapped_column(Date)
    visit_end_date: Mapped[datetime.date] = mapped_column(Date)
    visit_type_concept_id: Mapped[int] = mapped_column(Integer)
    visit_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    visit_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    visit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    preceding_visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[admitted_from_concept_id]
    )
    care_site: Mapped["CareSite"] = relationship("CareSite")
    discharged_to_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[discharged_to_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    preceding_visit_occurrence: Mapped["VisitOccurrence"] = relationship(
        "VisitOccurrence", remote_side=[visit_occurrence_id]
    )
    provider: Mapped["Provider"] = relationship("Provider")
    visit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_concept_id]
    )
    visit_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_source_concept_id]
    )
    visit_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_type_concept_id]
    )


class EpisodeEvent(OMOPCDMModelBase):
    """
    The EPISODE_EVENT table connects qualifying clinical events (such as
    CONDITION_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, MEASUREMENT) to
    the appropriate EPISODE entry. For example, linking the precise location of
    the metastasis (cancer modifier in MEASUREMENT) to the disease episode.

    User Guide

    This connecting table is used instead of the FACT_RELATIONSHIP table for
    linking low-level events to abstracted Episodes.

    ETL Conventions

    Some episodes may not have links to any underlying clinical events. For
    such episodes, the EPISODE_EVENT table is not populated.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#EPISODE_EVENT
    """

    __tablename__ = "episode_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["episode_event_field_concept_id"],
            ["concept.concept_id"],
            name="fpk_episode_event_episode_event_field_concept_id",
        ),
        ForeignKeyConstraint(
            ["episode_id"], ["episode.episode_id"], name="fpk_episode_event_episode_id"
        ),
        PrimaryKeyConstraint(
            "episode_id",
            "event_id",
            "episode_event_field_concept_id",
            name="eh_composite_pk_episode_event",
        ),
    )
    episode_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    episode_event_field_concept_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )
    episode_event_field_concept: Mapped["Concept"] = relationship("Concept")
    episode: Mapped["Episode"] = relationship("Episode")


class VisitDetail(OMOPCDMModelBase):
    """
    The VISIT_DETAIL table is an optional table used to represents details of
    each record in the parent VISIT_OCCURRENCE table. A good example of this
    would be the movement between units in a hospital during an inpatient stay
    or claim lines associated with a one insurance claim. For every record in
    the VISIT_OCCURRENCE table there may be 0 or more records in the
    VISIT_DETAIL table with a 1:n relationship where n may be 0. The
    VISIT_DETAIL table is structurally very similar to VISIT_OCCURRENCE table
    and belongs to the visit domain.

    User Guide

    The configuration defining the Visit Detail is described by Concepts in the
    Visit Domain, which form a hierarchical structure. The Visit Detail record
    will have an associated to the Visit Occurrence record in two ways:  1. The
    Visit Detail record will have the VISIT_OCCURRENCE_ID it is associated to
    2. The VISIT_DETAIL_CONCEPT_ID will be a descendant of the VISIT_CONCEPT_ID
    for the Visit.

    ETL Conventions

    It is not mandatory that the VISIT_DETAIL table be filled in, but if you
    find that the logic to create VISIT_OCCURRENCE records includes the roll-up
    of multiple smaller records to create one picture of a Visit then it is a
    good idea to use VISIT_DETAIL. In EHR data, for example, a Person may be in
    the hospital but instead of one over-arching Visit their encounters are
    recorded as times they interacted with a health care provider. A Person in
    the hospital interacts with multiple providers multiple times a day so the
    encounters must be strung together using some heuristic (defined by the
    ETL) to identify the entire Visit. In this case the encounters would be
    considered Visit Details and the entire Visit would be the Visit
    Occurrence. In this example it is also possible to use the Vocabulary to
    distinguish Visit Details from a Visit Occurrence by setting the
    VISIT_CONCEPT_ID to 9201 and the VISIT_DETAIL_CONCEPT_IDs either to 9201 or
    its children to indicate where the patient was in the hospital at the time
    of care.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#VISIT_DETAIL
    """

    __tablename__ = "visit_detail"
    __table_args__ = (
        ForeignKeyConstraint(
            ["admitted_from_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_admitted_from_concept_id",
        ),
        ForeignKeyConstraint(
            ["care_site_id"],
            ["care_site.care_site_id"],
            name="fpk_visit_detail_care_site_id",
        ),
        ForeignKeyConstraint(
            ["discharged_to_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_discharged_to_concept_id",
        ),
        ForeignKeyConstraint(
            ["parent_visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_visit_detail_parent_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_visit_detail_person_id"
        ),
        ForeignKeyConstraint(
            ["preceding_visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_visit_detail_preceding_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_visit_detail_provider_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_visit_detail_visit_detail_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_visit_detail_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("visit_detail_id", name="xpk_visit_detail"),
        Index("idx_visit_det_concept_id_1", "visit_detail_concept_id"),
        Index("idx_visit_det_occ_id", "visit_occurrence_id"),
        Index("idx_visit_det_person_id_1", "person_id"),
    )
    visit_detail_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    visit_detail_concept_id: Mapped[int] = mapped_column(Integer)
    visit_detail_start_date: Mapped[datetime.date] = mapped_column(Date)
    visit_detail_end_date: Mapped[datetime.date] = mapped_column(Date)
    visit_detail_type_concept_id: Mapped[int] = mapped_column(Integer)
    visit_occurrence_id: Mapped[int] = mapped_column(Integer)
    visit_detail_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    visit_detail_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    visit_detail_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    discharged_to_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    discharged_to_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    preceding_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    parent_visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    admitted_from_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[admitted_from_concept_id]
    )
    care_site: Mapped["CareSite"] = relationship("CareSite")
    discharged_to_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[discharged_to_concept_id]
    )
    parent_visit_detail: Mapped["VisitDetail"] = relationship(
        "VisitDetail",
        remote_side=[visit_detail_id],
        foreign_keys=[parent_visit_detail_id],
    )
    person: Mapped["Person"] = relationship("Person")
    preceding_visit_detail: Mapped["VisitDetail"] = relationship(
        "VisitDetail",
        remote_side=[visit_detail_id],
        foreign_keys=[preceding_visit_detail_id],
    )
    provider: Mapped["Provider"] = relationship("Provider")
    visit_detail_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_detail_concept_id]
    )
    visit_detail_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_detail_source_concept_id]
    )
    visit_detail_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[visit_detail_type_concept_id]
    )
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class ConditionOccurrence(OMOPCDMModelBase):
    """
    This table contains records of Events of a Person suggesting the presence
    of a disease or medical condition stated as a diagnosis, a sign, or a
    symptom, which is either observed by a Provider or reported by the patient.

    User Guide

    Conditions are defined by Concepts from the Condition domain, which form a
    complex hierarchy. As a result, the same Person with the same disease may
    have multiple Condition records, which belong to the same hierarchical
    family. Most Condition records are mapped from diagnostic codes, but
    recorded signs, symptoms and summary descriptions also contribute to this
    table. Rule out diagnoses should not be recorded in this table, but in
    reality their negating nature is not always captured in the source data,
    and other precautions must be taken when when identifying Persons who
    should suffer from the recorded Condition. Record all conditions as they
    exist in the source data. Any decisions about diagnosis/phenotype
    definitions would be done through cohort specifications. These cohorts can
    be housed in the COHORT table. Conditions span a time interval from start
    to end, but are typically recorded as single snapshot records with no end
    date. The reason is twofold: (i) At the time of the recording the duration
    is not known and later not recorded, and (ii) the Persons typically cease
    interacting with the healthcare system when they feel better, which leads
    to incomplete capture of resolved Conditions. The CONDITION_ERA table
    addresses this issue. Family history and past diagnoses ('history of') are
    not recorded in this table. Instead, they are listed in the OBSERVATION
    table. Codes written in the process of establishing the diagnosis, such as
    'question of' of and 'rule out', should not represented here. Instead, they
    should be recorded in the OBSERVATION table, if they are used for analyses.
    However, this information is not always available.

    ETL Conventions

    Source codes and source text fields mapped to Standard Concepts of the
    Condition Domain have to be recorded here.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#CONDITION_OCCURRENCE
    """

    __tablename__ = "condition_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["condition_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_status_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_status_concept_id",
        ),
        ForeignKeyConstraint(
            ["condition_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_condition_occurrence_condition_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"],
            ["person.person_id"],
            name="fpk_condition_occurrence_person_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_condition_occurrence_provider_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_condition_occurrence_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_condition_occurrence_visit_occurrence_id",
        ),
        PrimaryKeyConstraint(
            "condition_occurrence_id", name="xpk_condition_occurrence"
        ),
        Index("idx_condition_concept_id_1", "condition_concept_id"),
        Index("idx_condition_person_id_1", "person_id"),
        Index("idx_condition_visit_id_1", "visit_occurrence_id"),
    )
    condition_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer)
    condition_start_date: Mapped[datetime.date] = mapped_column(Date)
    condition_type_concept_id: Mapped[int] = mapped_column(Integer)
    condition_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    condition_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    condition_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    condition_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    stop_reason: Mapped[Optional[str]] = mapped_column(String(20))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    condition_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    condition_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    condition_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    condition_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_concept_id]
    )
    condition_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_source_concept_id]
    )
    condition_status_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_status_concept_id]
    )
    condition_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[condition_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class DeviceExposure(OMOPCDMModelBase):
    """
    The Device domain captures information about a person's exposure to a
    foreign physical object or instrument which is used for diagnostic or
    therapeutic purposes through a mechanism beyond chemical action. Devices
    include implantable objects (e.g. pacemakers, stents, artificial joints),
    medical equipment and supplies (e.g. bandages, crutches, syringes), other
    instruments used in medical procedures (e.g. sutures, defibrillators) and
    material used in clinical care (e.g. adhesives, body material, dental
    material, surgical material).

    User Guide

    The distinction between Devices or supplies and Procedures are sometimes
    blurry, but the former are physical objects while the latter are actions,
    often to apply a Device or supply.

    ETL Conventions

    Source codes and source text fields mapped to Standard Concepts of the
    Device Domain have to be recorded here.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DEVICE_EXPOSURE
    """

    __tablename__ = "device_exposure"
    __table_args__ = (
        ForeignKeyConstraint(
            ["device_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_concept_id",
        ),
        ForeignKeyConstraint(
            ["device_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["device_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_device_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_device_exposure_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_device_exposure_provider_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_device_exposure_unit_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_device_exposure_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_device_exposure_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("device_exposure_id", name="xpk_device_exposure"),
        Index("idx_device_concept_id_1", "device_concept_id"),
        Index("idx_device_person_id_1", "person_id"),
        Index("idx_device_visit_id_1", "visit_occurrence_id"),
    )
    device_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    device_concept_id: Mapped[int] = mapped_column(Integer)
    device_exposure_start_date: Mapped[datetime.date] = mapped_column(Date)
    device_type_concept_id: Mapped[int] = mapped_column(Integer)
    device_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    device_exposure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    device_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    unique_device_id: Mapped[Optional[str]] = mapped_column(String(255))
    production_id: Mapped[Optional[str]] = mapped_column(String(255))
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    device_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    device_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    device_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[device_concept_id]
    )
    device_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[device_source_concept_id]
    )
    device_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[device_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )
    unit_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_source_concept_id]
    )
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class DrugExposure(OMOPCDMModelBase):
    """
    This table captures records about the exposure to a Drug ingested or
    otherwise introduced into the body. A Drug is a biochemical substance
    formulated in such a way that when administered to a Person it will exert a
    certain biochemical effect on the metabolism. Drugs include prescription
    and over-the-counter medicines, vaccines, and large-molecule biologic
    therapies. Radiological devices ingested or applied locally do not count as
    Drugs.

    User Guide

    The purpose of records in this table is to indicate an exposure to a
    certain drug as best as possible. In this context a drug is defined as an
    active ingredient. Drug Exposures are defined by Concepts from the Drug
    domain, which form a complex hierarchy. As a result, one
    DRUG_SOURCE_CONCEPT_ID may map to multiple standard concept ids if it is a
    combination product. Records in this table represent prescriptions written,
    prescriptions dispensed, and drugs administered by a provider to name a
    few. The DRUG_TYPE_CONCEPT_ID can be used to find and filter on these
    types. This table includes additional information about the drug products,
    the quantity given, and route of administration.

    ETL Conventions

    Information about quantity and dose is provided in a variety of different
    ways and it is important for the ETL to provide as much information as
    possible from the data. Depending on the provenance of the data fields may
    be captured differently i.e. quantity for drugs administered may have a
    separate meaning from quantity for prescriptions dispensed. If a patient
    has multiple records on the same day for the same drug or procedures the
    ETL should not de-dupe them unless there is probable reason to believe the
    item is a true data duplicate. Take note on how to handle refills for
    prescriptions written.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#DRUG_EXPOSURE
    """

    __tablename__ = "drug_exposure"
    __table_args__ = (
        ForeignKeyConstraint(
            ["drug_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_drug_concept_id",
        ),
        ForeignKeyConstraint(
            ["drug_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_drug_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["drug_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_drug_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_drug_exposure_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_drug_exposure_provider_id",
        ),
        ForeignKeyConstraint(
            ["route_concept_id"],
            ["concept.concept_id"],
            name="fpk_drug_exposure_route_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_drug_exposure_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_drug_exposure_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("drug_exposure_id", name="xpk_drug_exposure"),
        Index("idx_drug_concept_id_1", "drug_concept_id"),
        Index("idx_drug_person_id_1", "person_id"),
        Index("idx_drug_visit_id_1", "visit_occurrence_id"),
    )
    drug_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    drug_exposure_start_date: Mapped[datetime.date] = mapped_column(Date)
    drug_exposure_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_type_concept_id: Mapped[int] = mapped_column(Integer)
    drug_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    drug_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    verbatim_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    stop_reason: Mapped[Optional[str]] = mapped_column(String(20))
    refills: Mapped[Optional[int]] = mapped_column(Integer)
    quantity: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    days_supply: Mapped[Optional[int]] = mapped_column(Integer)
    sig: Mapped[Optional[str]] = mapped_column(Text)
    route_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    lot_number: Mapped[Optional[str]] = mapped_column(String(50))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    drug_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    drug_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    route_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    dose_unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    drug_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_concept_id]
    )
    drug_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_source_concept_id]
    )
    drug_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[drug_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    route_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[route_concept_id]
    )
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class Measurement(OMOPCDMModelBase):
    """
    The MEASUREMENT table contains records of Measurements, i.e. structured
    values (numerical or categorical) obtained through systematic and
    standardized examination or testing of a Person or Person's sample. The
    MEASUREMENT table contains both orders and results of such Measurements as
    laboratory tests, vital signs, quantitative findings from pathology
    reports, etc. Measurements are stored as attribute value pairs, with the
    attribute as the Measurement Concept and the value representing the result.
    The value can be a Concept (stored in VALUE_AS_CONCEPT), or a numerical
    value (VALUE_AS_NUMBER) with a Unit (UNIT_CONCEPT_ID). The Procedure for
    obtaining the sample is housed in the PROCEDURE_OCCURRENCE table, though it
    is unnecessary to create a PROCEDURE_OCCURRENCE record for each measurement
    if one does not exist in the source data. Measurements differ from
    Observations in that they require a standardized test or some other
    activity to generate a quantitative or qualitative result. If there is no
    result, it is assumed that the lab test was conducted but the result was
    not captured.

    User Guide

    Measurements are predominately lab tests with a few exceptions, like blood
    pressure or function tests. Results are given in the form of a value and
    unit combination. When investigating measurements, look for
    operator_concept_ids (<, >, etc.).

    ETL Conventions

    Only records where the source value maps to a Concept in the measurement
    domain should be included in this table. Even though each Measurement
    always has a result, the fields VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are
    not mandatory as often the result is not given in the source data. When the
    result is not known, the Measurement record represents just the fact that
    the corresponding Measurement was carried out, which in itself is already
    useful information for some use cases. For some Measurement Concepts, the
    result is included in the test. For example, ICD10 CONCEPT_ID 45548980
    'Abnormal level of unspecified serum enzyme' indicates a Measurement and
    the result (abnormal). In those situations, the CONCEPT_RELATIONSHIP table
    in addition to the 'Maps to' record contains a second record with the
    relationship_id set to 'Maps to value'. In this example, the 'Maps to'
    relationship directs to 4046263 'Enzyme measurement' as well as a 'Maps to
    value' record to 4135493 'Abnormal'.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#MEASUREMENT
    """

    __tablename__ = "measurement"
    __table_args__ = (
        ForeignKeyConstraint(
            ["meas_event_field_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_meas_event_field_concept_id",
        ),
        ForeignKeyConstraint(
            ["measurement_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_concept_id",
        ),
        ForeignKeyConstraint(
            ["measurement_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["measurement_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_measurement_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["operator_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_operator_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_measurement_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_measurement_provider_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_unit_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"],
            ["concept.concept_id"],
            name="fpk_measurement_value_as_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_measurement_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_measurement_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("measurement_id", name="xpk_measurement"),
        Index("idx_measurement_concept_id_1", "measurement_concept_id"),
        Index("idx_measurement_person_id_1", "person_id"),
        Index("idx_measurement_visit_id_1", "visit_occurrence_id"),
    )
    measurement_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    measurement_concept_id: Mapped[int] = mapped_column(Integer)
    measurement_date: Mapped[datetime.date] = mapped_column(Date)
    measurement_type_concept_id: Mapped[int] = mapped_column(Integer)
    measurement_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    measurement_time: Mapped[Optional[str]] = mapped_column(String(10))
    operator_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    range_low: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    range_high: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    measurement_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    measurement_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    unit_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    value_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    measurement_event_id: Mapped[Optional[int]] = mapped_column(Integer)
    meas_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    meas_event_field_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[meas_event_field_concept_id]
    )
    measurement_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[measurement_concept_id]
    )
    measurement_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[measurement_source_concept_id]
    )
    measurement_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[measurement_type_concept_id]
    )
    operator_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[operator_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )
    unit_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_source_concept_id]
    )
    value_as_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class Note(OMOPCDMModelBase):
    """
    The NOTE table captures unstructured information that was recorded by a
    provider about a patient in free text (in ASCII, or preferably in UTF8
    format) notes on a given date. The type of note_text is CLOB or
    varchar(MAX) depending on RDBMS.

    ETL Conventions

    HL7/LOINC CDO is a standard for consistent naming of documents to support a
    range of use cases: retrieval, organization, display, and exchange. It
    guides the creation of LOINC codes for clinical notes. CDO annotates each
    document with 5 dimensions:

    According to CDO requirements, only 2 of the 5 dimensions are required to
    properly annotate a document; Kind of Document and any one of the other 4
    dimensions. However, not all the permutations of the CDO dimensions will
    necessarily yield an existing LOINC code. Each of these dimensions are
    contained in the OMOP Vocabulary under the domain of 'Meas Value' with each
    dimension represented as a Concept Class.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#NOTE
    """

    __tablename__ = "note"
    __table_args__ = (
        ForeignKeyConstraint(
            ["encoding_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_encoding_concept_id",
        ),
        ForeignKeyConstraint(
            ["language_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_language_concept_id",
        ),
        ForeignKeyConstraint(
            ["note_class_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_note_class_concept_id",
        ),
        ForeignKeyConstraint(
            ["note_event_field_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_note_event_field_concept_id",
        ),
        ForeignKeyConstraint(
            ["note_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_note_note_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_note_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"], ["provider.provider_id"], name="fpk_note_provider_id"
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_note_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_note_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("note_id", name="xpk_note"),
        Index("idx_note_concept_id_1", "note_type_concept_id"),
        Index("idx_note_person_id_1", "person_id"),
        Index("idx_note_visit_id_1", "visit_occurrence_id"),
    )
    note_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    note_date: Mapped[datetime.date] = mapped_column(Date)
    note_type_concept_id: Mapped[int] = mapped_column(Integer)
    note_class_concept_id: Mapped[int] = mapped_column(Integer)
    note_text: Mapped[str] = mapped_column(Text)
    encoding_concept_id: Mapped[int] = mapped_column(Integer)
    language_concept_id: Mapped[int] = mapped_column(Integer)
    note_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    note_title: Mapped[Optional[str]] = mapped_column(String(250))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    note_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    note_event_id: Mapped[Optional[int]] = mapped_column(Integer)
    note_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    encoding_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[encoding_concept_id]
    )
    language_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[language_concept_id]
    )
    note_class_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_class_concept_id]
    )
    note_event_field_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_event_field_concept_id]
    )
    note_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[note_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class Observation(OMOPCDMModelBase):
    """
    The OBSERVATION table captures clinical facts about a Person obtained in
    the context of examination, questioning or a procedure. Any data that
    cannot be represented by any other domains, such as social and lifestyle
    facts, medical history, family history, etc. are recorded here.

    User Guide

    Observations differ from Measurements in that they do not require a
    standardized test or some other activity to generate clinical fact. Typical
    observations are medical history, family history, the stated need for
    certain treatment, social circumstances, lifestyle choices, healthcare
    utilization patterns, etc. If the generation clinical facts requires a
    standardized testing such as lab testing or imaging and leads to a
    standardized result, the data item is recorded in the MEASUREMENT table. If
    the clinical fact observed determines a sign, symptom, diagnosis of a
    disease or other medical condition, it is recorded in the
    CONDITION_OCCURRENCE table. Valid Observation Concepts are not enforced to
    be from any domain though they still should be Standard Concepts.

    ETL Conventions

    Records whose Source Values map to any domain besides Condition, Procedure,
    Drug, Measurement or Device should be stored in the Observation table.
    Observations can be stored as attribute value pairs, with the attribute as
    the Observation Concept and the value representing the clinical fact. This
    fact can be a Concept (stored in VALUE_AS_CONCEPT), a numerical value
    (VALUE_AS_NUMBER), a verbatim string (VALUE_AS_STRING), or a datetime
    (VALUE_AS_DATETIME). Even though Observations do not have an explicit
    result, the clinical fact can be stated separately from the type of
    Observation in the VALUE_AS_* fields. It is recommended for Observations
    that are suggestive statements of positive assertion should have a value of
    'Yes' (concept_id=4188539), recorded, even though the null value is the
    equivalent.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#OBSERVATION
    """

    __tablename__ = "observation"
    __table_args__ = (
        ForeignKeyConstraint(
            ["obs_event_field_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_obs_event_field_concept_id",
        ),
        ForeignKeyConstraint(
            ["observation_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_concept_id",
        ),
        ForeignKeyConstraint(
            ["observation_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["observation_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_observation_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"], ["person.person_id"], name="fpk_observation_person_id"
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_observation_provider_id",
        ),
        ForeignKeyConstraint(
            ["qualifier_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_qualifier_concept_id",
        ),
        ForeignKeyConstraint(
            ["unit_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_unit_concept_id",
        ),
        ForeignKeyConstraint(
            ["value_as_concept_id"],
            ["concept.concept_id"],
            name="fpk_observation_value_as_concept_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_observation_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_observation_visit_occurrence_id",
        ),
        PrimaryKeyConstraint("observation_id", name="xpk_observation"),
        Index("idx_observation_concept_id_1", "observation_concept_id"),
        Index("idx_observation_person_id_1", "person_id"),
        Index("idx_observation_visit_id_1", "visit_occurrence_id"),
    )
    observation_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    observation_concept_id: Mapped[int] = mapped_column(Integer)
    observation_date: Mapped[datetime.date] = mapped_column(Date)
    observation_type_concept_id: Mapped[int] = mapped_column(Integer)
    observation_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    value_as_number: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric)
    value_as_string: Mapped[Optional[str]] = mapped_column(String(60))
    value_as_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    qualifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    observation_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    observation_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    qualifier_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    value_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    observation_event_id: Mapped[Optional[int]] = mapped_column(Integer)
    obs_event_field_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    obs_event_field_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[obs_event_field_concept_id]
    )
    observation_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[observation_concept_id]
    )
    observation_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[observation_source_concept_id]
    )
    observation_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[observation_type_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    provider: Mapped["Provider"] = relationship("Provider")
    qualifier_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[qualifier_concept_id]
    )
    unit_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[unit_concept_id]
    )
    value_as_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[value_as_concept_id]
    )
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")


class ProcedureOccurrence(OMOPCDMModelBase):
    """
    This table contains records of activities or processes ordered by, or
    carried out by, a healthcare provider on the patient with a diagnostic or
    therapeutic purpose.

    User Guide

    Lab tests are not a procedure, if something is observed with an expected
    resulting amount and unit then it should be a measurement. Phlebotomy is a
    procedure but so trivial that it tends to be rarely captured. It can be
    assumed that there is a phlebotomy procedure associated with many lab
    tests, therefore it is unnecessary to add them as separate procedures. If
    the user finds the same procedure over concurrent days, it is assumed those
    records are part of a procedure lasting more than a day. This logic is in
    lieu of the procedure_end_date, which will be added in a future version of
    the CDM.

    ETL Conventions

    When dealing with duplicate records, the ETL must determine whether to sum
    them up into one record or keep them separate. Things to consider are: -
    Same Procedure - Same PROCEDURE_DATETIME - Same Visit Occurrence or Visit
    Detail - Same Provider - Same Modifier for Procedures. Source codes and
    source text fields mapped to Standard Concepts of the Procedure Domain have
    to be recorded here.

    https://ohdsi.github.io/CommonDataModel/cdm54.html#PROCEDURE_OCCURRENCE
    """

    __tablename__ = "procedure_occurrence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["modifier_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_modifier_concept_id",
        ),
        ForeignKeyConstraint(
            ["person_id"],
            ["person.person_id"],
            name="fpk_procedure_occurrence_person_id",
        ),
        ForeignKeyConstraint(
            ["procedure_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_procedure_concept_id",
        ),
        ForeignKeyConstraint(
            ["procedure_source_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_procedure_source_concept_id",
        ),
        ForeignKeyConstraint(
            ["procedure_type_concept_id"],
            ["concept.concept_id"],
            name="fpk_procedure_occurrence_procedure_type_concept_id",
        ),
        ForeignKeyConstraint(
            ["provider_id"],
            ["provider.provider_id"],
            name="fpk_procedure_occurrence_provider_id",
        ),
        ForeignKeyConstraint(
            ["visit_detail_id"],
            ["visit_detail.visit_detail_id"],
            name="fpk_procedure_occurrence_visit_detail_id",
        ),
        ForeignKeyConstraint(
            ["visit_occurrence_id"],
            ["visit_occurrence.visit_occurrence_id"],
            name="fpk_procedure_occurrence_visit_occurrence_id",
        ),
        PrimaryKeyConstraint(
            "procedure_occurrence_id", name="xpk_procedure_occurrence"
        ),
        Index("idx_procedure_concept_id_1", "procedure_concept_id"),
        Index("idx_procedure_person_id_1", "person_id"),
        Index("idx_procedure_visit_id_1", "visit_occurrence_id"),
    )
    procedure_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    procedure_concept_id: Mapped[int] = mapped_column(Integer)
    procedure_date: Mapped[datetime.date] = mapped_column(Date)
    procedure_type_concept_id: Mapped[int] = mapped_column(Integer)
    procedure_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    procedure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    procedure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    modifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    procedure_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    procedure_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    modifier_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    modifier_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[modifier_concept_id]
    )
    person: Mapped["Person"] = relationship("Person")
    procedure_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[procedure_concept_id]
    )
    procedure_source_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[procedure_source_concept_id]
    )
    procedure_type_concept: Mapped["Concept"] = relationship(
        "Concept", foreign_keys=[procedure_type_concept_id]
    )
    provider: Mapped["Provider"] = relationship("Provider")
    visit_detail: Mapped["VisitDetail"] = relationship("VisitDetail")
    visit_occurrence: Mapped["VisitOccurrence"] = relationship("VisitOccurrence")
