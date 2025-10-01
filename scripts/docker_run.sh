#!/usr/bin/env bash
set -e
docker compose up --build -d
docker compose ps