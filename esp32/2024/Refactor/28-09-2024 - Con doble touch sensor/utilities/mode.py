import machine
import os
from utilities.common import file_exists

MODE_FILE_NAME = 'data/mode.txt'

from core.const import LED_WEB_SERVER, LED_MQTT, LED_WIFI


def read_mode():
    with open(MODE_FILE_NAME, 'r') as file:
        return file.read()


def write_mode(data):
    with open(MODE_FILE_NAME, 'w') as file:
        file.write(f'{data}')


def create_mode_file():
    # Verifica si la carpeta 'data' existe, si no, la crea
#     if not os.path.exists('/data'):
#         os.mkdir('data')

    # Crear el archivo y escribir MODE="local"
    if not file_exists(MODE_FILE_NAME):
        write_mode('MODE="local"')
        print("Archivo creado con MODE='local'")


def is_local_mode():
    content = read_mode()
    # Determinar el valor actual de MODE
    if 'MODE="local"' in content:
        return True
    else:
        return False


def toggle_mode():
    # Leer el archivo actual
    try:
        content = read_mode()
        # Determinar el valor actual de MODE
        if is_local_mode():
            new_mode = 'MODE="network"'
        else:
            new_mode = 'MODE="local"'

        # Escribir el nuevo valor de MODE
        write_mode(new_mode)

        print(f"MODE cambiado a {new_mode}")
        machine.reset()

    except OSError:
        print("No se pudo leer o modificar el archivo. Asegúrate de que existe.")


def get_is_local_mode():
    create_mode_file()
    return is_local_mode()
