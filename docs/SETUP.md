# 🐳 Setup Técnico - Kamin Data Challenge

Guía completa para configurar el entorno Docker y ejecutar el análisis de datos financieros.

## 🚀 Inicio Rápido

### Opción 1: Script automatizado (Recomendado)
```bash
# Iniciar Jupyter Lab
./scripts/start-dev.sh up

# Ver en navegador: http://localhost:8889
```

### Opción 2: Docker Compose manual
```bash
# Iniciar contenedor
docker-compose up --build

# Detener contenedor  
docker-compose down
```

## 📋 Comandos Disponibles

El script `./scripts/start-dev.sh` incluye varios comandos útiles:

```bash
./scripts/start-dev.sh up      # Iniciar Jupyter Lab (puerto 8889)
./scripts/start-dev.sh down    # Detener contenedores
./scripts/start-dev.sh build   # Reconstruir imagen Docker
./scripts/start-dev.sh shell   # Abrir shell interactivo
./scripts/start-dev.sh clean   # Limpiar contenedores e imágenes
./scripts/start-dev.sh logs    # Ver logs del contenedor
./scripts/start-dev.sh help    # Mostrar ayuda
```

## 🔧 Configuración del Entorno

### Contenedor Principal
- **Base**: Python 3.9-slim
- **Puerto**: 8889 (Jupyter Lab) - *Evita conflictos con puerto 8888*
- **Usuario**: kamin (no-root para seguridad)
- **Directorio de trabajo**: `/app`

### Dependencias Incluidas
- **Análisis de datos**: pandas, numpy, duckdb
- **Visualización**: matplotlib, seaborn, plotly
- **Desarrollo**: Jupyter Lab, IPython widgets
- **Herramientas**: black, flake8, pytest

### Volúmenes Montados
```
./src        → /app/src        (código fuente)
./notebooks  → /app/notebooks  (notebooks Jupyter)
./data       → /app/data       (datasets)
./queries    → /app/queries    (consultas SQL)
```

## 📊 Notebooks Disponibles

### `sql_analytics.ipynb`
Notebook principal del data challenge que incluye:
- ✅ Configuración de SQLAnalytics
- 🧪 Generación de tablas analíticas
- 📈 Verificación de resultados
- 🎮 Pipeline completo de análisis

### Uso del Notebook
1. Ejecutar `./scripts/start-dev.sh up`
2. Abrir http://localhost:8889
3. Navegar a `notebooks/sql_analytics.ipynb`
4. Ejecutar las celdas secuencialmente

## 🛠️ Desarrollo

### Estructura del Proyecto
```
kamin_data_challenge/
├── Dockerfile                 # Definición del contenedor
├── docker-compose.yml         # Orquestación de servicios
├── scripts/start-dev.sh      # Script de desarrollo
├── requirements.txt          # Dependencias Python
├── src/                      # Código fuente
│   ├── load.py              # Funciones de carga
│   ├── transform.py         # Funciones de transformación
│   └── sql_analytics.py     # Motor SQL Analytics
├── queries/DML/             # Consultas SQL optimizadas
│   ├── client_summary.sql   # Análisis por cliente
│   └── event_time_series.sql # Series temporales
├── notebooks/               # Notebooks Jupyter
│   └── sql_analytics.ipynb  # Análisis principal
└── data/                    # Datasets
    ├── raw/                 # Datos originales
    ├── processed/           # Datos procesados
    └── analytics/           # Resultados analíticos
```

### Desarrollo en Tiempo Real
Los cambios en el código fuente se reflejan inmediatamente en el contenedor gracias a los volúmenes montados:

- Edita archivos en `./src/` → Cambios disponibles en `/app/src/`
- Crea notebooks en `./notebooks/` → Accesibles en Jupyter Lab
- Modifica consultas en `./queries/` → Disponibles inmediatamente
- Agrega datos en `./data/` → Disponibles para análisis

## 🔍 Funciones Principales

