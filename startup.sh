#!/bin/bash
# Azure App Service startup script

# Run database seed on first deploy (creates tables + sample data)
if [ ! -f /home/caulong.db ]; then
    echo "Database not found — running seed..."
    python seed.py
fi

# Start gunicorn on the port Azure expects (8000)
gunicorn --bind=0.0.0.0:8000 --timeout=600 --workers=2 --log-level=info run:app
