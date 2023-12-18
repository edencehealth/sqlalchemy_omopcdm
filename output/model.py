from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class Cohort(Base):
    __tablename__ = 'cohort'
    __table_args__ = (
        PrimaryKeyConstraint('cohort_definition_id', 'subject_id', 'cohort_start_date', 'cohort_end_date', name='eh_synth_pk'),
    )

    cohort_definition_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    cohort_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)


class Concept(Base):
    __tablename__ = 'concept'
    __table_args__ = (
        ForeignKeyConstraint(['concept_class_id'], ['concept_class.concept_class_id'], name='fpk_concept_concept_class_id'),
        ForeignKeyConstraint(['domain_id'], ['domain.domain_id'], name='fpk_concept_domain_id'),
        ForeignKeyConstraint(['vocabulary_id'], ['vocabulary.vocabulary_id'], name='fpk_concept_vocabulary_id'),
        PrimaryKeyConstraint('concept_id', name='xpk_concept')
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

    concept_class: Mapped['ConceptClass'] = relationship('ConceptClass', foreign_keys=[concept_class_id])
    domain: Mapped['Domain'] = relationship('Domain', foreign_keys=[domain_id])
    vocabulary: Mapped['Vocabulary'] = relationship('Vocabulary', foreign_keys=[vocabulary_id])


class ConceptClass(Base):
    __tablename__ = 'concept_class'
    __table_args__ = (
        ForeignKeyConstraint(['concept_class_concept_id'], ['concept.concept_id'], name='fpk_concept_class_concept_class_concept_id'),
        PrimaryKeyConstraint('concept_class_id', name='xpk_concept_class')
    )

    concept_class_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    concept_class_name: Mapped[str] = mapped_column(String(255))
    concept_class_concept_id: Mapped[int] = mapped_column(Integer)

    concept_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[concept_class_concept_id])


class Domain(Base):
    __tablename__ = 'domain'
    __table_args__ = (
        ForeignKeyConstraint(['domain_concept_id'], ['concept.concept_id'], name='fpk_domain_domain_concept_id'),
        PrimaryKeyConstraint('domain_id', name='xpk_domain')
    )

    domain_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    domain_name: Mapped[str] = mapped_column(String(255))
    domain_concept_id: Mapped[int] = mapped_column(Integer)

    domain_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[domain_concept_id])


class Vocabulary(Base):
    __tablename__ = 'vocabulary'
    __table_args__ = (
        ForeignKeyConstraint(['vocabulary_concept_id'], ['concept.concept_id'], name='fpk_vocabulary_vocabulary_concept_id'),
        PrimaryKeyConstraint('vocabulary_id', name='xpk_vocabulary')
    )

    vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    vocabulary_name: Mapped[str] = mapped_column(String(255))
    vocabulary_concept_id: Mapped[int] = mapped_column(Integer)
    vocabulary_reference: Mapped[Optional[str]] = mapped_column(String(255))
    vocabulary_version: Mapped[Optional[str]] = mapped_column(String(255))

    vocabulary_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[vocabulary_concept_id])


t_cdm_source = Table(
    'cdm_source', Base.metadata,
    Column('cdm_source_name', String(255), nullable=False),
    Column('cdm_source_abbreviation', String(25), nullable=False),
    Column('cdm_holder', String(255), nullable=False),
    Column('source_description', Text),
    Column('source_documentation_reference', String(255)),
    Column('cdm_etl_reference', String(255)),
    Column('source_release_date', Date, nullable=False),
    Column('cdm_release_date', Date, nullable=False),
    Column('cdm_version', String(10)),
    Column('cdm_version_concept_id', Integer, nullable=False),
    Column('vocabulary_version', String(20), nullable=False),
    ForeignKeyConstraint(['cdm_version_concept_id'], ['concept.concept_id'], name='fpk_cdm_source_cdm_version_concept_id')
)


t_cohort_definition = Table(
    'cohort_definition', Base.metadata,
    Column('cohort_definition_id', Integer, nullable=False),
    Column('cohort_definition_name', String(255), nullable=False),
    Column('cohort_definition_description', Text),
    Column('definition_type_concept_id', Integer, nullable=False),
    Column('cohort_definition_syntax', Text),
    Column('subject_concept_id', Integer, nullable=False),
    Column('cohort_initiation_date', Date),
    ForeignKeyConstraint(['definition_type_concept_id'], ['concept.concept_id'], name='fpk_cohort_definition_definition_type_concept_id'),
    ForeignKeyConstraint(['subject_concept_id'], ['concept.concept_id'], name='fpk_cohort_definition_subject_concept_id')
)


