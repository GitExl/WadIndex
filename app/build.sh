#!/bin/sh

npm install

if [[ -z ${DEV_ENV+x} ]]; then
  npm run build
else
  tail -f /dev/null
fi
