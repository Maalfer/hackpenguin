import argparse
import subprocess
import signal
import time
import sys
import platform
import requests
import os
from datetime import datetime
import calendar

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

def is_user_in_docker_group():
    """Verifica si el usuario pertenece al grupo docker (usualmente 'docker' o 'dockerusers')."""
    try:
        # Obtenemos los grupos del usuario actual
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout
        # Comprobamos si 'docker' o 'dockerusers' está en los grupos del usuario
        return 'docker' in groups or 'dockerusers' in groups
    except subprocess.CalledProcessError:
        return False

def docker_command(cmd):
    if is_windows():
        return subprocess.run(["docker"] + cmd, shell=True, capture_output=True, text=True)
    
    # Si el usuario está en el grupo docker, no se necesita sudo
    if is_user_in_docker_group():
        return subprocess.run(["docker"] + cmd, capture_output=True, text=True)
    
    # Si el usuario no está en el grupo docker, usar sudo
    return subprocess.run(["sudo", "docker"] + cmd, capture_output=True, text=True)

def check_image():
    result = docker_command(["images", "--format", "{{.Repository}}:{{.Tag}}", IMAGE_NAME])
    if IMAGE_NAME not in result.stdout:
        pull_result = subprocess.Popen(["docker", "pull", IMAGE_NAME], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in pull_result.stdout:
            print(line.strip())
        pull_result.stdout.close()
        pull_result.wait()
        if pull_result.returncode != 0:
            sys.exit(1)

def cleanup():
    print_colored("Deteniendo y eliminando el contenedor...", "RED")
    docker_command(["stop", CONTAINER_NAME])
    docker_command(["rm", CONTAINER_NAME])
    print_colored("Contenedor eliminado.", "RED")
    sys.exit()

def cleanup_all():
    docker_command(["stop", CONTAINER_NAME])
    docker_command(["rm", CONTAINER_NAME])
    docker_command(["rmi", IMAGE_NAME])
    sys.exit()

def get_dockerhub_image_date():
    url = f"https://hub.docker.com/v2/repositories/{IMAGE_NAME.split(':')[0]}/tags/{IMAGE_NAME.split(':')[1]}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["last_updated"]
    else:
        sys.exit(1)

def get_local_image_date():
    result = docker_command(["images", "--format", "{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}", IMAGE_NAME])
    if IMAGE_NAME in result.stdout:
        lines = result.stdout.strip().split("\n")
        for line in lines:
            repo, created_at = line.split("\t")
            if repo == IMAGE_NAME:
                return created_at
    return None

def compare_dates(dockerhub_date, local_date):
    dockerhub_date = datetime.strptime(dockerhub_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    local_date = local_date.split(" ")[0] + " " + local_date.split(" ")[1]
    local_date = datetime.strptime(local_date, "%Y-%m-%d %H:%M:%S")
    
    # Restar un día de forma segura
    new_day = local_date.day - 1
    
    # Si el nuevo día es menor que 1, ajustamos el mes y el día correctamente
    if new_day < 1:
        # Obtener el mes y año de la fecha local
        year = local_date.year
        month = local_date.month
        
        # Ajustar al último día del mes anterior
        if month == 1:
            # Si es enero, retrocedemos al diciembre del año anterior
            month = 12
            year -= 1
        else:
            month -= 1

        # Obtener el último día del mes anterior
        last_day_of_previous_month = calendar.monthrange(year, month)[1]
        new_day = last_day_of_previous_month

        # Crear la nueva fecha
        local_date = local_date.replace(year=year, month=month, day=new_day)
    else:
        # Si no hay problema con el día, simplemente actualizamos la fecha
        local_date = local_date.replace(day=new_day)

    # Calcular la diferencia en días entre la fecha de DockerHub y la fecha local
    diff = (dockerhub_date - local_date).days
    return diff

def update_image():
    dockerhub_date = get_dockerhub_image_date()
    local_date = get_local_image_date()
    
    if local_date:
        date_diff = compare_dates(dockerhub_date, local_date)
        
        if date_diff < 2:  # Si la diferencia es menor a 2 días
            print("La imagen está actualizada! Disfruta 🙂")
        else:
            update = input("Hay una versión más reciente de la imagen. ¿Quieres actualizar? (s/n): ")
            if update.lower() == 's':
                cleanup()
                check_image()

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor hackpenguin.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    parser.add_argument("--update", action="store_true", help="Comprueba si hay una nueva versión de la imagen.")
    args = parser.parse_args()

    if args.clean:
        cleanup_all()
        sys.exit()

    if args.update:
        update_image()
        sys.exit()

    # Verificamos si el usuario pertenece al grupo dockerusers (o docker)
    if not is_user_in_docker_group():
        print_colored(
            "Tu usuario no está en el grupo 'dockerusers'. Para añadirlo, ejecuta el siguiente comando:\n"
            "sudo usermod -aG docker $USER\n\n"
            "Luego, cierra sesión y vuelve a iniciarla para que los cambios surtan efecto.\n"
            "Alternativamente, puedes utilizar 'sudo' antes de ejecutar los comandos de Docker si no deseas añadir tu usuario al grupo.\n\n"
            "¡Una vez que hayas hecho esto, todo estará listo para usar Docker sin problemas! 😄", 
            "RED"
        )
        sys.exit()

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())
    check_image()
    container_exists = docker_command(["ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"]).stdout.strip()

    if container_exists:
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
    print_colored("Presiona Ctrl+C para detener y eliminar el contenedor.", "YELLOW")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()