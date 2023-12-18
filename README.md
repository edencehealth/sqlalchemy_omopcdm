# sa_omopcdm

## how

In this repo we setup a postgres database container with the official OMOP CDM v5.4 DDL and PK constraints, then we run [sqlacodegen](https://github.com/agronholm/sqlacodegen) on the database.

You can recreate the output with:

`docker compose run --rm --build modelgen`

This command will bring up the database, load the DDL into it, build the modelgen container, and run it against the database. The result is written to the output dir.
