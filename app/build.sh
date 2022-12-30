#!/bin/sh

npm install

if [[ -z ${DEV_ENV+x} ]]; then
  npm run build
else
  npm run dev -- --host
fi
