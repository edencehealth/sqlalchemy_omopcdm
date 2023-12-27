# `sqlalchemy_omopcdm`

## About

In this repo we setup a postgres database container with the official OMOP CDM v5.4 DDL and PK constraints, then we run [sqlacodegen](https://github.com/agronholm/sqlacodegen) on the database and make some limited tweaks (such as adding documentation, setting the base model name, and applying the formatting tools `isort` and `black`).

You can recreate the output file with the following command:

`docker compose run --rm --build modelgen`

This single command will bring up the database, load the DDL into it, build the modelgen container, and run it against the database. The result is written to the output dir.

## Generating

When invoked with the `-h` / `--help` argument, the program emits this help documentation:

```
usage: modelgen [-h] [--log-dir LOG_DIR]
                [--log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}]
                [--db-dbms DB_DBMS] [--db-host DB_HOST] [--db-port DB_PORT]
                [--db-name DB_NAME] [--db-password DB_PASSWORD]
                [--db-user DB_USER] [--options OPTIONS]
                [--generator GENERATOR] [--output-file OUTPUT_FILE]
                [--base-doc-url BASE_DOC_URL] [--base-ddl-url BASE_DDL_URL]
                [--base-class-name BASE_CLASS_NAME]
                [--base-class-desc BASE_CLASS_DESC]
                [--cdm-version CDM_VERSION] [--cdm-schema CDM_SCHEMA]

options:
  -h, --help            show this help message and exit
  --log-dir LOG_DIR     directory where run logs should be written (default:
                        '/log')
  --log-level {CRITICAL,ERROR,WARNING,INFO,DEBUG}
                        the level of verbosity to use when writing to the
                        console (default: 'INFO')
  --db-dbms DB_DBMS     database management system operating on the db_host;
                        this is used to construct the DDL URLs (default:
                        'postgresql')
  --db-host DB_HOST     network hostname to use when connecting to db server
                        (default: 'localhost')
  --db-port DB_PORT     network port number to use when connecting to db
                        server (default: 5432)
  --db-name DB_NAME     (default: 'postgres')
  --db-password DB_PASSWORD
                        (default: 'postgres')
  --db-user DB_USER     (default: 'postgres')
  --options OPTIONS     options to pass to sqlacodegen (default: None)
  --generator GENERATOR
                        which sqlacodegen generator to use (default: None)
  --output-file OUTPUT_FILE
                        full path at which the output file should be written
                        (default: 'model.py')
  --base-doc-url BASE_DOC_URL
                        URL for both the OMOP CDM Table documentation links
                        and the page from which table descriptions are drawn
                        (default:
                        'https://ohdsi.github.io/CommonDataModel/cdm54.html')
  --base-ddl-url BASE_DDL_URL
                        URL template from which the official DDL files should
                        be downloaded from (default: 'https://raw.githubuserco
                        ntent.com/OHDSI/CommonDataModel/{cdm_version}/inst/ddl
                        /{cdm_version_short}/{dialect}')
  --base-class-name BASE_CLASS_NAME
                        the name of the base class which the models are all
                        subclasses of (default: 'OMOPCDMModelBase')
  --base-class-desc BASE_CLASS_DESC
                        the description used for the base class (default:
                        'Base for OMOP Common Data Model v5.4 Models')
  --cdm-version CDM_VERSION
                        the OMOP CDM version to generate (default: 'v5.4.1')
  --cdm-schema CDM_SCHEMA
                        the name of the OMOP CDM schema within the database on
                        the server (default: 'public')
```
