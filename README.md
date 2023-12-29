# `sqlalchemy_omopcdm`

## About

This package contains [Declarative Mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping)-based SQLAlchemy 2 models for each table in the OMOP CDM, including primary keys, indexes, and constraints. These models can be used to work with OMOP CDM databases - including the ability to initialize and query them.

The models in this repo are automatically created using the [sqlacodegen](https://pypi.org/project/sqlacodegen/)-based [sqlalchemy_omopcdm_modelgen](https://github.com/edencehealth/sqlalchemy_omopcdm_modelgen) container image.

**Important Note**: In order to use Declarative Mapping, [each table needs at least one column with primary key behavior](https://docs.sqlalchemy.org/en/20/faq/ormconfiguration.html#how-do-i-map-a-table-that-has-no-primary-key), to achieve this we have added 11 [unofficial & unsupported **composite** primary keys](https://github.com/edencehealth/sqlalchemy_omopcdm_modelgen/blob/main/src/modelgen/sql/eh_mods.sql) on the following tables: `cdm_source`, `cohort_definition`, `cohort`, `concept_ancestor`, `concept_relationship`, `concept_synonym`, `death`, `drug_strength`, `episode_event`, `fact_relationship`, `source_to_concept_map`

## Model Generation

You can recreate the output file with the following command:

`docker compose run --rm modelgen`

This single command will bring up the database, load the DDL into it, build the modelgen container, and run it against the database. The result is written to the output dir.