t_concept_ancestor = Table(
    'concept_ancestor', Base.metadata,
    Column('ancestor_concept_id', Integer, nullable=False),
    Column('descendant_concept_id', Integer, nullable=False),
    Column('min_levels_of_separation', Integer, nullable=False),
    Column('max_levels_of_separation', Integer, nullable=False),
    ForeignKeyConstraint(['ancestor_concept_id'], ['concept.concept_id'], name='fpk_concept_ancestor_ancestor_concept_id'),
    ForeignKeyConstraint(['descendant_concept_id'], ['concept.concept_id'], name='fpk_concept_ancestor_descendant_concept_id')
)


t_concept_synonym = Table(
    'concept_synonym', Base.metadata,
    Column('concept_id', Integer, nullable=False),
    Column('concept_synonym_name', String(1000), nullable=False),
    Column('language_concept_id', Integer, nullable=False),
    ForeignKeyConstraint(['concept_id'], ['concept.concept_id'], name='fpk_concept_synonym_concept_id'),
    ForeignKeyConstraint(['language_concept_id'], ['concept.concept_id'], name='fpk_concept_synonym_language_concept_id')
)


class Cost(Base):
    __tablename__ = 'cost'
    __table_args__ = (
        ForeignKeyConstraint(['cost_domain_id'], ['domain.domain_id'], name='fpk_cost_cost_domain_id'),
        ForeignKeyConstraint(['cost_type_concept_id'], ['concept.concept_id'], name='fpk_cost_cost_type_concept_id'),
        ForeignKeyConstraint(['currency_concept_id'], ['concept.concept_id'], name='fpk_cost_currency_concept_id'),
        ForeignKeyConstraint(['drg_concept_id'], ['concept.concept_id'], name='fpk_cost_drg_concept_id'),
        ForeignKeyConstraint(['revenue_code_concept_id'], ['concept.concept_id'], name='fpk_cost_revenue_code_concept_id'),
        PrimaryKeyConstraint('cost_id', name='xpk_cost')
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

    cost_domain: Mapped['Domain'] = relationship('Domain')
    cost_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[cost_type_concept_id])
    currency_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[currency_concept_id])
    drg_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drg_concept_id])
    revenue_code_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[revenue_code_concept_id])


t_drug_strength = Table(
    'drug_strength', Base.metadata,
    Column('drug_concept_id', Integer, nullable=False),
    Column('ingredient_concept_id', Integer, nullable=False),
    Column('amount_value', Numeric),
    Column('amount_unit_concept_id', Integer),
    Column('numerator_value', Numeric),
    Column('numerator_unit_concept_id', Integer),
    Column('denominator_value', Numeric),
    Column('denominator_unit_concept_id', Integer),
    Column('box_size', Integer),
    Column('valid_start_date', Date, nullable=False),
    Column('valid_end_date', Date, nullable=False),
    Column('invalid_reason', String(1)),
    ForeignKeyConstraint(['amount_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_amount_unit_concept_id'),
    ForeignKeyConstraint(['denominator_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_denominator_unit_concept_id'),
    ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_drug_concept_id'),
    ForeignKeyConstraint(['ingredient_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_ingredient_concept_id'),
    ForeignKeyConstraint(['numerator_unit_concept_id'], ['concept.concept_id'], name='fpk_drug_strength_numerator_unit_concept_id')
)


t_fact_relationship = Table(
    'fact_relationship', Base.metadata,
    Column('domain_concept_id_1', Integer, nullable=False),
    Column('fact_id_1', Integer, nullable=False),
    Column('domain_concept_id_2', Integer, nullable=False),
    Column('fact_id_2', Integer, nullable=False),
    Column('relationship_concept_id', Integer, nullable=False),
    ForeignKeyConstraint(['domain_concept_id_1'], ['concept.concept_id'], name='fpk_fact_relationship_domain_concept_id_1'),
    ForeignKeyConstraint(['domain_concept_id_2'], ['concept.concept_id'], name='fpk_fact_relationship_domain_concept_id_2'),
    ForeignKeyConstraint(['relationship_concept_id'], ['concept.concept_id'], name='fpk_fact_relationship_relationship_concept_id')
)


class Location(Base):
    __tablename__ = 'location'
    __table_args__ = (
        ForeignKeyConstraint(['country_concept_id'], ['concept.concept_id'], name='fpk_location_country_concept_id'),
        PrimaryKeyConstraint('location_id', name='xpk_location')
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

    country_concept: Mapped['Concept'] = relationship('Concept')


class Metadata(Base):
    __tablename__ = 'metadata'
    __table_args__ = (
        ForeignKeyConstraint(['metadata_concept_id'], ['concept.concept_id'], name='fpk_metadata_metadata_concept_id'),
        ForeignKeyConstraint(['metadata_type_concept_id'], ['concept.concept_id'], name='fpk_metadata_metadata_type_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_metadata_value_as_concept_id'),
        PrimaryKeyConstraint('metadata_id', name='xpk_metadata')
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

    metadata_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[metadata_concept_id])
    metadata_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[metadata_type_concept_id])
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id])


class NoteNlp(Base):
    __tablename__ = 'note_nlp'
    __table_args__ = (
        ForeignKeyConstraint(['note_nlp_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_note_nlp_concept_id'),
        ForeignKeyConstraint(['note_nlp_source_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_note_nlp_source_concept_id'),
        ForeignKeyConstraint(['section_concept_id'], ['concept.concept_id'], name='fpk_note_nlp_section_concept_id'),
        PrimaryKeyConstraint('note_nlp_id', name='xpk_note_nlp')
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

    note_nlp_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_nlp_concept_id])
    note_nlp_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_nlp_source_concept_id])
    section_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[section_concept_id])


