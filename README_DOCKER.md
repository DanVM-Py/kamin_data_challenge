# 🐳 Kamin Data Challenge - Docker Environment

¡Entorno Docker completamente configurado para análisis de datos con Jupyter Lab!

## 🚀 Inicio Rápido

### Opción 1: Script automatizado (Recomendado)
```bash
# Iniciar Jupyter Lab
./scripts/start-dev.sh

# Ver en navegador: http://localhost:8888
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
./scripts/start-dev.sh up      # Iniciar Jupyter Lab (por defecto)
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
- **Puerto**: 8888 (Jupyter Lab)
- **Usuario**: kamin (no-root para seguridad)
- **Directorio de trabajo**: `/app`

### Dependencias Incluidas
- **Análisis de datos**: pandas, numpy, scipy, scikit-learn
- **Visualización**: matplotlib, seaborn, plotly
- **Desarrollo**: Jupyter Lab, IPython widgets
- **Herramientas**: black, flake8, pytest

### Volúmenes Montados
```
./src        → /app/src        (código fuente)
./notebooks  → /app/notebooks  (notebooks Jupyter)
./data       → /app/data       (datasets)
```

## 📊 Notebooks Disponibles

### `load_local_docker.ipynb`
Notebook optimizado para el entorno Docker que incluye:
- ✅ Carga automática de datasets
- 🧪 Test de normalización de retry_logs
- 📈 Vista previa de datos
- 🎮 Playground para experimentar

### Uso del Notebook
1. Ejecutar `./scripts/start-dev.sh`
2. Abrir http://localhost:8888
3. Navegar a `notebooks/load_local_docker.ipynb`
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
│   └── transform.py         # Funciones de transformación
├── notebooks/               # Notebooks Jupyter
│   └── load_local_docker.ipynb
└── data/                    # Datasets
    ├── raw/                 # Datos originales
    └── processed/           # Datos procesados
```

### Desarrollo en Tiempo Real
Los cambios en el código fuente se reflejan inmediatamente en el contenedor gracias a los volúmenes montados:

- Edita archivos en `./src/` → Cambios disponibles en `/app/src/`
- Crea notebooks en `./notebooks/` → Accesibles en Jupyter Lab
- Agrega datos en `./data/` → Disponibles para análisis

## 🔍 Funciones Disponibles

### Carga de Datos (`src/load.py`)
```python
from load import load_csv

# Cargar un CSV
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
python src/load.py  # Ejecutar scripts
```

### Comandos Python
```python
# En Jupyter o shell
import sys
sys.path.append('/app/src')

from load import load_csv
from transform import normalize_retry_logs_metadata

# Cargar y procesar datos
df = load_csv('retry_logs.csv', Path('/app/data/raw'))
df_clean = normalize_retry_logs_metadata(df)
```

## 🐛 Troubleshooting

### Error: Puerto 8888 en uso
```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8889:8888"  # Usar puerto 8889 en lugar de 8888
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
```

### Reconstruir completamente
```bash
# Limpiar todo y reconstruir
./scripts/start-dev.sh clean
./scripts/start-dev.sh build
./scripts/start-dev.sh up
```

## 🎯 Ventajas del Entorno Docker

1. **🔒 Aislamiento**: No interfiere con otros proyectos
2. **📦 Reproducibilidad**: Mismo entorno en cualquier máquina
3. **⚡ Rapidez**: Setup instantáneo
4. **🛡️ Seguridad**: Usuario no-root
5. **🔄 Persistencia**: Datos y configuración guardados
6. **🎨 Completo**: Todas las herramientas incluidas

## 📞 Soporte

Si tienes problemas:
1. Verifica que Docker esté corriendo: `docker --version`
2. Revisa los logs: `./scripts/start-dev.sh logs`
3. Prueba reconstruir: `./scripts/start-dev.sh build`
4. Limpia y reinicia: `./scripts/start-dev.sh clean && ./scripts/start-dev.sh up`

---

¡Listo para analizar datos como un pro! 🚀📊 