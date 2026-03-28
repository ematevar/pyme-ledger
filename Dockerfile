FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y activar salida inmediata a consola
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema (por si Beancount las requiere)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Exponer el puerto de Django
EXPOSE 8000

# Comando para arrancar el servidor de desarrollo
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
