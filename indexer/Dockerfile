FROM python:3.9.16-alpine

RUN apk add --no-cache 7zip bash

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY crontab /etc/crontabs/root

CMD ["crond", "-f", "-d", "8"]
