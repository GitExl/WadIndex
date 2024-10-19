FROM pypy:3.10-7.3.17

RUN apt-get update && apt-get install -y \
  p7zip-full \
  bash \
  cron \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

COPY crontab /etc/crontabs/root

CMD ["cron", "-f", "-l", "2"]
