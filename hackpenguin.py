import argparse
import subprocess
import signal
import time
import sys
import os
import platform
import requests

CONTAINER_NAME = "bountypentest_container"
IMAGE_NAME = "maalfer/bountypentest:latest"

def print_colored(message, color):
    if platform.system() == "Windows":
        print(message)  # En Windows, los colores pueden no funcionar de manera nativa.
        return

    colors = {
        "RED": '\033[1;31m',
        "GREEN": '\033[1;32m',
        "YELLOW": '\033[1;33m',
        "CYAN": '\033[1;36m',
        "MAGENTA": '\033[1;35m',
        "WHITE_BOLD": '\033[1;37m',
        "RESET": '\033[0m'
    }
    print(f"{colors[color]}{message}{colors['RESET']}")

def is_windows():
    return platform.system() == "Windows"

def docker_command(cmd):
    if is_windows():
        return subprocess.run(["docker"] + cmd, shell=True, capture_output=True, text=True)
    return subprocess.run(["docker"] + cmd, capture_output=True, text=True)

def check_image():
    print_colored(f"Comprobando si la imagen {IMAGE_NAME} existe localmente...", "CYAN")
    result = docker_command(["images", "--format", "{{.Repository}}:{{.Tag}}", IMAGE_NAME])
    if IMAGE_NAME not in result.stdout:
        print_colored(f"La imagen {IMAGE_NAME} no se encontró. Descargando...", "YELLOW")

        # Iniciar el proceso de descarga de la imagen y capturar la salida en tiempo real
        pull_result = subprocess.Popen(["docker", "pull", IMAGE_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Leer y mostrar la salida de manera continua
        for line in pull_result.stdout:
            print(line.strip())  # Imprime la salida del proceso

        pull_result.stdout.close()
        pull_result.wait()

        if pull_result.returncode == 0:
            print_colored(f"Imagen {IMAGE_NAME} descargada exitosamente.", "GREEN")
        else:
            print_colored(f"Error al descargar la imagen {IMAGE_NAME}.", "RED")
            sys.exit(1)
    else:
        print_colored(f"La imagen {IMAGE_NAME} ya está disponible localmente.", "GREEN")

def cleanup():
    print_colored("Deteniendo y eliminando el contenedor...", "RED")
    docker_command(["stop", CONTAINER_NAME])
    docker_command(["rm", CONTAINER_NAME])
    print_colored("Contenedor eliminado. Saliendo.", "RED")
    sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor BountyPentest.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    parser.add_argument("--update", action="store_true", help="Comprueba si hay una nueva versión de la imagen.")
    args = parser.parse_args()

    if args.clean:
        print_colored("Limpiando el sistema...", "RED")
        docker_command(["rm", "-f", CONTAINER_NAME])
        docker_command(["rmi", IMAGE_NAME])
        print_colored("Sistema limpio.", "RED")
        sys.exit()

    if args.update:
        print_colored("La funcionalidad de actualización aún no está implementada.", "CYAN")
        sys.exit()

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

    # Verificar si la imagen está disponible localmente
    check_image()

    # Eliminar contenedor existente
    container_exists = docker_command(["ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"]).stdout.strip()
    if container_exists:
        print_colored(f"El contenedor {CONTAINER_NAME} ya existe. Eliminándolo...", "MAGENTA")
        docker_command(["rm", "-f", CONTAINER_NAME])

    # Iniciar el contenedor
    network_option = "--network=host" if not is_windows() else ""
    print_colored("Iniciando el contenedor...", "GREEN")
    container_id = docker_command(
        ["run", network_option, "--name", CONTAINER_NAME, "-d", IMAGE_NAME, "tail", "-f", "/dev/null"]
    ).stdout.strip()

    if container_id:
        print_colored("El contenedor está en ejecución.\n", "CYAN")
        print_colored("Para lanzar la máquina, ejecuta el siguiente comando:", "WHITE_BOLD")
        print_colored(f"docker exec -it {CONTAINER_NAME} bash\n", "GREEN")
        print_colored("Presiona Ctrl+C para detener y eliminar el contenedor.", "YELLOW")
    else:
        print_colored("Error al iniciar el contenedor.", "RED")
        sys.exit(1)

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
