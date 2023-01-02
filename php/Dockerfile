FROM php:8.2-fpm

RUN apt-get update && \
  apt-get install -y \
    bash \
    git \
    curl \
    zip \
    unzip && \
  rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions -o - | sh -s \
  mysqli \
  intl \
  opcache

RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer --version=2.5.1
ENV PATH="/root/.composer/vendor/bin:$PATH"

RUN curl -sS https://get.symfony.com/cli/installer | bash
ENV PATH="/root/.symfony5/bin:$PATH"

COPY build.sh .
RUN ./build.sh

WORKDIR "/var/www/html/api"
