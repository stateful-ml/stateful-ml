FROM prefecthq/prefect:2.18.3-python3.12

RUN apt update
RUN apt install -y libpq-dev

COPY ./shared/requirements.txt /opt/prefect/env/shared_requirements.txt
COPY ./pipelines/requirements.txt /opt/prefect/env/pipeline_requirements.txt
RUN pip install -r /opt/prefect/env/shared_requirements.txt
RUN pip install -r /opt/prefect/env/pipeline_requirements.txt

COPY ./pipelines/src /opt/prefect/pipelines/src
COPY ./shared /opt/prefect/pipelines/src/shared


WORKDIR /opt/prefect/

