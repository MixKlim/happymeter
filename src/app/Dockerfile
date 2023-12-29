FROM python:3.10-slim

RUN mkdir /fastapi

COPY ../../requirements.txt /fastapi

WORKDIR /fastapi

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . /fastapi

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
