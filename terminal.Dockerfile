FROM python:3.11-slim

COPY ./workspace/shared/requirements.txt /shared-requirements.txt
RUN pip install --no-cache-dir -r /shared-requirements.txt

COPY . /code
WORKDIR /code

CMD [ "/bin/bash" ]
