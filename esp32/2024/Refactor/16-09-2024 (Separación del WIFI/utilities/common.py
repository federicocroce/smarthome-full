import time
import machine
import os
from core.const import reset_pin, NETWORK_PROFILES

# Tiempo de espera para considerar que se ha pulsado el botón por 3 segundos
RESET_THRESHOLD = 3000  # en milisegundos

# Función para detectar el reset prolongado


def detect_reset_long_press(pin):
    start_time = time.ticks_ms()
    while reset_pin.value() == 0:  # Espera hasta que el botón de reset se suelte
        if time.ticks_diff(time.ticks_ms(), start_time) >= RESET_THRESHOLD:
            print("Reset")
            os.remove(NETWORK_PROFILES)
            machine.reset()
            return
    print("No reset")

    # Configura una interrupción para detectar la pulsación del botón de reset
reset_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=detect_reset_long_press)
