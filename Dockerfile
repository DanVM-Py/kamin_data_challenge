# Usar Python 3.9 como base
FROM python:3.9-slim

# Metadata del contenedor
LABEL maintainer="Kamin Data Challenge"
LABEL description="Container for data analysis with Jupyter and pandas - Full IDE Support"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app/src:/app

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash --user-group kamin

# Instalar dependencias del sistema necesarias para compilar librerías
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    vim \
    pkg-config \
    libhdf5-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker layers)
COPY requirements.txt .

# Instalar todas las dependencias Python
RUN pip install --upgrade pip setuptools wheel && \
    # Core data analysis
    pip install pandas>=1.5.0 && \
    pip install numpy>=1.21.0 && \
    pip install python-dateutil>=2.8.0 && \
    # Data visualization
    pip install matplotlib>=3.5.0 && \
    pip install seaborn>=0.11.0 && \
    pip install plotly>=5.0.0 && \
    # Data processing utilities
    pip install scikit-learn>=1.0.0 && \
    pip install scipy>=1.7.0 && \
    # Jupyter and interactive development
    pip install jupyter>=1.0.0 && \
    pip install jupyterlab>=3.4.0 && \
    pip install ipywidgets>=7.6.0 && \
    # Development tools
    pip install black && \
    pip install flake8 && \
    pip install pytest && \
    # Additional utilities found in codebase
    pip install pathlib2 && \
    pip install uuid && \
    # IDE integration tools
    pip install ipykernel && \
    pip install ipython && \
    # Install from requirements.txt for any additional deps
    pip install -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Cambiar permisos al usuario kamin
RUN chown -R kamin:kamin /app

# Cambiar a usuario no-root
USER kamin

# Crear directorios necesarios
RUN mkdir -p /app/notebooks /app/data/processed /app/data/raw /app/src

# Configurar Python path para imports
ENV PYTHONPATH="${PYTHONPATH}:/app/src:/app"

# Configurar Jupyter para IDE integration
RUN python -m ipykernel install --user --name=kamin --display-name="Kamin Data Challenge"

# Exponer puerto para Jupyter
EXPOSE 8888

# Comando por defecto: iniciar Jupyter Lab con configuración para IDE
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''", "--ServerApp.allow_remote_access=True"]