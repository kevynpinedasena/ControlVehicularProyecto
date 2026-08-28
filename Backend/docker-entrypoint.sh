#!/bin/sh
set -e

echo "Aplicando migraciones de base de datos..."
alembic upgrade head

echo "Sembrando datos iniciales (roles y super administrador)..."
python -m app.infrastructure.database.seed

echo "Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
