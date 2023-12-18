#!/bin/sh
# helper which loads the ddl files mounted into the container into the database
set -eu
SELF=$(basename "$0" '.sh')


log() {
  printf '%s %s %s\n' "$(date '+%FT%T%z')" "$SELF" "$*" >&2
}

die() {
  log "FATAL:" "$@"
  exit 1
}

main() {
  # arg-processing loop
  while [ $# -gt 0 ]; do
    arg="$1" # shift at end of loop; if you break in the loop don't forget to shift first
    case "$arg" in
      -h|-help|--help)
        usage
        ;;

      -d|--debug)
        set -x
        ;;

      --mega-turtles)
        usage "You can't handle MEGA-TURTLES."
        ;;

      --turtle)
        shift || usage "--turtle requires an argument"
        TURTLE="$1"
        ;;

      --)
        shift || true
        break
        ;;

      *)
        # unknown arg, leave it back in the positional params
        break
        ;;
    esac
    shift || break
  done

  # ensure required environment variables are set
  # : "${USER:?the USER environment variable must be set}"

  # do things
  temp_dir=$(mktemp -d)

  CDM_SCHEMA=${CDM_SCHEMA:-omopcdm}
  log "creating schema ${CDM_SCHEMA}"
  psql -c "CREATE SCHEMA IF NOT EXISTS ${CDM_SCHEMA};"

    #"/ddl/OMOPCDM_postgresql_5.4_indices.sql" \
    #"/ddl/OMOPCDM_postgresql_5.4_constraints.sql" \
  for file in \
    "/ddl/OMOPCDM_postgresql_5.4_ddl.sql" \
    "/ddl/OMOPCDM_postgresql_5.4_primary_keys.sql" \
  ; do
    tmp_file="${temp_dir}/$(basename "$file")"
    log "expanding sql vars of ${file} into ${tmp_file}"
    sed "s/@cdmDatabaseSchema/${CDM_SCHEMA}/g" "$file" >"$tmp_file"

    log "loading ${tmp_file}"
    psql -f "$tmp_file"
  done

  log "exiting with success"
  exit 0
}

main "$@"
# shellcheck disable=SC2317
exit
