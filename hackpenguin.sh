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
    echo -e "${WHITE_BOLD}Descripción:${RESET}"
    echo -e "  Este script inicia un contenedor Docker basado en la imagen 'maalfer/bountypentest:latest'."
    echo -e "  Si la imagen no existe localmente, se descargará automáticamente."
    echo -e "  El contenedor permanecerá activo hasta que el usuario lo detenga con Ctrl+C."
    echo -e "${WHITE_BOLD}Instrucciones:${RESET}"
    echo -e "  - Para acceder al contenedor, utiliza el comando que se mostrará al iniciar el script:"
    echo -e "    ${GREEN}sudo docker exec -it <container_id> bash${RESET}"
    echo -e "  - Para detener y eliminar el contenedor, presiona Ctrl+C mientras el script está en ejecución."
    echo -e "  - Para eliminar completamente la imagen y contenedores relacionados, usa ${GREEN}--clean${RESET}."
    exit 0
}

# Función para limpiar todos los contenedores y la imagen maalfer/bountypentest:latest al poner el parámetro --clean
clean_system() {
    echo -e "${RED}Limpiando todos los contenedores asociados a 'maalfer/bountypentest:latest'...${RESET}"
    docker ps -a --filter "ancestor=maalfer/bountypentest:latest" --format "{{.ID}}" | xargs -r docker rm -f
    echo -e "${RED}Eliminando la imagen 'maalfer/bountypentest:latest'...${RESET}"
    docker rmi maalfer/bountypentest:latest &> /dev/null
    echo -e "${RED}Limpieza completa.${RESET}"
    exit 0
}

# Comprobar los parámetros de entrada
if [[ "$1" == "-h" ]]; then
    show_help
elif [[ "$1" == "--clean" ]]; then
    clean_system
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
CONTAINER_ID=$(docker run --network=host --name "$CONTAINER_NAME" -d maalfer/bountypentest:latest tail -f /dev/null) # Usamos --network=host para que la máquina atacante use las mismas interfaces de red. De esta forma, conseguimos una compatibilidad total con cualquier máquina que estamos atacando.

echo -e "${CYAN}El contenedor está en ejecución.\n${RESET}"

echo -e "${WHITE_BOLD}Para lanzar la máquina, ejecuta el siguiente comando:${RESET}"

echo -e "${GREEN}sudo docker exec -it $CONTAINER_ID bash\n${RESET}"

# Mantener el script en ejecución hasta que se presione Ctrl+C
echo -e "${YELLOW}Presiona Ctrl+C para detener y eliminar el contenedor.${RESET}"
while true; do
    sleep 1
done
