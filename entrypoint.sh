#!/bin/sh
# Skrip ini memastikan Gunicorn dijalankan dengan port yang disediakan oleh Cloud Run.

# Cloud Run menyediakan port melalui variabel lingkungan PORT
if [ -z "$PORT" ]; then
    # Jika PORT tidak disetel (misalnya saat pengujian lokal)
    export PORT=8080
fi

# Jalankan Gunicorn, bind ke 0.0.0.0 dan $PORT
exec python -m gunicorn -w 4 -b 0.0.0.0:"$PORT" "app:app"