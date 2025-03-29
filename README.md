# MISW4201-202511-Backend-Grupo05

Proyecto del servicio de backend 'backend-app-enforma'.

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

Primero, instale las dependencias del proyecto:

```bash
  pipenv install
```

Luego, ejecute el proyecto en modo local para pruebas:

```bash
  pipenv run flask -e .env.test --app src/app run -h 0.0.0.0 -p 8081 --debug
```

O ejecute el proyecto en modo productivo:

```bash
  pipenv run flask --app src/app run -h 0.0.0.0 -p 8081
```

Para ejecutarlo como Docker container, primero se debe construir la imagen con el siguiente comando:

```bash
  docker build -t backend-app-enforma:1.0 .
```

Luego se puede arrancar un container en modo test con el siguiente comando:

```bash
  docker run -d -p 8081:8081 -e PORT=8081 -e ENVIRONMENT=test -e DB_HOST=memory -e JWT_SECRET_KEY=123 backend-app-enforma:1.0
```

## Uso

Para consumir la API siga la definición de los endpoints en la ruta `/swagger-ui`. Para descargar la definición de las APIs en formato OpenAPI abra la ruta `/api-spec.json`.

## Pruebas

Los tests unitarios los puede ejecutar con el siguiente comando:

```bash
  pytest --cov-fail-under=70 --cov=src --cov-report=html
```

## Reporte

- Ingrese a [Jenkins](http://157.253.238.75:8080/jenkins-misovirtual/).
- Busque el repositorio MISW4201-202511-Backend-Grupo05.
- En la barra lateral izquierda, ubique los espacios de GitInspector y Coverage report. Al abrirlos, en la parte superior derecha utilice el enlace Zip para descargarlos y visualizarlos correctamente.

## Despliegue

Para el despliegue en Heroku se deben ejecutar los siguientes comandos:

```bash
  heroku login
  heroku container:login
  heroku stack:set container --app <heorku-app-name>

  heroku container:push web --app <heorku-app-name>
  heroku container:release web --app <heorku-app-name>
```

Para leer logs en Heroku ejecutar el siguiente comando:

```bash
  heroku logs --app <heorku-app-name> --tail
```

Para reiniciar la app en Heroku ejecutar el siguiente comando:

```bash
  heroku restart --app <heorku-app-name>
```

## Autores

- Felipe Suárez - f.suarezb@uniandes.edu.co
- Andy Yair Bolaño Castilla - a.bolanoc@uniandes.edu.co
- Santiago Gómez Perdomo - s.gomezp2345@uniandes.edu.co
- Javier Hernández - je.hernandezc1@uniandes.edu.co
