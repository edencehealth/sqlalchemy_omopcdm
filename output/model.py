from typing import Optional

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class CareSite(Base):
    __tablename__ = 'care_site'
    __table_args__ = (
        PrimaryKeyConstraint('care_site_id', name='xpk_care_site'),
    )

    care_site_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    care_site_name: Mapped[Optional[str]] = mapped_column(String(255))
    place_of_service_concept_id: Mapped[Optional[int]] = mapped_column(Integer)
    location_id: Mapped[Optional[int]] = mapped_column(Integer)
    care_site_source_value: Mapped[Optional[str]] = mapped_column(String(50))
    place_of_service_source_value: Mapped[Optional[str]] = mapped_column(String(50))


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
    Column('vocabulary_version', String(20), nullable=False)
)


class Cohort(Base):
    __tablename__ = 'cohort'
    __table_args__ = (
        PrimaryKeyConstraint('cohort_definition_id', 'subject_id', 'cohort_start_date', 'cohort_end_date', name='eh_synth_pk'),
    )

    cohort_definition_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cohort_start_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)
    cohort_end_date: Mapped[datetime.date] = mapped_column(Date, primary_key=True)


t_cohort_definition = Table(
    'cohort_definition', Base.metadata,
    Column('cohort_definition_id', Integer, nullable=False),
    Column('cohort_definition_name', String(255), nullable=False),
    Column('cohort_definition_description', Text),
    Column('definition_type_concept_id', Integer, nullable=False),
    Column('cohort_definition_syntax', Text),
    Column('subject_concept_id', Integer, nullable=False),
    Column('cohort_initiation_date', Date)
)


