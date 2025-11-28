# 1. Tahap Build (Stage 1: untuk menginstal dependensi)
# Menggunakan base image yang sama (3.11-slim)
FROM python:3.11-slim AS builder

# Setel environment variables untuk efisiensi
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tetapkan direktori kerja
WORKDIR /usr/src/app

# Salin dan instal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Tahap Production (Stage 2: Image final yang lebih ramping)
# Menggunakan base image python:3.11-slim yang bersih
FROM python:3.11-slim

# Setel environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tetapkan direktori kerja
WORKDIR /usr/src/app

# Salin hanya dependensi yang sudah diinstal dari tahap 'builder'
# Ini memastikan image final sekecil mungkin
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Salin kode aplikasi, templates, dan file lain yang diperlukan
COPY . .

RUN chmod +x /usr/src/app/entrypoint.sh

# Ekspos port tempat Gunicorn akan berjalan (default-nya 8000)
EXPOSE 8000

# Perintah menjalankan aplikasi dengan Gunicorn
# Asumsi: Anda memiliki objek Flask bernama 'app' di dalam app.py
# -w 4: 4 worker (sesuaikan dengan CPU klaster Anda)
# -b 0.0.0.0:8000: bind ke semua interface di port 8000
# CMD gunicorn -w 4 -b 0.0.0.0:"$PORT" app:app

ENTRYPOINT ["./entrypoint.sh"]