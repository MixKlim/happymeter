FROM python:3.10-slim

WORKDIR /happymeter

COPY ./requirements.txt .

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY src/ .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
