import machine
import os
import time
from core.const import off_led_core
# from core.const_led import off_led_devices

def file_exists(filepath):
    try:
        os.stat(filepath)  # Intenta obtener la información del archivo
        return True        # Si no lanza una excepción, el archivo existe
    except OSError:
        return False

def blinking_led(led, custom_sleep=0.1):
        led.on()
        time.sleep(custom_sleep)
        led.off()
        time.sleep(custom_sleep)
        
def reset_device():
    off_led_core()
#     off_led_devices()
    machine.reset()
    
    