class Relationship(Base):
    __tablename__ = 'relationship'
    __table_args__ = (
        ForeignKeyConstraint(['relationship_concept_id'], ['concept.concept_id'], name='fpk_relationship_relationship_concept_id'),
        PrimaryKeyConstraint('relationship_id', name='xpk_relationship')
    )

    relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    relationship_name: Mapped[str] = mapped_column(String(255))
    is_hierarchical: Mapped[str] = mapped_column(String(1))
    defines_ancestry: Mapped[str] = mapped_column(String(1))
    reverse_relationship_id: Mapped[str] = mapped_column(String(20))
    relationship_concept_id: Mapped[int] = mapped_column(Integer)

    relationship_concept: Mapped['Concept'] = relationship('Concept')


t_source_to_concept_map = Table(
    'source_to_concept_map', Base.metadata,
    Column('source_code', String(50), nullable=False),
    Column('source_concept_id', Integer, nullable=False),
    Column('source_vocabulary_id', String(20), nullable=False),
    Column('source_code_description', String(255)),
    Column('target_concept_id', Integer, nullable=False),
    Column('target_vocabulary_id', String(20), nullable=False),
    Column('valid_start_date', Date, nullable=False),
    Column('valid_end_date', Date, nullable=False),
    Column('invalid_reason', String(1)),
    ForeignKeyConstraint(['source_concept_id'], ['concept.concept_id'], name='fpk_source_to_concept_map_source_concept_id'),
    ForeignKeyConstraint(['target_concept_id'], ['concept.concept_id'], name='fpk_source_to_concept_map_target_concept_id'),
    ForeignKeyConstraint(['target_vocabulary_id'], ['vocabulary.vocabulary_id'], name='fpk_source_to_concept_map_target_vocabulary_id')
)


class CareSite(Base):
    __tablename__ = 'care_site'
    __table_args__ = (
        ForeignKeyConstraint(['location_id'], ['location.location_id'], name='fpk_care_site_location_id'),
        ForeignKeyConstraint(['place_of_service_concept_id'], ['concept.concept_id'], name='fpk_care_site_place_of_service_concept_id'),
        PrimaryKeyConstraint('care_site_id', name='xpk_care_site')
    )

    care_site_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    care_site_name: Mapped[Optional[str]] = mapped_column(String(255))
    place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    place_of_service_source_value: Mapped[Optional[str]] = mapped_column(String(50))

    location: Mapped['Location'] = relationship('Location')
    place_of_service_concept: Mapped['Concept'] = relationship('Concept')


