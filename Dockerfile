FROM python:3.12-rc-bullseye

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt