FROM prefecthq/prefect:2.18.3-python3.12
RUN apt update
RUN apt install -y curl
RUN curl -sSL https://get.docker.com/ | sh
RUN pip install prefect-docker
