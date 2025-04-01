# Imagen Docker base Python.
FROM python:3.12

# Variables de entorno de la aplicación.
ENV ENVIRONMENT=production
ENV DB_USER=dbuser
ENV DB_PASSWORD=mypass
ENV DB_HOST=172.18.0.2
ENV DB_PORT=5432
ENV DB_NAME=db
ENV JWT_SECRET_KEY=6a037737-af5d-4b93-a9e5-dd8fec11221b

# Instalar dependencias de la aplicación.
COPY Pipfile Pipfile.lock ./

RUN python -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --system --deploy

# Directorio de instalación.
WORKDIR /app

# Copiar código fuente de la aplicación.
COPY ./src .

# Set environment variables
ENV FLASK_APP="apirest"
ENV FLASK_DEBUG=1

# Expose port 5000 for the Flask development server to listen on
EXPOSE 5000

# Define the command to run the Flask development server
CMD ["flask", "run", "--host=0.0.0.0"]