### SQL Analytics Engine (`src/sql_analytics.py`)
```python
from src.sql_analytics import SQLAnalytics

# Inicializar motor analítico
analytics = SQLAnalytics(processed_data_path, output_path)

# Generar todas las tablas
results = analytics.generate_analytics_tables()

# O crear tablas específicas
analytics.create_client_summary()
analytics.create_event_time_series()
```

### Carga de Datos (`src/load.py`)
```python
from load import load_csv

# Cargar un CSV específico
df = load_csv('clients.csv', base_path=DATA_RAW)
```

### Transformaciones (`src/transform.py`)
```python
from transform import normalize_retry_logs_metadata

# Normalizar retry logs
df_clean = normalize_retry_logs_metadata(df_retries)
```

## 📝 Ejemplos de Uso

### Shell Interactivo
```bash
# Acceder al shell del contenedor
./scripts/start-dev.sh shell

# Dentro del contenedor
python -c "import pandas as pd; print('✅ Pandas disponible')"
python src/sql_analytics.py  # Ejecutar pipeline completo
```

### Comandos Python en Jupyter
```python
# Configurar path
import sys
sys.path.append('/app/src')

# Importar componentes
from sql_analytics import SQLAnalytics
from pathlib import Path

# Ejecutar análisis
analytics = SQLAnalytics(
    Path('/app/data/processed'), 
    Path('/app/data/analytics')
)
results = analytics.generate_analytics_tables()
```

## 🐛 Troubleshooting

### Error: Puerto 8889 en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8890:8888"  # Usar puerto 8890 en lugar de 8889
```

### Error: Permisos de archivos
```bash
# Dar permisos al script
chmod +x scripts/start-dev.sh

# Resetear permisos del proyecto
sudo chown -R $USER:$USER .
```

### Error: Datos no encontrados
```bash
# Verificar estructura de datos
ls -la data/raw/
# Debe contener: clients.csv, events.csv, retry_logs.csv

ls -la data/processed/
# Debe contener los CSVs procesados
```

### Error: Consultas SQL no encontradas
```bash
# Verificar queries SQL
ls -la queries/DML/
# Debe contener: client_summary.sql, event_time_series.sql
```

### Reconstruir completamente
```bash
# Limpiar todo y reconstruir
./scripts/start-dev.sh clean
./scripts/start-dev.sh build
./scripts/start-dev.sh up
```

### Problemas de sincronización de archivos
```bash
# Verificar volúmenes montados
docker exec kamin_data_challenge ls -la /app/queries/DML/
docker exec kamin_data_challenge cat /app/queries/DML/client_summary.sql | head -5
```

## 🎯 Ventajas del Entorno Docker

1. **🔒 Aislamiento**: No interfiere con otros proyectos
2. **📦 Reproducibilidad**: Mismo entorno en cualquier máquina
3. **⚡ Rapidez**: Setup instantáneo
4. **🛡️ Seguridad**: Usuario no-root
5. **🔄 Persistencia**: Datos y configuración guardados
6. **🎨 Completo**: Todas las herramientas incluidas
7. **🐍 DuckDB**: Motor SQL optimizado para análisis

## 🚀 Performance Tips

### Para datasets grandes
- DuckDB maneja eficientemente datasets de varios GB
- Las consultas SQL están optimizadas con CTEs
- Los CAST explícitos evitan errores de tipos

### Para desarrollo
- Usa `./scripts/start-dev.sh logs` para debugging
- Los volúmenes sincronizados permiten editar sin reconstruir
- El logging detallado ayuda a rastrear errores

## 📞 Soporte

Si tienes problemas:
1. Verifica que Docker esté corriendo: `docker --version`
2. Revisa los logs: `./scripts/start-dev.sh logs`
3. Prueba reconstruir: `./scripts/start-dev.sh build`
4. Limpia y reinicia: `./scripts/start-dev.sh clean && ./scripts/start-dev.sh up`
5. Verifica puertos: `netstat -tlnp | grep 8889`

---

¡Listo para analizar datos financieros como un pro! 🚀📊 