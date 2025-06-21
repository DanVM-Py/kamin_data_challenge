#!/bin/bash

echo "🐳 Kamin Data Challenge - Docker Development Environment"
echo "========================================================="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detectar si necesita sudo para Docker
detect_sudo_requirement() {
    if docker version &> /dev/null; then
        echo ""
    elif sudo docker version &> /dev/null; then
        echo "sudo "
    else
        echo -e "${RED}❌ Docker no está disponible con o sin sudo${NC}"
        echo "Verifica que Docker esté instalado y corriendo"
        exit 1
    fi
}

# Detectar comando Docker Compose disponible
detect_compose_cmd() {
    local sudo_prefix=$1
    
    if ${sudo_prefix}docker compose version &> /dev/null; then
        echo "${sudo_prefix}docker compose"
    elif command -v docker-compose &> /dev/null && ${sudo_prefix}docker-compose version &> /dev/null; then
        echo "${sudo_prefix}docker-compose"
    else
        echo -e "${RED}❌ Docker Compose no está disponible${NC}"
        echo "Por favor instala Docker Compose"
        exit 1
    fi
}

# Detectar configuración
SUDO_PREFIX=$(detect_sudo_requirement)
COMPOSE_CMD=$(detect_compose_cmd "$SUDO_PREFIX")

echo -e "${BLUE}📦 Configuración detectada:${NC}"
echo -e "   Docker: ${SUDO_PREFIX}docker"
echo -e "   Compose: $COMPOSE_CMD"

# Función para ejecutar comando con verificación de errores
run_with_check() {
    local cmd="$1"
    local success_msg="$2"
    local error_msg="$3"
    
    echo -e "${BLUE}🔄 Ejecutando: $cmd${NC}"
    
    if eval "$cmd"; then
        if [ -n "$success_msg" ]; then
            echo -e "${GREEN}✅ $success_msg${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ $error_msg${NC}"
        return 1
    fi
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}Uso:${NC}"
    echo "  ./scripts/start-dev.sh [comando]"
    echo ""
    echo -e "${BLUE}Comandos disponibles:${NC}"
    echo "  up       - Iniciar Jupyter Lab (por defecto)"
    echo "  down     - Detener contenedores"
    echo "  build    - Reconstruir imagen Docker"
    echo "  shell    - Abrir shell interactivo en el contenedor"
    echo "  clean    - Limpiar contenedores e imágenes"
    echo "  logs     - Ver logs del contenedor"
    echo "  help     - Mostrar esta ayuda"
    echo ""
    echo -e "${YELLOW}💡 Tu configuración requiere: $COMPOSE_CMD${NC}"
}

# Función para iniciar Jupyter
start_jupyter() {
    echo -e "${GREEN}🚀 Iniciando Jupyter Lab...${NC}"
    
    if run_with_check "$COMPOSE_CMD up --build -d kamin-jupyter" \
                      "Contenedor iniciado correctamente" \
                      "Error al iniciar el contenedor"; then
        
        # Esperar un poco y verificar que esté corriendo
        echo -e "${BLUE}⏳ Verificando estado del servicio...${NC}"
        sleep 3
        
        if run_with_check "$COMPOSE_CMD ps kamin-jupyter" \
                          "" \
                          "Error verificando el estado del contenedor"; then
            
            echo ""
            echo -e "${GREEN}🎉 ¡Jupyter Lab iniciado exitosamente!${NC}"
            echo -e "${YELLOW}📊 Disponible en: http://localhost:8888${NC}"
            echo ""
            echo -e "${BLUE}💡 Comandos útiles:${NC}"
            echo "   Ver logs:     $COMPOSE_CMD logs -f kamin-jupyter"
            echo "   Detener:      $COMPOSE_CMD down"
            echo "   Shell:        ./scripts/start-dev.sh shell"
        fi
    else
        echo -e "${RED}💥 Falló el inicio de Jupyter Lab${NC}"
        echo -e "${YELLOW}💡 Sugerencias:${NC}"
        echo "   - Verifica que Docker esté corriendo"
        echo "   - Prueba: $COMPOSE_CMD logs kamin-jupyter"
        echo "   - O ejecuta: ./scripts/start-dev.sh clean"
    fi
}

# Función para abrir shell
open_shell() {
    echo -e "${GREEN}🐚 Abriendo shell interactivo...${NC}"
    
    if run_with_check "$COMPOSE_CMD up -d kamin-dev" \
                      "Contenedor dev iniciado" \
                      "Error iniciando contenedor dev"; then
        
        echo -e "${BLUE}🔗 Conectando al shell...${NC}"
        $COMPOSE_CMD exec kamin-dev bash
    fi
}

# Función para limpiar
clean_docker() {
    echo -e "${YELLOW}🧹 Limpiando contenedores e imágenes...${NC}"
    
    run_with_check "$COMPOSE_CMD down --volumes --remove-orphans" \
                   "Contenedores detenidos" \
                   "Error deteniendo contenedores"
    
    run_with_check "${SUDO_PREFIX}docker system prune -f" \
                   "Sistema Docker limpiado" \
                   "Error limpiando sistema Docker"
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
}

# Procesar argumentos
case "${1:-up}" in
    "up"|"start")
        start_jupyter
        ;;
    "down"|"stop")
        echo -e "${YELLOW}⏹️  Deteniendo contenedores...${NC}"
        run_with_check "$COMPOSE_CMD down" \
                       "Contenedores detenidos" \
                       "Error deteniendo contenedores"
        ;;
    "build"|"rebuild")
        echo -e "${BLUE}🔨 Reconstruyendo imagen...${NC}"
        run_with_check "$COMPOSE_CMD build --no-cache" \
                       "Imagen reconstruida" \
                       "Error reconstruyendo imagen"
        ;;
    "shell"|"bash")
        open_shell
        ;;
    "clean")
        clean_docker
        ;;
    "logs")
        echo -e "${BLUE}📋 Mostrando logs...${NC}"
        $COMPOSE_CMD logs -f kamin-jupyter
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${YELLOW}⚠️  Comando desconocido: $1${NC}"
        show_help
        exit 1
        ;;
esac 