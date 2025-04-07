# Imagen base de Python
FROM python:3.12-slim

# Configuración del directorio de trabajo
WORKDIR /app/src

# Instalar dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno de la aplicación
ENV ENVIRONMENT=production \
    DB_USER=dbuser \
    DB_PASSWORD=mypass \
    DB_HOST=172.18.0.2 \
    DB_PORT=5432 \
    DB_NAME=db \
    JWT_SECRET_KEY=6a037737-af5d-4b93-a9e5-dd8fec11221b \
    FLASK_APP=app.py \
    PYTHONPATH="/app"


# Copiar archivos de dependencias primero para optimizar el caché de Docker
COPY Pipfile Pipfile.lock ./

# Actualizar pip y instalar dependencias de la aplicación
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir pipenv \
    && pipenv install --system --deploy

# Copiar el código fuente de la aplicación dentro de la carpeta src
COPY ./src ./src

# Exponer el puerto 8081 para la aplicación Flask
EXPOSE 8081

# Comando de ejecución de Flask (ajustar la ruta a asgi)
CMD ["uvicorn", "asgi:app", "--host", "0.0.0.0", "--port", "8081"]
