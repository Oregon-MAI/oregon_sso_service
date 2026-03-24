#!/bin/sh
set -e
sleep 5
alembic -c src/alembic.ini upgrade head
exec uvicorn src.main:app --host 0.0.0.0 --port 8000