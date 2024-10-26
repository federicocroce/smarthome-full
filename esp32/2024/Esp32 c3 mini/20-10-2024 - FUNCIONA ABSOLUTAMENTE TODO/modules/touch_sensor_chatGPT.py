from machine import Pin
import time
from time import sleep
from utilities.delay import delay_seconds


class Touch:
    def __init__(self, pin_num, timeout=2):
        self.button = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.press_count = 0
        self.last_press_time = 0
        self.timeout = timeout  # Tiempo en segundos para reiniciar el contador de pulsos
        self.button_held = False  # Estado para saber si el botón está siendo presionado

        # Configurar interrupción para detectar cuando el botón es presionado
        self.button.irq(trigger=Pin.IRQ_FALLING, handler=self.is_touching)

    # Función que se ejecutará cuando se detecte un pulsador presionado
    def is_touching(self, pin):
        current_time = time.time()

        # Si ha pasado más del timeout entre pulsos, se reinicia el contador
        if current_time - self.last_press_time > self.timeout:
            self.press_count = 0

        # Aumentar el contador de pulsos y actualizar el tiempo del último pulso
        self.press_count += 1
        self.last_press_time = current_time

        # Evaluar cuántas veces se ha presionado
        if self.press_count == 1:
            print("Se enciende o se apaga el LED")
        elif self.press_count == 2:
            print("Se cambia la temperatura de LED")
        elif self.press_count == 3:
            print("Se seteó a color rojo")
            self.press_count = 0  # Reiniciar el contador después de 3 pulsaciones

    # Función para detectar si el botón se mantiene presionado
    def check_button_held(self):
        if self.button.value() == 0:  # El botón está presionado
            if not self.button_held:
                self.button_held = True
                print("Estoy siendo presionado")
        else:  # El botón ya no está presionado
            print("NO esta presionado")
            self.button_held = False

    # Función para gestionar el timeout y reiniciar el contador de pulsos si es necesario
    def reset_press_count_if_needed(self):
        if self.press_count > 0 and time.time() - self.last_press_time > self.timeout:
            self.press_count = 0
            
    def check_touch_reset_press(self):
        self.check_button_held()
        self.reset_press_count_if_needed()