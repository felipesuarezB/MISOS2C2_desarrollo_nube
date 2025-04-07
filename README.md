# MISW4201-202511-Backend-Grupo05

Proyecto del servicio de backend 'nba-api'.

## Índice

1. [Estructura](#estructura)
2. [Ejecución](#ejecución)
3. [Uso](#uso)
4. [Pruebas](#pruebas)
5. [Reporte](#reporte)
6. [Despliegue](#despliegue)
7. [Autores](#autores)

## Estructura

```txt
  /
    ├── src/ # Código de la aplicación backend.
    ├── tests/ # Carpeta con los tests de la aplicación.
    ├── Dockerfile # Archivo para la creación de imagen Docker.
    ├── README.md # Usted está aquí.
    └── Pipfile # Archivo de declaración de dependencias del proyecto.
```

## Ejecución

Primero se debe instalar pipenv:

```bash
  pip install pipenv
```

Luego, instale las dependencias del proyecto:

```bash
  pipenv install
```

Luego, ejecute el proyecto en modo local para pruebas:

```bash
  pipenv run flask -e .env.test --app src/app run -h 0.0.0.0 -p 8081 --debug
```

Para ejecutarlo como Docker container, primero se debe construir la imagen con el siguiente comando:

```bash
  docker build -t nba-api:1.0 .
```

Luego se puede arrancar un container en modo test con el siguiente comando:

```bash
  docker run -d -p 8081:8081 -e PORT=8081 -e ENVIRONMENT=test -e DB_HOST=memory -e JWT_SECRET_KEY=123 nba-api:1.0
```

Nota: esto sólo levanta el componente relacionado a la nba-api



Para ejecutar Docker compose con los componentes: nba-api, redis, db, celery:

1. Agregar variables de entorno al archivo `.env`

2. Ejecutar el comando:

```bash
  docker compose up
```

## Uso

Para consumir la API siga la definición de los endpoints en la ruta `/swagger-ui`. Para descargar la definición de las APIs en formato OpenAPI abra la ruta `/api-spec.json`.

## Autores

- Felipe Suárez - f.suarezb@uniandes.edu.co
- Andy Yair Bolaño Castilla - a.bolanoc@uniandes.edu.co
- Santiago Gómez Perdomo - s.gomezp2345@uniandes.edu.co
- Javier Hernández - je.hernandezc1@uniandes.edu.co