t_concept_relationship = Table(
    'concept_relationship', Base.metadata,
    Column('concept_id_1', Integer, nullable=False),
    Column('concept_id_2', Integer, nullable=False),
    Column('relationship_id', String(20), nullable=False),
    Column('valid_start_date', Date, nullable=False),
    Column('valid_end_date', Date, nullable=False),
    Column('invalid_reason', String(1)),
    ForeignKeyConstraint(['concept_id_1'], ['concept.concept_id'], name='fpk_concept_relationship_concept_id_1'),
    ForeignKeyConstraint(['concept_id_2'], ['concept.concept_id'], name='fpk_concept_relationship_concept_id_2'),
    ForeignKeyConstraint(['relationship_id'], ['relationship.relationship_id'], name='fpk_concept_relationship_relationship_id')
)


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = (
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_provider_care_site_id'),
        ForeignKeyConstraint(['gender_concept_id'], ['concept.concept_id'], name='fpk_provider_gender_concept_id'),
        ForeignKeyConstraint(['gender_source_concept_id'], ['concept.concept_id'], name='fpk_provider_gender_source_concept_id'),
        ForeignKeyConstraint(['specialty_concept_id'], ['concept.concept_id'], name='fpk_provider_specialty_concept_id'),
        ForeignKeyConstraint(['specialty_source_concept_id'], ['concept.concept_id'], name='fpk_provider_specialty_source_concept_id'),
        PrimaryKeyConstraint('provider_id', name='xpk_provider')
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

    care_site: Mapped['CareSite'] = relationship('CareSite')
    gender_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_concept_id])
    gender_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_source_concept_id])
    specialty_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specialty_concept_id])
    specialty_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specialty_source_concept_id])


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_person_care_site_id'),
        ForeignKeyConstraint(['ethnicity_concept_id'], ['concept.concept_id'], name='fpk_person_ethnicity_concept_id'),
        ForeignKeyConstraint(['ethnicity_source_concept_id'], ['concept.concept_id'], name='fpk_person_ethnicity_source_concept_id'),
        ForeignKeyConstraint(['gender_concept_id'], ['concept.concept_id'], name='fpk_person_gender_concept_id'),
        ForeignKeyConstraint(['gender_source_concept_id'], ['concept.concept_id'], name='fpk_person_gender_source_concept_id'),
        ForeignKeyConstraint(['location_id'], ['location.location_id'], name='fpk_person_location_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_person_provider_id'),
        ForeignKeyConstraint(['race_concept_id'], ['concept.concept_id'], name='fpk_person_race_concept_id'),
        ForeignKeyConstraint(['race_source_concept_id'], ['concept.concept_id'], name='fpk_person_race_source_concept_id'),
        PrimaryKeyConstraint('person_id', name='xpk_person')
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

    care_site: Mapped['CareSite'] = relationship('CareSite')
    ethnicity_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ethnicity_concept_id])
    ethnicity_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[ethnicity_source_concept_id])
    gender_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_concept_id])
    gender_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[gender_source_concept_id])
    location: Mapped['Location'] = relationship('Location')
    provider: Mapped['Provider'] = relationship('Provider')
    race_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[race_concept_id])
    race_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[race_source_concept_id])


class ConditionEra(Base):
    __tablename__ = 'condition_era'
    __table_args__ = (
        ForeignKeyConstraint(['condition_concept_id'], ['concept.concept_id'], name='fpk_condition_era_condition_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_condition_era_person_id'),
        PrimaryKeyConstraint('condition_era_id', name='xpk_condition_era')
    )

    condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer)
    condition_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    condition_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    condition_occurrence_count: Mapped[Optional[int]] = mapped_column(Integer)

    condition_concept: Mapped['Concept'] = relationship('Concept')
    person: Mapped['Person'] = relationship('Person')


t_death = Table(
    'death', Base.metadata,
    Column('person_id', Integer, nullable=False),
    Column('death_date', Date, nullable=False),
    Column('death_datetime', DateTime),
    Column('death_type_concept_id', Integer),
    Column('cause_concept_id', Integer),
    Column('cause_source_value', String(50)),
    Column('cause_source_concept_id', Integer),
    ForeignKeyConstraint(['cause_concept_id'], ['concept.concept_id'], name='fpk_death_cause_concept_id'),
    ForeignKeyConstraint(['cause_source_concept_id'], ['concept.concept_id'], name='fpk_death_cause_source_concept_id'),
    ForeignKeyConstraint(['death_type_concept_id'], ['concept.concept_id'], name='fpk_death_death_type_concept_id'),
    ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_death_person_id')
)


class DoseEra(Base):
    __tablename__ = 'dose_era'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_dose_era_drug_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_dose_era_person_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_dose_era_unit_concept_id'),
        PrimaryKeyConstraint('dose_era_id', name='xpk_dose_era')
    )

    dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    unit_concept_id: Mapped[int] = mapped_column(Integer)
    dose_value: Mapped[decimal.Decimal] = mapped_column(Numeric)
    dose_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    dose_era_end_date: Mapped[datetime.date] = mapped_column(Date)

    drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id])
    person: Mapped['Person'] = relationship('Person')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id])


