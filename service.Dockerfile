FROM python:3.11-slim
WORKDIR /code

COPY ./service/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# use your favourite workaround for forcing shared dirs into the context!
COPY ./service/app /code/app
COPY ./shared /code/app/shared

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
