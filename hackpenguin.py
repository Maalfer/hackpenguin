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
    docker_command(["images", "--format", "{{.Repository}}:{{.Tag}}", IMAGE_NAME])

def cleanup():
    docker_command(["stop", CONTAINER_NAME])
    docker_command(["rm", CONTAINER_NAME])
    sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor hackpenguin.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    args = parser.parse_args()

    if args.clean:
        cleanup()
        sys.exit()

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

    check_image()

    docker_command(["ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"]).stdout.strip()

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

    print_colored("\nPara lanzar la máquina, ejecuta el siguiente comando:", "WHITE_BOLD")
    print_colored(f"docker exec -it {CONTAINER_NAME} bash\n", "GREEN")
    print_colored("Presiona Ctrl+C para detener y eliminar el contenedor.", "RED")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
