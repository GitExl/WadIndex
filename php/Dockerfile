FROM php:8.3-fpm

RUN apt-get update && \
  apt-get install -y \
    bash \
    git \
    curl \
    zip \
    unzip && \
  rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions -o - | sh -s \
  pdo_mysql \
  intl \
  opcache

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer --version=2.8.1
ENV PATH="$PATH:/root/.composer/vendor/bin"

RUN curl -sS https://get.symfony.com/cli/installer | bash
ENV PATH="$PATH:/root/.symfony5/bin"

COPY build.sh .
RUN ./build.sh

WORKDIR "/var/www/html/api"
