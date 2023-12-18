
# helper for downloading the CSV files from the CommonDataModel repo

CDM_VERSION_LONG=v5.4.1
CDM_VERSION_SHORT=5.4
DIALECT=postgresql
BASE_URL=https://raw.githubusercontent.com/OHDSI/CommonDataModel/$(CDM_VERSION_LONG)/inst/ddl/$(CDM_VERSION_SHORT)/$(DIALECT)
CURL=curl -fsSL

NAMES=\
OMOPCDM_${DIALECT}_${CDM_VERSION_SHORT}_constraints.sql \
OMOPCDM_${DIALECT}_${CDM_VERSION_SHORT}_ddl.sql \
OMOPCDM_${DIALECT}_${CDM_VERSION_SHORT}_indices.sql \
OMOPCDM_${DIALECT}_${CDM_VERSION_SHORT}_primary_keys.sql

.PHONY: all clean
all: $(NAMES)
clean:
	rm -fv $(NAMES)

%.sql:
	$(CURL) -o $@ "$(BASE_URL)/$@"
