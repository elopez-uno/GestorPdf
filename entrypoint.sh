#!/bin/sh

set -e

echo "Inicializando base de datos y datos por defecto..."
flask init-data

echo "Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:create_app()"
