#!/usr/bin/env bash

set -ex

echo "start post create command..."

# install requirements.dev
pip install -r requirements.dev

# install pre-commit
pre-commit install

# copy .example.env to .env
cp .example.env .env

# install requirements.txt
pip install -r requirements.txt

# docker compose up
# docker compose up -d

# start app
make app

echo "done post create command"
