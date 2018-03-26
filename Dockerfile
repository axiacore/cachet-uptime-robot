FROM python:3.6-alpine3.7

WORKDIR /usr/src/app

COPY . .

CMD sh run.sh