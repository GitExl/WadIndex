FROM php:8.2-fpm

RUN apt-get update && \
  docker-php-ext-configure mysqli \
  && docker-php-ext-install -j$(nproc) mysqli