class Concept(Base):
    __tablename__ = 'concept'
    __table_args__ = (
        PrimaryKeyConstraint('concept_id', name='xpk_concept'),
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


t_concept_ancestor = Table(
    'concept_ancestor', Base.metadata,
    Column('ancestor_concept_id', Integer, nullable=False),
    Column('descendant_concept_id', Integer, nullable=False),
    Column('min_levels_of_separation', Integer, nullable=False),
    Column('max_levels_of_separation', Integer, nullable=False)
)


class ConceptClass(Base):
    __tablename__ = 'concept_class'
    __table_args__ = (
        PrimaryKeyConstraint('concept_class_id', name='xpk_concept_class'),
    )

    concept_class_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    concept_class_name: Mapped[str] = mapped_column(String(255))
    concept_class_concept_id: Mapped[int] = mapped_column(Integer)


t_concept_relationship = Table(
    'concept_relationship', Base.metadata,
    Column('concept_id_1', Integer, nullable=False),
    Column('concept_id_2', Integer, nullable=False),
    Column('relationship_id', String(20), nullable=False),
    Column('valid_start_date', Date, nullable=False),
    Column('valid_end_date', Date, nullable=False),
    Column('invalid_reason', String(1))
)


t_concept_synonym = Table(
    'concept_synonym', Base.metadata,
    Column('concept_id', Integer, nullable=False),
    Column('concept_synonym_name', String(1000), nullable=False),
    Column('language_concept_id', Integer, nullable=False)
)


class ConditionEra(Base):
    __tablename__ = 'condition_era'
    __table_args__ = (
        PrimaryKeyConstraint('condition_era_id', name='xpk_condition_era'),
    )

    condition_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    condition_concept_id: Mapped[int] = mapped_column(Integer)
    condition_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    condition_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    condition_occurrence_count: Mapped[Optional[int]] = mapped_column(Integer)


class ConditionOccurrence(Base):
    __tablename__ = 'condition_occurrence'
    __table_args__ = (
        PrimaryKeyConstraint('condition_occurrence_id', name='xpk_condition_occurrence'),
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


class Cost(Base):
    __tablename__ = 'cost'
    __table_args__ = (
        PrimaryKeyConstraint('cost_id', name='xpk_cost'),
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


t_death = Table(
    'death', Base.metadata,
    Column('person_id', Integer, nullable=False),
    Column('death_date', Date, nullable=False),
    Column('death_datetime', DateTime),
    Column('death_type_concept_id', Integer),
    Column('cause_concept_id', Integer),
    Column('cause_source_value', String(50)),
    Column('cause_source_concept_id', Integer)
)


class DeviceExposure(Base):
    __tablename__ = 'device_exposure'
    __table_args__ = (
        PrimaryKeyConstraint('device_exposure_id', name='xpk_device_exposure'),
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


class Domain(Base):
    __tablename__ = 'domain'
    __table_args__ = (
        PrimaryKeyConstraint('domain_id', name='xpk_domain'),
    )

    domain_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    domain_name: Mapped[str] = mapped_column(String(255))
    domain_concept_id: Mapped[int] = mapped_column(Integer)


class DoseEra(Base):
    __tablename__ = 'dose_era'
    __table_args__ = (
        PrimaryKeyConstraint('dose_era_id', name='xpk_dose_era'),
    )

    dose_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    unit_concept_id: Mapped[int] = mapped_column(Integer)
    dose_value: Mapped[decimal.Decimal] = mapped_column(Numeric)
    dose_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    dose_era_end_date: Mapped[datetime.date] = mapped_column(Date)


class DrugEra(Base):
    __tablename__ = 'drug_era'
    __table_args__ = (
        PrimaryKeyConstraint('drug_era_id', name='xpk_drug_era'),
    )

    drug_era_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    drug_concept_id: Mapped[int] = mapped_column(Integer)
    drug_era_start_date: Mapped[datetime.date] = mapped_column(Date)
    drug_era_end_date: Mapped[datetime.date] = mapped_column(Date)
    drug_exposure_count: Mapped[Optional[int]] = mapped_column(Integer)
    gap_days: Mapped[Optional[int]] = mapped_column(Integer)


class DrugExposure(Base):
    __tablename__ = 'drug_exposure'
    __table_args__ = (
        PrimaryKeyConstraint('drug_exposure_id', name='xpk_drug_exposure'),
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
    Column('invalid_reason', String(1))
)


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        PrimaryKeyConstraint('episode_id', name='xpk_episode'),
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


t_episode_event = Table(
    'episode_event', Base.metadata,
    Column('episode_id', Integer, nullable=False),
    Column('event_id', Integer, nullable=False),
    Column('episode_event_field_concept_id', Integer, nullable=False)
)


t_fact_relationship = Table(
    'fact_relationship', Base.metadata,
    Column('domain_concept_id_1', Integer, nullable=False),
    Column('fact_id_1', Integer, nullable=False),
    Column('domain_concept_id_2', Integer, nullable=False),
    Column('fact_id_2', Integer, nullable=False),
    Column('relationship_concept_id', Integer, nullable=False)
)


class Location(Base):
    __tablename__ = 'location'
    __table_args__ = (
        PrimaryKeyConstraint('location_id', name='xpk_location'),
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


class Measurement(Base):
    __tablename__ = 'measurement'
    __table_args__ = (
        PrimaryKeyConstraint('measurement_id', name='xpk_measurement'),
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


class Metadata(Base):
    __tablename__ = 'metadata'
    __table_args__ = (
        PrimaryKeyConstraint('metadata_id', name='xpk_metadata'),
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


class Note(Base):
    __tablename__ = 'note'
    __table_args__ = (
        PrimaryKeyConstraint('note_id', name='xpk_note'),
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


class NoteNlp(Base):
    __tablename__ = 'note_nlp'
    __table_args__ = (
        PrimaryKeyConstraint('note_nlp_id', name='xpk_note_nlp'),
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


class Observation(Base):
    __tablename__ = 'observation'
    __table_args__ = (
        PrimaryKeyConstraint('observation_id', name='xpk_observation'),
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


class ObservationPeriod(Base):
    __tablename__ = 'observation_period'
    __table_args__ = (
        PrimaryKeyConstraint('observation_period_id', name='xpk_observation_period'),
    )

    observation_period_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(Integer)
    observation_period_start_date: Mapped[datetime.date] = mapped_column(Date)
    observation_period_end_date: Mapped[datetime.date] = mapped_column(Date)
    period_type_concept_id: Mapped[int] = mapped_column(Integer)


class PayerPlanPeriod(Base):
    __tablename__ = 'payer_plan_period'
    __table_args__ = (
        PrimaryKeyConstraint('payer_plan_period_id', name='xpk_payer_plan_period'),
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


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        PrimaryKeyConstraint('person_id', name='xpk_person'),
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


class ProcedureOccurrence(Base):
    __tablename__ = 'procedure_occurrence'
    __table_args__ = (
        PrimaryKeyConstraint('procedure_occurrence_id', name='xpk_procedure_occurrence'),
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


class Provider(Base):
    __tablename__ = 'provider'
    __table_args__ = (
        PrimaryKeyConstraint('provider_id', name='xpk_provider'),
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


class Relationship(Base):
    __tablename__ = 'relationship'
    __table_args__ = (
        PrimaryKeyConstraint('relationship_id', name='xpk_relationship'),
    )

    relationship_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    relationship_name: Mapped[str] = mapped_column(String(255))
    is_hierarchical: Mapped[str] = mapped_column(String(1))
    defines_ancestry: Mapped[str] = mapped_column(String(1))
    reverse_relationship_id: Mapped[str] = mapped_column(String(20))
    relationship_concept_id: Mapped[int] = mapped_column(Integer)


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
    Column('invalid_reason', String(1))
)


class Specimen(Base):
    __tablename__ = 'specimen'
    __table_args__ = (
        PrimaryKeyConstraint('specimen_id', name='xpk_specimen'),
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


class VisitDetail(Base):
    __tablename__ = 'visit_detail'
    __table_args__ = (
        PrimaryKeyConstraint('visit_detail_id', name='xpk_visit_detail'),
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


class VisitOccurrence(Base):
    __tablename__ = 'visit_occurrence'
    __table_args__ = (
        PrimaryKeyConstraint('visit_occurrence_id', name='xpk_visit_occurrence'),
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


class Vocabulary(Base):
    __tablename__ = 'vocabulary'
    __table_args__ = (
        PrimaryKeyConstraint('vocabulary_id', name='xpk_vocabulary'),
    )

    vocabulary_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    vocabulary_name: Mapped[str] = mapped_column(String(255))
    vocabulary_concept_id: Mapped[int] = mapped_column(Integer)
    vocabulary_reference: Mapped[Optional[str]] = mapped_column(String(255))
    vocabulary_version: Mapped[Optional[str]] = mapped_column(String(255))
