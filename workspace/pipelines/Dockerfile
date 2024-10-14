# build from workspace/
FROM prefecthq/prefect:2.18.3-python3.12

RUN apt update \
    && apt install -y libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt clean

COPY ./shared/requirements.txt /opt/prefect/env/shared-requirements.txt
RUN pip install -r /opt/prefect/env/shared-requirements.txt

COPY ./pipelines/requirements.txt /opt/prefect/env/pipeline-requirements.txt
RUN pip install -r /opt/prefect/env/pipeline-requirements.txt

COPY ./pipelines/src /opt/prefect/pipelines/src
COPY ./shared /opt/prefect/pipelines/src/shared

WORKDIR /opt/prefect/
