FROM python:3.6-slim

RUN apt-get update && apt-get install -y build-essential
RUN pip install nameko emplo-nameko-zipkin

COPY . /app
WORKDIR /app
CMD nameko run --config=config.yml service
