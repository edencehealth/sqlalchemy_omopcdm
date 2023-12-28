FROM python:3.11-slim

ARG AG="apt-get -yq --no-install-recommends"
RUN set -eux; \
  $AG update; \
  $AG upgrade; \
  $AG install \
    git \
  ;

COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY ["src/modelgen", "/app/modelgen"]

# there's a bug in sqlacodegen 3.0.0rc3, we're just going to patch it for now
RUN set -eux; \
    sed -i 's/args.option.split/args.options.split/' \
    /usr/local/lib/python3.*/site-packages/sqlacodegen/cli.py

ENV PYTHONPATH="/app"
ENTRYPOINT [ "python3", "-m", "modelgen" ]