class DrugEra(Base):
    __tablename__ = 'drug_era'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_era_drug_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_drug_era_person_id'),
        PrimaryKeyConstraint('drug_era_id', name='xpk_drug_era')
    )

    drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    drug_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    drug_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_exposure_count: Mapped[Optional[int]] = mapped_column(Integer)
    gap_days: Mapped[Optional[int]] = mapped_column(Integer)

    drug_concept: Mapped['Concept'] = relationship('Concept')
    person: Mapped['Person'] = relationship('Person')


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        ForeignKeyConstraint(['episode_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_concept_id'),
        ForeignKeyConstraint(['episode_object_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_object_concept_id'),
        ForeignKeyConstraint(['episode_source_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_source_concept_id'),
        ForeignKeyConstraint(['episode_type_concept_id'], ['concept.concept_id'], name='fpk_episode_episode_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_episode_person_id'),
        PrimaryKeyConstraint('episode_id', name='xpk_episode')
    )

    episode_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    episode_concept_id: Mapped[int] = mapped_column(Integer)
    episode_start_date: Mapped[datetime.date] = mapped_column(Date)
    episode_object_concept_id: Mapped[int] = mapped_column(Integer)
    episode_type_concept_id: Mapped[int] = mapped_column(Integer)
    episode_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    episode_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    episode_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    episode_parent_id: Mapped[Optional[int]] = mapped_column(Integer)
    episode_number: Mapped[Optional[int]] = mapped_column(Integer)
    episode_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    episode_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)

    episode_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_concept_id])
    episode_object_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_object_concept_id])
    episode_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_source_concept_id])
    episode_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[episode_type_concept_id])
    person: Mapped['Person'] = relationship('Person')


class ObservationPeriod(Base):
    __tablename__ = 'observation_period'
    __table_args__ = (
        ForeignKeyConstraint(['period_type_concept_id'], ['concept.concept_id'], name='fpk_observation_period_period_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_observation_period_person_id'),
        PrimaryKeyConstraint('observation_period_id', name='xpk_observation_period')
    )

    observation_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    observation_period_start_date: Mapped[datetime.date] = mapped_column(Date)
    observation_period_end_date: Mapped[datetime.date] = mapped_column(Date)
    period_type_concept_id: Mapped[int] = mapped_column(Integer)

    period_type_concept: Mapped['Concept'] = relationship('Concept')
    person: Mapped['Person'] = relationship('Person')


class PayerPlanPeriod(Base):
    __tablename__ = 'payer_plan_period'
    __table_args__ = (
        ForeignKeyConstraint(['payer_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_payer_concept_id'),
        ForeignKeyConstraint(['payer_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_payer_source_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_payer_plan_period_person_id'),
        ForeignKeyConstraint(['plan_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_plan_concept_id'),
        ForeignKeyConstraint(['plan_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_plan_source_concept_id'),
        ForeignKeyConstraint(['sponsor_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_sponsor_concept_id'),
        ForeignKeyConstraint(['sponsor_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_sponsor_source_concept_id'),
        ForeignKeyConstraint(['stop_reason_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_stop_reason_concept_id'),
        ForeignKeyConstraint(['stop_reason_source_concept_id'], ['concept.concept_id'], name='fpk_payer_plan_period_stop_reason_source_concept_id'),
        PrimaryKeyConstraint('payer_plan_period_id', name='xpk_payer_plan_period')
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

    payer_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[payer_concept_id])
    payer_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[payer_source_concept_id])
    person: Mapped['Person'] = relationship('Person')
    plan_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[plan_concept_id])
    plan_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[plan_source_concept_id])
    sponsor_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[sponsor_concept_id])
    sponsor_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[sponsor_source_concept_id])
    stop_reason_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[stop_reason_concept_id])
    stop_reason_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[stop_reason_source_concept_id])


class Specimen(Base):
    __tablename__ = 'specimen'
    __table_args__ = (
        ForeignKeyConstraint(['anatomic_site_concept_id'], ['concept.concept_id'], name='fpk_specimen_anatomic_site_concept_id'),
        ForeignKeyConstraint(['disease_status_concept_id'], ['concept.concept_id'], name='fpk_specimen_disease_status_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_specimen_person_id'),
        ForeignKeyConstraint(['specimen_concept_id'], ['concept.concept_id'], name='fpk_specimen_specimen_concept_id'),
        ForeignKeyConstraint(['specimen_type_concept_id'], ['concept.concept_id'], name='fpk_specimen_specimen_type_concept_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_specimen_unit_concept_id'),
        PrimaryKeyConstraint('specimen_id', name='xpk_specimen')
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

    anatomic_site_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[anatomic_site_concept_id])
    disease_status_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[disease_status_concept_id])
    person: Mapped['Person'] = relationship('Person')
    specimen_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specimen_concept_id])
    specimen_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[specimen_type_concept_id])
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id])


