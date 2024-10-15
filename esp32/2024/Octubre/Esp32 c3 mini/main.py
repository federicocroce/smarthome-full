from machine import Pin
import time

# Configurar el Pin 6 como entrada con una resistencia pull-down
pin6 = Pin(6, Pin.IN, Pin.PULL_DOWN)

def detectar_contacto(pin):
    if pin.value() == 1:
        print("¡Contacto detectado en el Pin 6!")
    else:
        print("NO")

# Configuramos un callback para el pin, se activará en el borde ascendente (de bajo a alto)
pin6.irq(trigger=Pin.IRQ_RISING, handler=detectar_contacto)

# Bucle principal
while True:
    print("while")
    time.sleep(1)  # Mantener el programa activo
