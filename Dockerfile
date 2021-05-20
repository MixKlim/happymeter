FROM python:3.8-slim

COPY ./src /happymeter/src
COPY ./requirements.txt /happymeter

WORKDIR /happymeter

RUN pip3 install -r requirements.txt

WORKDIR /happymeter/src/app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host=127.0.0.1", "--reload"]
