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

def cleanup_all():
    print_colored("Deteniendo y eliminando el contenedor e imagen...", "RED")
    docker_command(["stop", CONTAINER_NAME])
    docker_command(["rm", CONTAINER_NAME])
    docker_command(["rmi", IMAGE_NAME])
    print_colored("Contenedor e imagen eliminado.", "RED")
    sys.exit()

def get_dockerhub_image_date():
    """Obtiene la fecha del último push de la imagen desde Docker Hub."""
    url = f"https://hub.docker.com/v2/repositories/{IMAGE_NAME.split(':')[0]}/tags/{IMAGE_NAME.split(':')[1]}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["last_updated"]
    else:
        print_colored("Error al obtener la fecha de Docker Hub.", "RED")
        sys.exit(1)

def get_local_image_date():
    """Obtiene la fecha del último push de la imagen local usando docker images."""
    result = docker_command(["images", "--format", "{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}", IMAGE_NAME])
    if IMAGE_NAME in result.stdout:
        lines = result.stdout.strip().split("\n")
        for line in lines:
            repo, created_at = line.split("\t")
            if repo == IMAGE_NAME:
                return created_at
    return None

def compare_dates(dockerhub_date, local_date):
    """Compara las fechas de Docker Hub y la imagen local para ver si hay una nueva versión."""
    dockerhub_date = datetime.strptime(dockerhub_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    local_date = local_date.split(" ")[0] + " " + local_date.split(" ")[1]
    local_date = datetime.strptime(local_date, "%Y-%m-%d %H:%M:%S")
    local_date = local_date.replace(day=local_date.day - 1)
    diff = (dockerhub_date - local_date).days
    return diff

def update_image():
    """Función para manejar la actualización de la imagen."""
    print_colored("Comprobando si hay una nueva versión de la imagen...", "CYAN")
    dockerhub_date = get_dockerhub_image_date()
    local_date = get_local_image_date()

    if local_date:
        print_colored(f"Fecha de la imagen local: {local_date}", "GREEN")
        print_colored(f"Fecha de la imagen en Docker Hub: {dockerhub_date}", "GREEN")
        date_diff = compare_dates(dockerhub_date, local_date)
        print_colored(f"Diferencia de días: {date_diff} días", "CYAN")

        if date_diff > 2:
            update = input("Hay una versión más reciente de la imagen. ¿Quieres actualizar? (s/n): ")
            if update.lower() == 's':
                cleanup()
                check_image()
                print_colored("Imagen actualizada con éxito.", "GREEN")
            else:
                print_colored("No se realizará la actualización.", "YELLOW")
        else:
            print_colored("No hay una actualización disponible.", "GREEN")
    else:
        print_colored("No se pudo obtener la fecha de la imagen local.", "RED")

def save_image():
    """Función para guardar la imagen localmente usando docker save."""
    current_dir = os.getcwd()
    save_path = os.path.join(current_dir, f"{IMAGE_NAME.replace(':', '_').replace('/', '_')}.tar")
    print_colored(f"Guardando la imagen {IMAGE_NAME} en {save_path}...", "CYAN")
    result = docker_command(["save", "-o", save_path, IMAGE_NAME])
    if result.returncode == 0:
        print_colored(f"Imagen {IMAGE_NAME} guardada correctamente en {save_path}.", "GREEN")
    else:
        print_colored(f"Error al guardar la imagen {IMAGE_NAME}.", "RED")
        sys.exit(1)

def load_image():
    """Función para cargar la imagen desde un archivo tar en el directorio actual."""
    current_dir = os.getcwd()
    tar_file = os.path.join(current_dir, "maalfer_hackpenguin_latest.tar")
    if os.path.exists(tar_file):
        print_colored(f"Cargando la imagen desde {tar_file}...", "CYAN")
        result = docker_command(["load", "-i", tar_file])
        if result.returncode == 0:
            print_colored(f"Imagen cargada correctamente desde {tar_file}.", "GREEN")
        else:
            print_colored(f"Error al cargar la imagen desde {tar_file}.", "RED")
            sys.exit(1)
    else:
        print_colored(f"No se encontró el archivo {tar_file} en el directorio actual.", "RED")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor hackpenguin.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    parser.add_argument("--update", action="store_true", help="Comprueba si hay una nueva versión de la imagen.")
    parser.add_argument("--save", action="store_true", help="Guarda la imagen localmente en un archivo tar.")
    parser.add_argument("--load", action="store_true", help="Carga la imagen desde el archivo maalfer_hackpenguin_latest.tar.")
    args = parser.parse_args()

    if args.clean:
        print_colored("Limpiando el sistema...", "RED")
        cleanup_all()
        sys.exit()

    if args.update:
        update_image()
        sys.exit()

    if args.save:
        save_image()
        sys.exit()

    if args.load:
        load_image()
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