class VisitOccurrence(Base):
    __tablename__ = 'visit_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['admitted_from_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_admitted_from_concept_id'),
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_visit_occurrence_care_site_id'),
        ForeignKeyConstraint(['discharged_to_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_discharged_to_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_visit_occurrence_person_id'),
        ForeignKeyConstraint(['preceding_visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_visit_occurrence_preceding_visit_occurrence_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_visit_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_concept_id'),
        ForeignKeyConstraint(['visit_source_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_source_concept_id'),
        ForeignKeyConstraint(['visit_type_concept_id'], ['concept.concept_id'], name='fpk_visit_occurrence_visit_type_concept_id'),
        PrimaryKeyConstraint('visit_occurrence_id', name='xpk_visit_occurrence')
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

    admitted_from_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[admitted_from_concept_id])
    care_site: Mapped['CareSite'] = relationship('CareSite')
    discharged_to_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[discharged_to_concept_id])
    person: Mapped['Person'] = relationship('Person')
    preceding_visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence', remote_side=[visit_occurrence_id])
    provider: Mapped['Provider'] = relationship('Provider')
    visit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_concept_id])
    visit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_source_concept_id])
    visit_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_type_concept_id])


t_episode_event = Table(
    'episode_event', Base.metadata,
    Column('episode_id', Integer, nullable=False),
    Column('event_id', Integer, nullable=False),
    Column('episode_event_field_concept_id', Integer, nullable=False),
    ForeignKeyConstraint(['episode_event_field_concept_id'], ['concept.concept_id'], name='fpk_episode_event_episode_event_field_concept_id'),
    ForeignKeyConstraint(['episode_id'], ['episode.episode_id'], name='fpk_episode_event_episode_id')
)


