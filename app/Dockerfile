FROM node:20.18-alpine

RUN apk add bash

# Install this version until NPM gets its stuff together.
RUN npm --global install npm@10.3 --no-audit

WORKDIR /var/app
ENTRYPOINT ["./build.sh"]
