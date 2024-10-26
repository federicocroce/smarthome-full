import time
import machine
import os
from core.const import RESET_PIN, NETWORK_PROFILES
from utilities.mode import toggle_mode

timer = machine.Timer(0)
RESET_THRESHOLD = 3000  # Tiempo para resetear (en ms)
DEBOUNCE_TIME = 50  # Tiempo para ignorar rebotes (en ms)
CHANGE_MODE_COUNT_MAX = 2
CHANGE_MODE_COUNT = 0
CHANGE_MODE_REST_COUNT_THRESHOLD = 2000  # Tiempo entre doble pulsación (en ms)
last_press_time = 0  # Tiempo de la última pulsación

def set_custom_button():

    def reset_threshold_mode(pin):
        global CHANGE_MODE_COUNT
        CHANGE_MODE_COUNT = 0
        print("Se reinicia")

    # Función para detectar pulsaciones largas o cortas
    def detect_reset_long_press(pin):
        global CHANGE_MODE_COUNT, last_press_time

        current_time = time.ticks_ms()

        # Ignorar rebotes (evitar múltiples lecturas rápidas)
        if time.ticks_diff(current_time, last_press_time) < DEBOUNCE_TIME:
            return

        last_press_time = current_time

        # Detectar si es una pulsación larga para resetear
        start_time = time.ticks_ms()
        while RESET_PIN.value() == 0:  # Espera hasta que se suelte el botón
            if time.ticks_diff(time.ticks_ms(), start_time) >= RESET_THRESHOLD:
                print("Reset")
                os.remove(NETWORK_PROFILES)
                machine.reset()
                return

        # Si se detecta una pulsación corta
        timer.init(mode=machine.Timer.ONE_SHOT,
                   period=CHANGE_MODE_REST_COUNT_THRESHOLD,
                   callback=reset_threshold_mode)

        # Incrementar el contador para el cambio de modo
        CHANGE_MODE_COUNT += 1
        print(f"Contador de modo: {CHANGE_MODE_COUNT}")

        if CHANGE_MODE_COUNT == CHANGE_MODE_COUNT_MAX:
            timer.deinit()  # Detener el temporizador si ya no es necesario
            toggle_mode()
            CHANGE_MODE_COUNT = 0
            print("Modo cambiado")
        else:
            print("Esperando segunda pulsación...")

    # Configurar la interrupción para el botón
    RESET_PIN.irq(trigger=machine.Pin.IRQ_FALLING, handler=detect_reset_long_press)
