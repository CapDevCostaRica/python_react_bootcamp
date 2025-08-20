FROM python:3.13.7-slim

RUN apt-get -q -y update
RUN apt install -y git
WORKDIR /app

ARG APPLICATION_FOLDER

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./contributors/${APPLICATION_FOLDER}/requirements.txt /app/contributors/${APPLICATION_FOLDER}/requirements.txt
RUN pip install --no-cache-dir -r /app/contributors/${APPLICATION_FOLDER}/requirements.txt

EXPOSE 4000
