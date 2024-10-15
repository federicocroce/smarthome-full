import time
import machine
import os
from core.const import RESET_PIN, NETWORK_PROFILES
from utilities.mode import toggle_mode
timer = machine.Timer(-1)
# Tiempo de espera para considerar que se ha pulsado el botón por 3 segundos
RESET_THRESHOLD = 3000  # en milisegundos

CHANGE_MODE_COUNT_MAX = 2
CHANGE_MODE_COUNT = 0
CHANGE_MODE_REST_COUNT_THRESHOLD = 2000


def reset_threshold_mode():
    CHANGE_MODE_COUNT = 0

# Función para detectar el reset prolongado


def detect_reset_long_press(pin):
    start_time = time.ticks_ms()
    while RESET_PIN.value() == 0:  # Espera hasta que el botón de reset se suelte
        if time.ticks_diff(time.ticks_ms(), start_time) >= RESET_THRESHOLD:
            print("Reset")
            os.remove(NETWORK_PROFILES)
            machine.reset()
            return
        else:
            timer.init(mode=machine.Timer.ONE_SHOT,
                       period=CHANGE_MODE_REST_COUNT_THRESHOLD, callback=reset_threshold_mode)
            if CHANGE_MODE_COUNT == CHANGE_MODE_COUNT_MAX:
                timer.deinit()
                toggle_mode()
                CHANGE_MODE_COUNT = 0
            else:
                CHANGE_MODE_COUNT = CHANGE_MODE_COUNT + 1
    print("No reset")


    # Configura una interrupción para detectar la pulsación del botón de reset
reset_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=detect_reset_long_press)


def file_exists(filepath):
    try:
        os.stat(filepath)  # Intenta obtener la información del archivo
        return True        # Si no lanza una excepción, el archivo existe
    except OSError:
        return False