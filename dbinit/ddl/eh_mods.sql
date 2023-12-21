ALTER TABLE cdm_source
  ADD CONSTRAINT "eh_composite_pk_cdm_source" PRIMARY KEY (cdm_source_name, cdm_source_abbreviation, cdm_holder, source_description, source_documentation_reference, cdm_etl_reference, source_release_date, cdm_release_date, cdm_version, cdm_version_concept_id, vocabulary_version);

ALTER TABLE cohort
  ADD CONSTRAINT "eh_composite_pk_cohort" PRIMARY KEY (cohort_definition_id, subject_id, cohort_start_date, cohort_end_date);

ALTER TABLE cohort_definition
  ADD CONSTRAINT "eh_composite_pk_cohort_definition" PRIMARY KEY (cohort_definition_id, cohort_definition_name, cohort_definition_description, definition_type_concept_id, cohort_definition_syntax, subject_concept_id, cohort_initiation_date);

ALTER TABLE concept_ancestor
  ADD CONSTRAINT "eh_composite_pk_concept_ancestor" PRIMARY KEY (ancestor_concept_id, descendant_concept_id, min_levels_of_separation, max_levels_of_separation);

ALTER TABLE concept_relationship
  ADD CONSTRAINT "eh_composite_pk_concept_relationship" PRIMARY KEY (concept_id_1, concept_id_2, relationship_id, valid_start_date, valid_end_date, invalid_reason);

ALTER TABLE concept_synonym
  ADD CONSTRAINT "eh_composite_pk_concept_synonym" PRIMARY KEY (concept_id, concept_synonym_name, language_concept_id);

ALTER TABLE death
  ADD CONSTRAINT "eh_composite_pk_death" PRIMARY KEY (person_id, death_date, death_datetime, death_type_concept_id, cause_concept_id, cause_source_value, cause_source_concept_id);

ALTER TABLE drug_strength
  ADD CONSTRAINT "eh_composite_pk_drug_strength" PRIMARY KEY (drug_concept_id, ingredient_concept_id, amount_value, amount_unit_concept_id, numerator_value, numerator_unit_concept_id, denominator_value, denominator_unit_concept_id, box_size, valid_start_date, valid_end_date, invalid_reason);

ALTER TABLE episode_event
  ADD CONSTRAINT "eh_composite_pk_episode_event" PRIMARY KEY (episode_id, event_id, episode_event_field_concept_id);

ALTER TABLE fact_relationship
  ADD CONSTRAINT "eh_composite_pk_fact_relationship" PRIMARY KEY (domain_concept_id_1, fact_id_1, domain_concept_id_2, fact_id_2, relationship_concept_id);

ALTER TABLE source_to_concept_map
  ADD CONSTRAINT "eh_composite_pk_source_to_concept_map" PRIMARY KEY (source_code, source_concept_id, source_vocabulary_id, source_code_description, target_concept_id, target_vocabulary_id, valid_start_date, valid_end_date, invalid_reason);

