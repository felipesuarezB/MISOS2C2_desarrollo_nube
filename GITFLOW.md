# Guía GitFlow para el Proyecto

Este documento describe el modelo de ramificación GitFlow que utilizamos en nuestro proyecto, junto con las prácticas de CI/CD implementadas.

## Estructura de ramas

El proyecto sigue el modelo GitFlow con las siguientes ramas principales:

- **main**: Contiene el código en producción. Todos los cambios en esta rama se despliegan automáticamente en el entorno de producción.
- **develop**: Rama principal de desarrollo. Integra todas las características completadas para la próxima versión.
- **feature/**: Ramas para desarrollar nuevas características. Se crean a partir de `develop` y se fusionan de vuelta a `develop`.
- **release/**: Ramas para preparar una nueva versión. Se crean a partir de `develop` y se fusionan a `main` y `develop`.
- **hotfix/**: Ramas para correcciones urgentes en producción. Se crean a partir de `main` y se fusionan a `main` y `develop`.

## Flujo de trabajo

### Desarrollar una nueva característica

```bash
# Crear una rama feature desde develop
git checkout develop
git pull
git checkout -b feature/nombre-caracteristica

# Desarrollar y hacer commits
git add .
git commit -m "Descripción del cambio"

# Actualizar con cambios de develop regularmente
git checkout develop
git pull
git checkout feature/nombre-caracteristica
git merge develop

# Cuando la característica esté completa, crear un Pull Request a develop
```

### Crear una versión de lanzamiento

```bash
# Crear una rama release desde develop
git checkout develop
git pull
git checkout -b release/vX.Y.Z

# Hacer ajustes finales, correcciones de bugs, etc.
git add .
git commit -m "Ajustes para release vX.Y.Z"

# Cuando la versión esté lista, fusionar a main y develop
# Esto generalmente se hace mediante Pull Requests
```

### Resolver un problema urgente en producción

```bash
# Crear una rama hotfix desde main
git checkout main
git pull
git checkout -b hotfix/descripcion-problema

# Hacer la corrección
git add .
git commit -m "Corrección del problema"

# Crear Pull Requests a main y develop
```

## Integración Continua (CI)

- Cada Pull Request activa automáticamente pruebas y análisis de código.
- El código debe pasar todas las pruebas antes de ser fusionado.
- Los Pull Requests a `develop`, `release/*` y `main` requieren revisión de código.

## Despliegue Continuo (CD)

- Cambios en `develop` se despliegan automáticamente en el entorno de desarrollo.
- Cambios en `release/*` se despliegan automáticamente en el entorno de staging.
- Cambios en `main` se despliegan automáticamente en el entorno de producción.

## Etiquetas y versiones

- Al fusionar una rama `release/` a `main`, se debe crear una etiqueta de versión:

```bash
git checkout main
git pull
git tag -a vX.Y.Z -m "Versión X.Y.Z"
git push origin vX.Y.Z
```

## Convenciones de commits

Utilizamos el formato [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<alcance>): <descripción>

[cuerpo opcional]

[pie opcional]
```

Tipos comunes:
- feat: Nueva característica
- fix: Corrección de errores
- docs: Cambios en documentación
- style: Cambios que no afectan el funcionamiento (formato, espacios, etc.)
- refactor: Cambios de código que no son nuevas características ni correcciones
- test: Adición o corrección de pruebas
- chore: Cambios en el proceso de construcción o herramientas auxiliares 