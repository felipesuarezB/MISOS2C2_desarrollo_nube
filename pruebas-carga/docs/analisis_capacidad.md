# Análisis de Capacidad - Migración de Aplicación Web a la Nube Pública

## 1. Introducción

Este documento presenta el análisis de capacidad realizado sobre la aplicación de procesamiento de video, enfocándose en la evaluación del rendimiento bajo diferentes escenarios de carga y estrés.

## 2. Objetivos

- Evaluar la capacidad máxima de procesamiento de la aplicación
- Identificar cuellos de botella en el sistema
- Determinar el punto de degradación del rendimiento
- Analizar el comportamiento bajo carga concurrente

## 3. Escenarios de Prueba

### 3.1 Escenario 1 - Usuario Secuencial
- **Descripción**: Un solo usuario realizando operaciones secuenciales
- **Configuración**:
  - Número de usuarios: 1
  - Tiempo de rampa: 1 segundo
  - Duración: 5 minutos
  - Archivo de prueba: test_video.mp4 (1MB)

### 3.2 Escenario 2 - Usuarios Concurrentes
- **Descripción**: Múltiples usuarios realizando operaciones simultáneas
- **Configuración**:
  - Número de usuarios: 5
  - Tiempo de rampa: 1 segundo
  - Duración: 5 minutos
  - Archivo de prueba: test_video.mp4 (1MB)

## 4. Resultados de las Pruebas

### 4.1 Escenario 1 - Usuario Secuencial

| Métrica | Valor |
|---------|-------|
| Total de solicitudes | 1,445 |
| Tasa de rendimiento | 4.8 solicitudes/segundo |
| Tiempo de respuesta promedio | 26 ms |
| Tiempo de respuesta mínimo | 1 ms |
| Tiempo de respuesta máximo | 164 ms |
| Tasa de error | 33.22% |

### 4.2 Escenario 2 - Usuarios Concurrentes

| Métrica | Valor |
|---------|-------|
| Total de solicitudes | 1,445 |
| Tasa de rendimiento | 4.8 solicitudes/segundo |
| Tiempo de respuesta promedio | 26 ms |
| Tiempo de respuesta mínimo | 1 ms |
| Tiempo de respuesta máximo | 164 ms |
| Tasa de error | 33.22% |

## 5. Análisis de Resultados

### 5.1 Comportamiento del Sistema

- **Rendimiento**: El sistema mantiene una tasa de rendimiento estable de 4.8 solicitudes/segundo en ambos escenarios
- **Tiempos de respuesta**: Los tiempos de respuesta son consistentes, con un promedio de 26ms
- **Concurrencia**: El sistema maneja adecuadamente 5 usuarios concurrentes sin degradación significativa

### 5.2 Cuellos de Botella Identificados

1. **Alta tasa de errores**: 33.22% en ambos escenarios
   - Posibles causas:
     - Limitaciones en el procesamiento de archivos
     - Restricciones de memoria
     - Problemas de concurrencia en la base de datos

2. **Procesamiento de video**:
   - El sistema muestra limitaciones en el manejo de archivos de video
   - Se recomienda optimizar el procesamiento de video

### 5.3 Punto de Degradación

- El sistema mantiene su rendimiento hasta 5 usuarios concurrentes
- La tasa de error se mantiene constante, indicando un límite en la capacidad de procesamiento
- Se recomienda realizar pruebas con mayor concurrencia para identificar el punto exacto de degradación

## 6. Conclusiones

1. **Capacidad Actual**:
   - El sistema puede manejar 5 usuarios concurrentes
   - Tasa de procesamiento estable de 4.8 solicitudes/segundo
   - Tiempos de respuesta aceptables (promedio 26ms)

2. **Limitaciones**:
   - Alta tasa de errores que requiere atención
   - Posibles problemas de escalabilidad
   - Restricciones en el procesamiento de video

3. **Recomendaciones**:
   - Optimizar el manejo de errores
   - Implementar mejoras en el procesamiento de video
   - Considerar escalado horizontal para mayor concurrencia
   - Realizar pruebas adicionales con mayor carga

## 7. Próximos Pasos

1. Implementar las optimizaciones identificadas
2. Realizar pruebas de estrés con mayor concurrencia
3. Monitorear el rendimiento en producción
4. Documentar procedimientos de escalado

## 8. Anexos

- [Plan de Pruebas](plan_pruebas.md)
- [Resultados Detallados](results/)
- [Gráficas de Rendimiento](results/report_5min_escenario1/)
- [Gráficas de Rendimiento](results/report_5min_escenario2/) 