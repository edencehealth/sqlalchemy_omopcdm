ALTER TABLE @cdmDatabaseSchema.cdm_source
  ADD CONSTRAINT "eh_composite_pk_cdm_source" PRIMARY KEY (cdm_source_name, cdm_source_abbreviation, cdm_holder, source_release_date, cdm_release_date, cdm_version_concept_id, vocabulary_version);

ALTER TABLE @cdmDatabaseSchema.cohort
  ADD CONSTRAINT "eh_composite_pk_cohort" PRIMARY KEY (cohort_definition_id, subject_id, cohort_start_date, cohort_end_date);

ALTER TABLE @cdmDatabaseSchema.cohort_definition
  ADD CONSTRAINT "eh_composite_pk_cohort_definition" PRIMARY KEY (cohort_definition_id, cohort_definition_name, definition_type_concept_id, subject_concept_id);

ALTER TABLE @cdmDatabaseSchema.concept_ancestor
  ADD CONSTRAINT "eh_composite_pk_concept_ancestor" PRIMARY KEY (ancestor_concept_id, descendant_concept_id, min_levels_of_separation, max_levels_of_separation);

ALTER TABLE @cdmDatabaseSchema.concept_relationship
  ADD CONSTRAINT "eh_composite_pk_concept_relationship" PRIMARY KEY (concept_id_1, concept_id_2, relationship_id, valid_start_date, valid_end_date);

ALTER TABLE @cdmDatabaseSchema.concept_synonym
  ADD CONSTRAINT "eh_composite_pk_concept_synonym" PRIMARY KEY (concept_id, concept_synonym_name, language_concept_id);

ALTER TABLE @cdmDatabaseSchema.death
  ADD CONSTRAINT "eh_composite_pk_death" PRIMARY KEY (person_id, death_date);

ALTER TABLE @cdmDatabaseSchema.drug_strength
  ADD CONSTRAINT "eh_composite_pk_drug_strength" PRIMARY KEY (drug_concept_id, ingredient_concept_id, valid_start_date, valid_end_date);

ALTER TABLE @cdmDatabaseSchema.episode_event
  ADD CONSTRAINT "eh_composite_pk_episode_event" PRIMARY KEY (episode_id, event_id, episode_event_field_concept_id);

ALTER TABLE @cdmDatabaseSchema.fact_relationship
  ADD CONSTRAINT "eh_composite_pk_fact_relationship" PRIMARY KEY (domain_concept_id_1, fact_id_1, domain_concept_id_2, fact_id_2, relationship_concept_id);

ALTER TABLE @cdmDatabaseSchema.source_to_concept_map
  ADD CONSTRAINT "eh_composite_pk_source_to_concept_map" PRIMARY KEY (source_code, source_concept_id, source_vocabulary_id, target_concept_id, target_vocabulary_id, valid_start_date, valid_end_date);
