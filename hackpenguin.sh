#!/bin/bash

CONTAINER_NAME="bountypentest_container"

# Colores fosforitos
RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
WHITE_BOLD='\033[1;37m'
RESET='\033[0m'

# Menú de ayuda al poner --help
show_help() {
    echo -e "${WHITE_BOLD}Uso del script:${RESET}"
    echo -e "${GREEN}  ./script.sh${RESET}          - Ejecuta el script para iniciar un contenedor BountyPentest."
    echo -e "${GREEN}  ./script.sh -h${RESET}       - Muestra este menú de ayuda."
    echo -e "${GREEN}  ./script.sh --clean${RESET}  - Elimina todos los contenedores y la imagen 'maalfer/bountypentest:latest'."
    echo -e "${GREEN}  ./script.sh --update${RESET} - Comprueba si hay una nueva versión de la imagen en Docker Hub."
    echo -e "${WHITE_BOLD}Descripción:${RESET}"
    echo -e "  Este script inicia un contenedor Docker basado en la imagen 'maalfer/bountypentest:latest'."
    echo -e "  Si la imagen no existe localmente, se descargará automáticamente."
    echo -e "  El contenedor permanecerá activo hasta que el usuario lo detenga con Ctrl+C."
    exit 0
}

# Función para limpiar todos los contenedores y la imagen maalfer/bountypentest:latest al poner el parámetro --clean
clean_system() {
    echo -e "${RED}Limpiando todos los contenedores asociados a 'maalfer/bountypentest:latest'...${RESET}"
    docker ps -a --filter "ancestor=maalfer/bountypentest:latest" --format "{{.ID}}" | xargs -r docker rm -f
    echo -e "${RED}Eliminando la imagen 'maalfer/bountypentest:latest'...${RESET}"
    docker rmi maalfer/bountypentest:latest &> /dev/null
    echo -e "${RED}Limpieza completa.${RESET}"
}

# Función para comprobar la última versión de la imagen en Docker Hub
check_update() {
    echo -e "${CYAN}Comprobando si hay una nueva versión de la imagen en Docker Hub...${RESET}"
    
    # Obtener la fecha de creación de la imagen local
    local_created=$(docker images --format "{{.CreatedAt}}" maalfer/bountypentest:latest | head -n 1)

    if [[ -z "$local_created" ]]; then
        echo -e "${YELLOW}No se encontró una imagen local. Se procederá a descargar la última versión.${RESET}"
        clean_system
        docker pull maalfer/bountypentest:latest
        return
    fi

    # Obtener la fecha de actualización de la imagen remota desde Docker Hub
    remote_created=$(curl -s "https://hub.docker.com/v2/repositories/maalfer/bountypentest/tags/latest/" | jq -r '.last_updated' | tr 'T' ' ' | awk '{print $1}' 2>/dev/null)

    # Calcular la diferencia en días entre las dos fechas
    current_time=$(date +%s)
    local_age_days=$(( (current_time - local_created_epoch) / 86400 ))
    remote_age_days=$(( (current_time - remote_created_epoch) / 86400 ))

    # Si la imagen remota es más reciente y tiene al menos 2 días de diferencia, solicitar actualización
    if [[ $remote_age_days -lt $local_age_days && $((local_age_days - remote_age_days)) -ge 2 ]]; then
        echo -e "${YELLOW}Hay una nueva versión de la imagen disponible en Docker Hub (diferencia: $((local_age_days - remote_age_days)) días).${RESET}"
        echo -e "${WHITE_BOLD}¿Deseas actualizar a la última versión? (s/n):${RESET}"
        read -r response
        if [[ "$response" == "s" || "$response" == "S" ]]; then
            clean_system
            echo -e "${CYAN}Descargando la última versión de la imagen...${RESET}"
            docker pull maalfer/bountypentest:latest
        else
            echo -e "${CYAN}Actualización cancelada.${RESET}"
        fi
    else
        echo -e "${GREEN}La imagen local está actualizada o la diferencia es menor a 2 días.${RESET}"
    fi
}

# Comprobar los parámetros de entrada
if [[ "$1" == "-h" ]]; then
    show_help
elif [[ "$1" == "--clean" ]]; then
    clean_system
    exit 0
elif [[ "$1" == "--update" ]]; then
    check_update
    exit 0
fi

cleanup() {
    echo -e "${RED}Deteniendo y eliminando el contenedor...${RESET}"
    docker stop "$CONTAINER_NAME" &> /dev/null
    docker rm "$CONTAINER_NAME" &> /dev/null
    echo -e "${RED}Contenedor eliminado. Saliendo.${RESET}"
    exit
}

trap cleanup SIGINT

# Comprobar si la imagen 'maalfer/bountypentest:latest' existe
if ! docker images | grep -q "maalfer/bountypentest.*latest"; then
    echo -e "${YELLOW}La imagen maalfer/bountypentest:latest no se encontró. Descargando...${RESET}"
    docker pull maalfer/bountypentest:latest
fi

# Comprobar si ya existe un contenedor con el mismo nombre
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo -e "${MAGENTA}El contenedor con nombre $CONTAINER_NAME ya existe. Eliminándolo...${RESET}"
    docker rm -f "$CONTAINER_NAME"
fi

# Con tail -f /dev/null conseguimos que el contenedor esté siempre en ejecución.
echo -e "${GREEN}Iniciando el contenedor...${RESET}"
CONTAINER_ID=$(docker run --network=host --name "$CONTAINER_NAME" -d maalfer/bountypentest:latest tail -f /dev/null)

echo -e "${CYAN}El contenedor está en ejecución.\n${RESET}"

echo -e "${WHITE_BOLD}Para lanzar la máquina, ejecuta el siguiente comando:${RESET}"

echo -e "${GREEN}sudo docker exec -it $CONTAINER_ID bash\n${RESET}"

# Mantener el script en ejecución hasta que se presione Ctrl+C
echo -e "${YELLOW}Presiona Ctrl+C para detener y eliminar el contenedor.${RESET}"
while true; do
    sleep 1
done
