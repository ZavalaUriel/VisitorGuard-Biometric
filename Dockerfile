# Dockerfile para VisitorGuard Backend
FROM python:3.12-slim

# Instalar dependencias del sistema para OpenCV y librerías de reconocimiento facial
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY backend/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY backend/ .

# Crear directorios necesarios
RUN mkdir -p /app/temp /app/uploads/visits

# Exponer el puerto de la aplicación
EXPOSE 5000

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
