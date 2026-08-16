# syntax=docker/dockerfile:1

FROM python:3.13-slim

WORKDIR /moonpie

COPY requirements.txt /moonpie
RUN pip install --no-cache-dir -r requirements.txt

COPY . /moonpie

CMD ["gunicorn", "-w", "2", "moonpie:create_app()"]
