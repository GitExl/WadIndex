#!/bin/sh

cd /var/www/html/api

if [[ -z ${DEV_ENV+x} ]]; then
  composer install --no-ansi --no-dev --no-interaction --no-plugins --no-progress --no-scripts --optimize-autoloader
  mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
fi