class VisitDetail(Base):
    __tablename__ = 'visit_detail'
    __table_args__ = (
        ForeignKeyConstraint(['admitted_from_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_admitted_from_concept_id'),
        ForeignKeyConstraint(['care_site_id'], ['care_site.care_site_id'], name='fpk_visit_detail_care_site_id'),
        ForeignKeyConstraint(['discharged_to_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_discharged_to_concept_id'),
        ForeignKeyConstraint(['parent_visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_visit_detail_parent_visit_detail_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_visit_detail_person_id'),
        ForeignKeyConstraint(['preceding_visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_visit_detail_preceding_visit_detail_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_visit_detail_provider_id'),
        ForeignKeyConstraint(['visit_detail_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_concept_id'),
        ForeignKeyConstraint(['visit_detail_source_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_source_concept_id'),
        ForeignKeyConstraint(['visit_detail_type_concept_id'], ['concept.concept_id'], name='fpk_visit_detail_visit_detail_type_concept_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_visit_detail_visit_occurrence_id'),
        PrimaryKeyConstraint('visit_detail_id', name='xpk_visit_detail')
    )

    visit_detail_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    visit_detail_concept_id: Mapped[int] = mapped_column(Integer)
    visit_detail_start_date: Mapped[datetime.date] = mapped_column(Date)
    visit_detail_end_date: Mapped[datetime.date] = mapped_column(Date)
    visit_detail_type_concept_id: Mapped[int] = mapped_column(Integer)
    visit_occurrence_id: Mapped[int] = mapped_column(Integer)
    visit_detail_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    visit_detail_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
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

    admitted_from_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[admitted_from_concept_id])
    care_site: Mapped['CareSite'] = relationship('CareSite')
    discharged_to_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[discharged_to_concept_id])
    parent_visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[parent_visit_detail_id])
    person: Mapped['Person'] = relationship('Person')
    preceding_visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail', remote_side=[visit_detail_id], foreign_keys=[preceding_visit_detail_id])
    provider: Mapped['Provider'] = relationship('Provider')
    visit_detail_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_concept_id])
    visit_detail_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_source_concept_id])
    visit_detail_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[visit_detail_type_concept_id])
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class ConditionOccurrence(Base):
    __tablename__ = 'condition_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['condition_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_concept_id'),
        ForeignKeyConstraint(['condition_source_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_source_concept_id'),
        ForeignKeyConstraint(['condition_status_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_status_concept_id'),
        ForeignKeyConstraint(['condition_type_concept_id'], ['concept.concept_id'], name='fpk_condition_occurrence_condition_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_condition_occurrence_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_condition_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_condition_occurrence_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_condition_occurrence_visit_occurrence_id'),
        PrimaryKeyConstraint('condition_occurrence_id', name='xpk_condition_occurrence')
    )

    condition_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer)
    condition_start_date: Mapped[datetime.date] = mapped_column(Date)
    condition_type_concept_id: Mapped[int] = mapped_column(Integer)
    condition_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    condition_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    condition_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    condition_status_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    stop_reason: Mapped[Optional[str]] = mapped_column(String(20))
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    condition_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    condition_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    condition_status_source_value: Mapped[Optional[str]] = mapped_column(String(50))

    condition_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_concept_id])
    condition_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_source_concept_id])
    condition_status_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_status_concept_id])
    condition_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[condition_type_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class DeviceExposure(Base):
    __tablename__ = 'device_exposure'
    __table_args__ = (
        ForeignKeyConstraint(['device_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_concept_id'),
        ForeignKeyConstraint(['device_source_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_source_concept_id'),
        ForeignKeyConstraint(['device_type_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_device_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_device_exposure_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_device_exposure_provider_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_unit_concept_id'),
        ForeignKeyConstraint(['unit_source_concept_id'], ['concept.concept_id'], name='fpk_device_exposure_unit_source_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_device_exposure_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_device_exposure_visit_occurrence_id'),
        PrimaryKeyConstraint('device_exposure_id', name='xpk_device_exposure')
    )

    device_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    device_concept_id: Mapped[int] = mapped_column(Integer)
    device_exposure_start_date: Mapped[datetime.date] = mapped_column(Date)
    device_type_concept_id: Mapped[int] = mapped_column(Integer)
    device_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    device_exposure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    device_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
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

    device_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_concept_id])
    device_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_source_concept_id])
    device_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[device_type_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id])
    unit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_source_concept_id])
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class DrugExposure(Base):
    __tablename__ = 'drug_exposure'
    __table_args__ = (
        ForeignKeyConstraint(['drug_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_concept_id'),
        ForeignKeyConstraint(['drug_source_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_source_concept_id'),
        ForeignKeyConstraint(['drug_type_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_drug_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_drug_exposure_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_drug_exposure_provider_id'),
        ForeignKeyConstraint(['route_concept_id'], ['concept.concept_id'], name='fpk_drug_exposure_route_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_drug_exposure_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_drug_exposure_visit_occurrence_id'),
        PrimaryKeyConstraint('drug_exposure_id', name='xpk_drug_exposure')
    )

    drug_exposure_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    drug_exposure_start_date: Mapped[datetime.date] = mapped_column(Date)
    drug_exposure_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_type_concept_id: Mapped[int] = mapped_column(Integer)
    drug_exposure_start_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    drug_exposure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
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

    drug_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_concept_id])
    drug_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_source_concept_id])
    drug_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[drug_type_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    route_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[route_concept_id])
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class Measurement(Base):
    __tablename__ = 'measurement'
    __table_args__ = (
        ForeignKeyConstraint(['meas_event_field_concept_id'], ['concept.concept_id'], name='fpk_measurement_meas_event_field_concept_id'),
        ForeignKeyConstraint(['measurement_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_concept_id'),
        ForeignKeyConstraint(['measurement_source_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_source_concept_id'),
        ForeignKeyConstraint(['measurement_type_concept_id'], ['concept.concept_id'], name='fpk_measurement_measurement_type_concept_id'),
        ForeignKeyConstraint(['operator_concept_id'], ['concept.concept_id'], name='fpk_measurement_operator_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_measurement_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_measurement_provider_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_measurement_unit_concept_id'),
        ForeignKeyConstraint(['unit_source_concept_id'], ['concept.concept_id'], name='fpk_measurement_unit_source_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_measurement_value_as_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_measurement_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_measurement_visit_occurrence_id'),
        PrimaryKeyConstraint('measurement_id', name='xpk_measurement')
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

    meas_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[meas_event_field_concept_id])
    measurement_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_concept_id])
    measurement_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_source_concept_id])
    measurement_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[measurement_type_concept_id])
    operator_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[operator_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id])
    unit_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_source_concept_id])
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id])
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class Note(Base):
    __tablename__ = 'note'
    __table_args__ = (
        ForeignKeyConstraint(['encoding_concept_id'], ['concept.concept_id'], name='fpk_note_encoding_concept_id'),
        ForeignKeyConstraint(['language_concept_id'], ['concept.concept_id'], name='fpk_note_language_concept_id'),
        ForeignKeyConstraint(['note_class_concept_id'], ['concept.concept_id'], name='fpk_note_note_class_concept_id'),
        ForeignKeyConstraint(['note_event_field_concept_id'], ['concept.concept_id'], name='fpk_note_note_event_field_concept_id'),
        ForeignKeyConstraint(['note_type_concept_id'], ['concept.concept_id'], name='fpk_note_note_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_note_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_note_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_note_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_note_visit_occurrence_id'),
        PrimaryKeyConstraint('note_id', name='xpk_note')
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

    encoding_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[encoding_concept_id])
    language_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[language_concept_id])
    note_class_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_class_concept_id])
    note_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_event_field_concept_id])
    note_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[note_type_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = (
        ForeignKeyConstraint(['obs_event_field_concept_id'], ['concept.concept_id'], name='fpk_observation_obs_event_field_concept_id'),
        ForeignKeyConstraint(['observation_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_concept_id'),
        ForeignKeyConstraint(['observation_source_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_source_concept_id'),
        ForeignKeyConstraint(['observation_type_concept_id'], ['concept.concept_id'], name='fpk_observation_observation_type_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_observation_person_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_observation_provider_id'),
        ForeignKeyConstraint(['qualifier_concept_id'], ['concept.concept_id'], name='fpk_observation_qualifier_concept_id'),
        ForeignKeyConstraint(['unit_concept_id'], ['concept.concept_id'], name='fpk_observation_unit_concept_id'),
        ForeignKeyConstraint(['value_as_concept_id'], ['concept.concept_id'], name='fpk_observation_value_as_concept_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_observation_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_observation_visit_occurrence_id'),
        PrimaryKeyConstraint('observation_id', name='xpk_observation')
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

    obs_event_field_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[obs_event_field_concept_id])
    observation_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_concept_id])
    observation_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_source_concept_id])
    observation_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[observation_type_concept_id])
    person: Mapped['Person'] = relationship('Person')
    provider: Mapped['Provider'] = relationship('Provider')
    qualifier_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[qualifier_concept_id])
    unit_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[unit_concept_id])
    value_as_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[value_as_concept_id])
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')


