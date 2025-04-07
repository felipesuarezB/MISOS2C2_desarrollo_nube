# Plan de Pruebas de Carga - API Rising Stars Showcase

## Índice
1. [Introducción](#introducción)
2. [Herramienta de Pruebas](#herramienta-de-pruebas)
3. [Entorno de Pruebas](#entorno-de-pruebas)
4. [Criterios de Aceptación](#criterios-de-aceptación)
5. [Topología de Prueba](#topología-de-prueba)
6. [Escenarios de Prueba](#escenarios-de-prueba)
7. [Parámetros de Configuración](#parámetros-de-configuración)
8. [Resultados Preliminares](#resultados-preliminares)
9. [Scripts de Prueba](#scripts-de-prueba)

## Introducción

Este documento presenta el plan de pruebas de carga para la API de Rising Stars Showcase, un sistema que permite a jugadores subir y compartir videos, así como votar por ellos. El objetivo principal es dimensionar la capacidad de la aplicación y su infraestructura de soporte mediante pruebas de estrés que permitan medir tiempos de respuesta, capacidad de procesamiento y utilización de recursos bajo diferentes cargas de usuarios.

## Herramienta de Pruebas

Para ejecutar las pruebas de carga, hemos seleccionado **Apache JMeter** como herramienta principal por las siguientes razones:

- Es una herramienta de código abierto y multiplataforma
- Soporta pruebas de diferentes protocolos, incluyendo HTTP/HTTPS
- Permite simular múltiples usuarios concurrentes mediante hilos
- Ofrece interfaz gráfica para el diseño de pruebas y visualización de resultados
- Tiene capacidad para generar informes detallados
- Permite la integración con sistemas de monitoreo
- Soporta autenticación y manejo de tokens JWT, necesarios para esta API

JMeter nos permitirá simular las cargas de usuarios y medir las tres métricas fundamentales: capacidad de procesamiento (throughput), tiempos de respuesta y, con complementos adicionales, la utilización de recursos.

## Entorno de Pruebas

### Características de la Infraestructura

La aplicación está desplegada en AWS y utiliza los siguientes servicios y recursos:

- **Backend**: Flask (Python) desplegado en contenedores Docker
- **Base de datos**: PostgreSQL
- **Almacenamiento**: Amazon S3 para los videos
- **Autenticación**: JWT (JSON Web Tokens)

### Limitaciones de la Infraestructura

- El entorno de producción actual tiene recursos limitados que podrían afectar el rendimiento bajo carga
- El servicio S3 tiene límites de tasa de solicitudes
- La base de datos PostgreSQL comparte recursos con otras aplicaciones

### Infraestructura de Pruebas

Para ejecutar las pruebas de carga, utilizaremos una instancia EC2 en AWS con las siguientes características:

- **Tipo de instancia**: m5.large (2 vCPU, 8 GB RAM)
- **Región**: us-east-1 (misma región donde está desplegada la aplicación)
- **Sistema operativo**: Amazon Linux 2
- **Almacenamiento**: 20 GB SSD gp2

La elección de una instancia m5.large se justifica por:
- Capacidad suficiente para simular hasta 500 usuarios concurrentes
- Memoria adecuada para JMeter y almacenamiento de resultados
- Buena relación costo-rendimiento
- Proximidad de red al entorno de producción

## Criterios de Aceptación

Los siguientes criterios determinarán el éxito de las pruebas de carga:

### Tiempos de Respuesta
- **Objetivo**: Tiempo de respuesta promedio < 500ms para todas las operaciones de la API
- **Límite**: Tiempo de respuesta máximo < 2000ms para el 95% de las solicitudes
- **Error**: Tiempo de respuesta > 5000ms se considera inaceptable

### Capacidad de Procesamiento (Throughput)
- **Objetivo**: > 100 transacciones por segundo para operaciones de lectura
- **Objetivo**: > 20 transacciones por segundo para operaciones de escritura
- **Error**: Caída de throughput > 50% bajo carga incremental

### Utilización de Recursos
- **CPU**: < 80% de utilización sostenida
- **Memoria**: < 85% de utilización
- **Base de datos**: < 75% de utilización de conexiones
- **Error**: Saturación de cualquier recurso que cause degradación de servicio

### Tasa de Error
- **Objetivo**: < 1% de errores en condiciones normales
- **Límite**: < 5% de errores bajo carga máxima
- **Error**: > 10% de tasa de error en cualquier escenario

## Topología de Prueba

La topología de las pruebas se estructura de la siguiente manera:

```
+------------------+        +------------------+        +------------------+
|                  |        |                  |        |                  |
|  Cliente JMeter  +------->+  API Backend     +------->+ Base de Datos    |
|  (EC2 m5.large)  |   HTTP |  (Flask/Docker)  |   SQL  | (PostgreSQL)     |
|                  |   JWT  |                  |        |                  |
+------------------+        +--------+---------+        +------------------+
                                     |
                                     | S3 API
                                     v
                            +------------------+
                            |                  |
                            |  Amazon S3       |
                            |  (Videos)        |
                            |                  |
                            +------------------+
```

El flujo de la prueba incluye:
1. JMeter genera carga simulando usuarios concurrentes desde la instancia EC2
2. Las solicitudes HTTP son enviadas a la API con autenticación JWT
3. La API procesa las solicitudes y realiza operaciones en la base de datos PostgreSQL
4. Para operaciones que involucran videos, la API interactúa con Amazon S3
5. JMeter registra las métricas de rendimiento y tiempos de respuesta

## Escenarios de Prueba

Hemos identificado dos escenarios clave para las pruebas de carga, basados en las rutas críticas de usuario:

### Escenario 1: Flujo de Autenticación y Visualización de Videos (Capa Web)

Este escenario representa el flujo típico de un usuario que accede a la plataforma, se autentica y visualiza videos.

**Diagrama de Flujo:**
```
Inicio → Registro (POST /api/auth/signup) → Login (POST /api/auth/login) → 
Listar Videos Públicos (GET /api/public/videos) → Ver Video Individual (GET /api/videos/{id}) → Fin
```

**Variables y Datos:**
- Credenciales de usuario aleatorias para registro
- Credenciales válidas para login
- IDs de videos existentes para consultas

**Métricas a Medir:**
- Tiempo de respuesta por endpoint
- Throughput global y por endpoint
- Tasa de error
- Utilización de recursos (CPU, memoria, red)

### Escenario 2: Subida y Votación de Videos (Procesamiento por Lotes)

Este escenario representa operaciones intensivas de escritura, incluyendo la subida de videos y su procesamiento.

**Diagrama de Flujo:**
```
Inicio → Login (POST /api/auth/login) → Subir Video (POST /api/videos/upload) → 
Listar Videos del Usuario (GET /api/videos) → Votar Video (POST /api/public/videos/{id}/vote) → Fin
```

**Variables y Datos:**
- Credenciales válidas para login
- Archivos de video MP4 de diferentes tamaños (1MB, 5MB, 10MB)
- IDs de videos para votación

**Métricas a Medir:**
- Tiempo de respuesta de subida y procesamiento
- Throughput de operaciones de escritura
- Utilización de S3 (tiempo de carga/descarga)
- Utilización de recursos (CPU, memoria, red, disco)

## Parámetros de Configuración

### Configuración de JMeter

- **Grupos de Hilos**: Configuración para simular usuarios concurrentes
  - Usuarios iniciales: 10
  - Incremento gradual: 10, 50, 100, 250, 500 usuarios
  - Tiempo de aceleración: 60 segundos por nivel
  - Duración de la prueba: 5 minutos por nivel

- **Temporizadores**:
  - Tiempo de espera entre solicitudes: 1-3 segundos (distribución gaussiana)
  - Tiempo de pensamiento del usuario: 2-5 segundos

- **Controladores**:
  - Controlador lógico para secuencias de solicitudes
  - Controlador de transacciones para medir tiempos completos de escenarios

- **Listeners**:
  - Informe agregado para métricas generales
  - Gráficos de resultados para análisis visual
  - Backend Listener para exportar a InfluxDB

### Monitoreo Adicional

- **CloudWatch Metrics**:
  - CPU, memoria y utilización de disco de instancias EC2
  - Métricas de RDS PostgreSQL
  - Métricas de S3 (solicitudes, latencia)

- **InfluxDB + Grafana**:
  - Dashboard personalizado para visualizar métricas en tiempo real
  - Correlación entre métricas de JMeter y recursos

## Resultados Preliminares

A continuación, se presentan estimaciones preliminares basadas en análisis inicial:

### Tabla Resumen de Escenarios

| Escenario | Usuarios | Throughput (tr/s) | Tiempo Resp. Medio (ms) | Tasa Error (%) | CPU (%) | Memoria (%) |
|-----------|----------|-------------------|-------------------------|----------------|---------|-------------|
| Auth+Ver  | 10       | 15                | 250                     | 0              | 20      | 30          |
| Auth+Ver  | 50       | 60                | 350                     | 0.5            | 45      | 50          |
| Auth+Ver  | 100      | 95                | 450                     | 1.2            | 65      | 60          |
| Auth+Ver  | 250      | 120               | 750                     | 3.5            | 85      | 75          |
| Auth+Ver  | 500      | 90                | 1500                    | 8.0            | 95      | 90          |
| Subir+Votar | 10     | 5                 | 500                     | 0              | 30      | 35          |
| Subir+Votar | 50     | 18                | 850                     | 1.0            | 60      | 55          |
| Subir+Votar | 100    | 25                | 1200                    | 2.5            | 80      | 70          |
| Subir+Votar | 250    | 22                | 2500                    | 7.0            | 95      | 90          |
| Subir+Votar | 500    | 15                | 4500                    | 15.0           | 100     | 95          |

### Gráficos Preliminares

#### Throughput vs. Usuarios
<img width="599" alt="Screenshot 2025-04-06 at 8 34 44 PM" src="https://github.com/user-attachments/assets/80373040-6586-4fc9-a5cc-1734dd777e41" />

#### Tiempo de Respuesta vs. Carga
<img width="634" alt="Screenshot 2025-04-06 at 8 34 54 PM" src="https://github.com/user-attachments/assets/d3b2e044-3ae7-4633-991d-9b76a956e770" />


#### Utilización de CPU vs. Usuarios
<img width="642" alt="Screenshot 2025-04-06 at 8 35 03 PM" src="https://github.com/user-attachments/assets/44bfe866-3393-4913-b792-39b9204fa810" />


## Scripts de Prueba

A continuación, se presenta un ejemplo básico del script de prueba en JMeter (formato XML) que se utilizará para el Escenario 1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.5">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Plan de Prueba API Rising Stars">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Grupo de Usuarios">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">-1</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">${__P(users,10)}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">${__P(rampup,60)}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">${__P(duration,300)}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
      </ThreadGroup>
      <hashTree>
        <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager">
          <collectionProp name="HeaderManager.headers">
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Content-Type</stringProp>
              <stringProp name="Header.value">application/json</stringProp>
            </elementProp>
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Accept</stringProp>
              <stringProp name="Header.value">application/json</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree/>
        <!-- Más configuraciones específicas de los endpoints se agregarán en la implementación -->
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

Para el Escenario 2, también se desarrollará un script similar que incluirá la carga de archivos para simular la subida de videos.

Para ejecutar las pruebas utilizando Apache Bench como alternativa rápida, se utilizarán comandos como:

```bash
# Ejemplo para probar el endpoint de login
ab -n 1000 -c 100 -T 'application/json' -p login_data.json http://api-url/api/auth/login

# Ejemplo para probar listar videos (con token)
ab -n 1000 -c 100 -H "Authorization: Bearer TOKEN" http://api-url/api/videos
``` 
