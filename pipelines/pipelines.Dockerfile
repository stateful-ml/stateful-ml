FROM prefecthq/prefect:2.18.3-python3.12
COPY requirements.txt /opt/prefect/pipelines/requirements.txt
RUN python -m pip install -r /opt/prefect/pipelines/requirements.txt
COPY . /opt/prefect/pipelines/
WORKDIR /opt/prefect/pipelines/