class ProcedureOccurrence(Base):
    __tablename__ = 'procedure_occurrence'
    __table_args__ = (
        ForeignKeyConstraint(['modifier_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_modifier_concept_id'),
        ForeignKeyConstraint(['person_id'], ['person.person_id'], name='fpk_procedure_occurrence_person_id'),
        ForeignKeyConstraint(['procedure_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_concept_id'),
        ForeignKeyConstraint(['procedure_source_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_source_concept_id'),
        ForeignKeyConstraint(['procedure_type_concept_id'], ['concept.concept_id'], name='fpk_procedure_occurrence_procedure_type_concept_id'),
        ForeignKeyConstraint(['provider_id'], ['provider.provider_id'], name='fpk_procedure_occurrence_provider_id'),
        ForeignKeyConstraint(['visit_detail_id'], ['visit_detail.visit_detail_id'], name='fpk_procedure_occurrence_visit_detail_id'),
        ForeignKeyConstraint(['visit_occurrence_id'], ['visit_occurrence.visit_occurrence_id'], name='fpk_procedure_occurrence_visit_occurrence_id'),
        PrimaryKeyConstraint('procedure_occurrence_id', name='xpk_procedure_occurrence')
    )

    procedure_occurrence_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    procedure_concept_id: Mapped[int] = mapped_column(Integer)
    procedure_date: Mapped[datetime.date] = mapped_column(Date)
    procedure_type_concept_id: Mapped[int] = mapped_column(Integer)
    procedure_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    procedure_end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    procedure_end_datetime: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    modifier_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    quantity: Mapped[Optional[int]] = mapped_column(Integer)
    provider_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_occurrence_id: Mapped[Optional[int]] = mapped_column(Integer)
    visit_detail_id: Mapped[Optional[int]] = mapped_column(Integer)
    procedure_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    procedure_source_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    modifier_source_value: Mapped[Optional[str]] = mapped_column(String(50))

    modifier_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[modifier_concept_id])
    person: Mapped['Person'] = relationship('Person')
    procedure_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_concept_id])
    procedure_source_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_source_concept_id])
    procedure_type_concept: Mapped['Concept'] = relationship('Concept', foreign_keys=[procedure_type_concept_id])
    provider: Mapped['Provider'] = relationship('Provider')
    visit_detail: Mapped['VisitDetail'] = relationship('VisitDetail')
    visit_occurrence: Mapped['VisitOccurrence'] = relationship('VisitOccurrence')
