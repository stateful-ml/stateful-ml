FROM prefecthq/prefect:2.18.3-python3.12
COPY ./pipelines/requirements.txt /opt/prefect/pipelines/requirements.txt
RUN python -m pip install -r /opt/prefect/pipelines/requirements.txt
COPY ./pipelines/src /opt/prefect/pipelines/
COPY ./shared /opt/prefect/pipelines/shared
WORKDIR /opt/prefect/pipelines/
