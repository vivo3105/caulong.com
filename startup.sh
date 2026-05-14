#!/bin/bash
# Azure App Service startup script

cd /home/site/wwwroot

echo "=== CauLong.com startup ==="
echo "Working dir: $(pwd)"
echo "Python: $(python --version)"

# Always run seed (idempotent — won't duplicate data)
echo "Running seed..."
python seed.py

# Start gunicorn
echo "Starting gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout=600 --workers=2 --log-level=info run:app
