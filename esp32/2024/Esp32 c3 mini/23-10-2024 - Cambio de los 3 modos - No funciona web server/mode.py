from core.const import LED_WEB_SERVER, LED_MQTT, LED_WIFI, MODE_FILE_NAME
import machine
from utilities.common import file_exists, write_json, read_json

modes = ['local', 'wbserver', 'wifi']

current_mode = ''
current_index_mode = 0

def read_mode():
    global current_mode
    data = read_json(MODE_FILE_NAME)
    print("data", data)
    if data:
        current_mode = data.get('mode', 'local')
        print("MODE", current_mode)
        return current_mode
    else:
        return ''


def write_mode(data):
    write_json(MODE_FILE_NAME, {"mode": data})


def create_mode_file():
    global current_mode, current_index_mode
    # Crear el archivo y escribir MODE="local"
    if not file_exists(MODE_FILE_NAME):
        write_mode({"mode": 'local'})
        print("Archivo creado con MODE='local'")
        current_mode = 'local'
    else:
        current_mode = read_mode()
        print(current_mode)
        current_index_mode = modes.index(current_mode)
        print("current_index_mode", current_index_mode)


def is_local_mode():
    global current_mode
    print("is_local_mode MODE", current_mode)
    return current_mode == 'local'

def is_wbserver_mode():
    global current_mode
    return current_mode == 'wbserver'

def is_wifi_mode():
    global current_mode
    return current_mode == 'wifi'

def toggle_mode():
    global current_mode, current_index_mode
    # Leer el archivo actual
    try:
        try:
            current_index_mode += 1
            modes[current_index_mode]
            print('current_index_temperature', current_index_mode)
        except IndexError:
            current_index_mode = 0

        current_mode = modes[current_index_mode]

        # Escribir el nuevo valor de MODE
        write_mode(current_mode)

        print(f"MODE cambiado a {current_mode}")
        machine.reset()

    except OSError:
        print("No se pudo leer o modificar el archivo. Asegúrate de que existe.")


# def get_is_local_mode():
#     create_mode_file()
#     return is_local_mode()
