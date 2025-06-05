FROM python:3.12.7

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./src/ ./src/

WORKDIR /app/src