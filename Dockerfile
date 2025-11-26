# Gunakan base image Python
FROM python:3.11-slim

# Set working directory di container
WORKDIR /app

# Salin file requirements dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh project ke container
COPY . .

# Expose port Flask (default 5000)
EXPOSE 5000

# Jalankan Flask app
CMD ["python", "app.py"]
