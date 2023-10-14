from machine import Pin, TouchPad
from time import sleep

def limit_value(value, minimum, maximum):
    return max(minimum, min(value, maximum))

class Touch:
    def __init__(self, pin_num):
        self.touch = TouchPad(Pin(pin_num))
        self.value = 0
    
    def set_touch(self):
        touch = self.touch
        touch_value = touch.read()
        # Limitamos el valor entre 10 y 1000 (por ejemplo)
        touch_value = limit_value(touch_value, 10, 1000)
        print('Touch:', touch_value)
        self.value = touch_value
            
    def get_value(self):
        return self.value

# Crear objetos para los pines táctiles
touch_increase = Touch(33)
touch_decrease = Touch(32)

while True:
    # Leer el valor táctil para aumentar y disminuir
    touch_increase.set_touch()
    touch_decrease.set_touch()

    # Ejemplo de uso: Incrementar o disminuir un valor en base a los toques
    increment_step = 50  # Valor a incrementar o disminuir
    value = 500  # Valor inicial

    if touch_increase.get_value() > 500:  # Si el pin táctil de incremento es tocado
        value += increment_step
    elif touch_decrease.get_value() > 500:  # Si el pin táctil de disminución es tocado
        value -= increment_step

    print('Valor:', value)
    sleep(0.1)  # Pequeña pausa para evitar lecturas erróneas

