FROM prefecthq/prefect:2.18.3-python3.12
RUN apt update
RUN apt install -y curl
RUN apt install -y libpq-dev

RUN curl -sSL https://get.docker.com/ | sh
RUN pip install prefect-docker


COPY ./shared/requirements.txt shared_requirements.txt
COPY ./pipelines/requirements.txt pipeline_requirements.txt
RUN pip install -r shared_requirements.txt
RUN pip install -r pipeline_requirements.txt
