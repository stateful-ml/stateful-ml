FROM prefecthq/prefect:2.18.3-python3.12
RUN apt update && apt install -y docker
RUN pip install prefect-docker
