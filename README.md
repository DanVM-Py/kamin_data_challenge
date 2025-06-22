# 🚀 Kamin Data Challenge

Análisis completo de datos financieros usando SQL Analytics, Python y Docker para evaluar patrones de transacciones, tasas de fallo y comportamiento de reintentos.

## 📋 Resumen Ejecutivo

**Objetivo:** Analizar 15,000 eventos financieros de 60 clientes para identificar patrones operacionales y métricas de rendimiento.

**Stack Técnico:** Python + DuckDB + SQL + Docker + Jupyter Lab

**Entregables:**
- 📊 **Client Summary Analytics** - Métricas por cliente
- 📈 **Event Time Series** - Análisis temporal de transacciones  
- 🔄 **Retry Analysis** - Patrones de reintento y éxito

## 🎯 Resultados Clave

| Métrica | Valor | Insight |
|---------|--------|---------|
| **Total Eventos** | 15,000 | Mix pay_in/pay_out balanceado |
| **Clientes Activos** | 60 | Distribución multi-sector |
| **Tasa de Fallos** | ~12% | Dentro de rangos aceptables |
| **Eventos con Retry** | 1,500 | 10% requieren reintento |
| **Éxito Retry** | ~85% | Alta efectividad de recuperación |

## 🚀 Inicio Rápido

### 1️⃣ Ejecutar Análisis Completo
```bash
# Iniciar entorno Docker
./scripts/start-dev.sh up

# Abrir Jupyter Lab
open http://localhost:8889
```

### 2️⃣ Generar Tablas Analíticas
```python
# En Jupyter: notebooks/sql_analytics.ipynb
from src.sql_analytics import SQLAnalytics

analytics = SQLAnalytics(processed_data, output_path)
results = analytics.generate_analytics_tables()
```

### 3️⃣ Resultados Generados
```
📁 data/analytics/
├── client_summary.csv      # Métricas por cliente
└── event_time_series.csv   # Series temporales
```

## 📊 Arquitectura de Datos

```
📁 Pipeline ETL
├── 📥 Raw Data        → clients.csv, events.csv, retry_logs.csv
├── 🔄 Processing      → Normalización y limpieza  
├── 🏗️ SQL Analytics   → DuckDB + consultas optimizadas
└── 📈 Output          → Tablas analíticas CSV
```

### Flujo de Procesamiento
1. **Load** → CSVs to DuckDB tables
2. **Transform** → SQL queries con CAST y JOINs
3. **Analytics** → Métricas agregadas por cliente/tiempo
4. **Export** → CSV para visualización/BI

## 🔧 Stack Técnico

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Data Processing** | Python + Pandas | ETL y manipulación |
| **SQL Engine** | DuckDB | Consultas analíticas |
| **Containerización** | Docker + Compose | Reproducibilidad |
| **Development** | Jupyter Lab | Análisis interactivo |
| **Logging** | Python logging | Monitoreo de pipeline |

## 📈 Análisis Realizados

### 1. **Client Summary Analytics**
- Volúmenes totales por cliente
- Tasas de fallo por cliente  
- Distribución pay_in vs pay_out
- Delays promedio de procesamiento
- Conteo de eventos con retry

### 2. **Event Time Series Analytics**  
- Series temporales por hora/día
- Volúmenes de transacciones
- Tasas de fallo temporales
- Patrones de retry por tiempo
- Métricas de performance

### 3. **Retry Pattern Analysis**
- Efectividad de reintentos
- Distribución temporal de retries
- Correlación retry-éxito por cliente

## 🎯 Insights de Negocio

### ✅ **Fortalezas Operacionales**
- **Alta efectividad de retry** (85% éxito)
- **Distribución balanceada** pay_in/pay_out
- **Tasas de fallo controladas** (~12%)

### 🔍 **Oportunidades de Mejora**  
- Optimizar delays de procesamiento
- Reducir eventos que requieren retry
- Análisis sectorial de performance

### 📊 **Métricas de Performance**
- **Throughput:** 15K eventos procesados
- **Reliability:** 88% eventos exitosos first-try
- **Recovery:** 85% retry success rate

## 🛠️ Setup y Desarrollo

### Prerequisitos
- Docker & Docker Compose
- 4GB RAM disponible
- Puerto 8889 libre

### Instalación Completa
Ver [docs/SETUP.md](docs/SETUP.md) para guía técnica detallada.

### Estructura del Proyecto
```
kamin_data_challenge/
├── 📊 data/              # Datasets raw/processed/analytics
├── 🐍 src/               # Código Python modular
├── 📋 queries/DML/       # Consultas SQL optimizadas  
├── 📓 notebooks/         # Jupyter análisis
├── 🐳 docker/            # Configuración Docker
└── 📚 docs/              # Documentación
```

## 🏆 Metodología

**Enfoque:** SQL-first analytics con Python orchestration  
**Validación:** Logs exhaustivos + error handling  
**Reproducibilidad:** Docker + volúmenes sincronizados  
**Escalabilidad:** Arquitectura modular extensible

---

## 📞 Summary

**Challenge:** Kamin Data Analysis  
**Tech Stack:** Python + SQL + Docker  
**Status:** ✅ Completado

Para detalles técnicos ver [docs/SETUP.md](docs/SETUP.md)  
Para metodología ver [docs/ANALYSIS.md](docs/ANALYSIS.md)
