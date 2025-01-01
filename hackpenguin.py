import argparse
import subprocess
import signal
import time
import sys
import platform
import requests
import os
from datetime import datetime

CONTAINER_NAME = "hackpenguin_container"
IMAGE_NAME = "maalfer/hackpenguin:latest"

def enable_windows_ansi():
    if platform.system() == "Windows":
        import os
        os.system('')

def print_colored(message, color):
    colors = {
        "RED": '\033[1;31m',
        "GREEN": '\033[1;32m',
        "YELLOW": '\033[1;33m',
        "CYAN": '\033[1;36m',
        "MAGENTA": '\033[1;35m',
        "WHITE_BOLD": '\033[1;37m',
        "RESET": '\033[0m'
    }

    if platform.system() == "Windows":
        enable_windows_ansi()

    print(f"{colors.get(color, colors['RESET'])}{message}{colors['RESET']}")

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

        pull_result = subprocess.Popen(["docker", "pull", IMAGE_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        for line in pull_result.stdout:
            print(line.strip())

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
    print_colored("Contenedor eliminado.", "RED")
    sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor hackpenguin.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    args = parser.parse_args()

    if args.clean:
        print_colored("Limpiando el sistema...", "RED")
        cleanup()
        sys.exit()

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

    check_image()

    print_colored(f"Comprobando si el contenedor {CONTAINER_NAME} ya existe...", "CYAN")
    container_exists = docker_command(["ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"]).stdout.strip()

    if container_exists:
        print_colored(f"El contenedor {CONTAINER_NAME} ya existe. Eliminándolo...", "MAGENTA")
        docker_command(["rm", "-f", CONTAINER_NAME])

    print_colored("Iniciando el contenedor...", "GREEN")

    current_dir = os.getcwd()
    container_id = docker_command([
        "run",
        "--network=host",
        "--privileged",
        "--name", CONTAINER_NAME,
        "-v", f"{current_dir}:/home",
        "-d", IMAGE_NAME,
        "tail", "-f", "/dev/null"
    ]).stdout.strip()

    if not container_id:
        print_colored("Error al iniciar el contenedor. Verificando detalles...", "RED")
        logs_result = docker_command(["logs", CONTAINER_NAME])
        print_colored(logs_result.stdout, "CYAN")
        sys.exit(1)

    print_colored(f"Contenedor {CONTAINER_NAME} en ejecución con ID {container_id}.", "CYAN")
    print_colored("Para lanzar la máquina, ejecuta el siguiente comando:", "WHITE_BOLD")
    print_colored(f"docker exec -it {CONTAINER_NAME} bash\n", "GREEN")
    print_colored("Presiona Ctrl+C para detener y eliminar el contenedor.", "YELLOW")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
