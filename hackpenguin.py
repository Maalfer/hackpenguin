import argparse
import subprocess
import signal
import time
import sys
import requests

CONTAINER_NAME = "bountypentest_container"

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
    print(f"{colors[color]}{message}{colors['RESET']}")

def show_help():
    print_colored("Uso del script:", "WHITE_BOLD")
    print_colored("  python script.py", "GREEN")
    print_colored("  python script.py -h", "GREEN")
    print_colored("  python script.py --clean", "GREEN")
    print_colored("  python script.py --update", "GREEN")
    print_colored("\nDescripción:", "WHITE_BOLD")
    print("  Este script inicia un contenedor Docker basado en la imagen 'maalfer/bountypentest:latest'.")
    print("  Si la imagen no existe localmente, se descargará automáticamente.")
    print("  El contenedor permanecerá activo hasta que el usuario lo detenga con Ctrl+C.")

def clean_system():
    print_colored("Limpiando todos los contenedores asociados a 'maalfer/bountypentest:latest'...", "RED")
    containers = subprocess.run(
        ["docker", "ps", "-a", "--filter", "ancestor=maalfer/bountypentest:latest", "--format", "{{.ID}}"],
        capture_output=True, text=True
    ).stdout.splitlines()
    if containers:
        subprocess.run(["docker", "rm", "-f"] + containers)
    print_colored("Eliminando la imagen 'maalfer/bountypentest:latest'...", "RED")
    subprocess.run(["docker", "rmi", "maalfer/bountypentest:latest"], stdout=subprocess.DEVNULL)
    print_colored("Limpieza completa.", "RED")

def check_update():
    print_colored("Comprobando si hay una nueva versión de la imagen en Docker Hub...", "CYAN")
    local_created = subprocess.run(
        ["docker", "images", "--format", "{{.CreatedAt}}", "maalfer/bountypentest:latest"],
        capture_output=True, text=True
    ).stdout.strip()

    if not local_created:
        print_colored("No se encontró una imagen local. Se procederá a descargar la última versión.", "YELLOW")
        clean_system()
        subprocess.run(["docker", "pull", "maalfer/bountypentest:latest"])
        return

    try:
        response = requests.get("https://hub.docker.com/v2/repositories/maalfer/bountypentest/tags/latest/")
        response.raise_for_status()
        remote_created = response.json().get("last_updated", "").split("T")[0]
    except Exception as e:
        print_colored(f"Error al comprobar la actualización: {e}", "RED")
        return

    print_colored("Comparando fechas locales y remotas...", "CYAN")
    if remote_created > local_created:
        print_colored("Hay una nueva versión de la imagen disponible en Docker Hub.", "YELLOW")
        update = input("¿Deseas actualizar a la última versión? (s/n): ").strip().lower()
        if update == 's':
            clean_system()
            print_colored("Descargando la última versión de la imagen...", "CYAN")
            subprocess.run(["docker", "pull", "maalfer/bountypentest:latest"])
        else:
            print_colored("Actualización cancelada.", "CYAN")
    else:
        print_colored("La imagen local está actualizada.", "GREEN")

def cleanup():
    print_colored("Deteniendo y eliminando el contenedor...", "RED")
    subprocess.run(["docker", "stop", CONTAINER_NAME], stdout=subprocess.DEVNULL)
    subprocess.run(["docker", "rm", CONTAINER_NAME], stdout=subprocess.DEVNULL)
    print_colored("Contenedor eliminado. Saliendo.", "RED")
    sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Script para gestionar contenedor BountyPentest.")
    parser.add_argument("--clean", action="store_true", help="Elimina todos los contenedores y la imagen.")
    parser.add_argument("--update", action="store_true", help="Comprueba si hay una nueva versión de la imagen.")
    args = parser.parse_args()

    if args.clean:
        clean_system()
        sys.exit()

    if args.update:
        check_update()
        sys.exit()

    signal.signal(signal.SIGINT, lambda sig, frame: cleanup())

    image_exists = subprocess.run(
        ["docker", "images", "maalfer/bountypentest:latest"],
        capture_output=True, text=True
    ).stdout

    if not image_exists:
        print_colored("La imagen maalfer/bountypentest:latest no se encontró. Descargando...", "YELLOW")
        subprocess.run(["docker", "pull", "maalfer/bountypentest:latest"])

    container_exists = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"],
        capture_output=True, text=True
    ).stdout.strip()

    if container_exists:
        print_colored(f"El contenedor con nombre {CONTAINER_NAME} ya existe. Eliminándolo...", "MAGENTA")
        subprocess.run(["docker", "rm", "-f", CONTAINER_NAME])

    print_colored("Iniciando el contenedor...", "GREEN")
    container_id = subprocess.run(
        ["docker", "run", "--network=host", "--name", CONTAINER_NAME, "-d", "maalfer/bountypentest:latest", "tail", "-f", "/dev/null"],
        capture_output=True, text=True
    ).stdout.strip()

    print_colored("El contenedor está en ejecución.\n", "CYAN")
    print_colored("Para lanzar la máquina, ejecuta el siguiente comando:", "WHITE_BOLD")
    print_colored(f"sudo docker exec -it {container_id} bash\n", "GREEN")
    print_colored("Presiona Ctrl+C para detener y eliminar el contenedor.", "YELLOW")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()