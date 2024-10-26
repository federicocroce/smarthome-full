import machine
import os
import time
from core.const import off_led_core, DATA_CORE_PATH
import json
# from core.const_led import off_led_devices

def file_exists(filepath):
    try:
        os.stat(filepath)  # Intenta obtener la información del archivo
        return True        # Si no lanza una excepción, el archivo existe
    except OSError:
        return False
    
    
def write_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f)
    except (OSError, ValueError) as e:
        print("Error al escribir el archivo JSON:", e)
        return None
    
def read_json(filepath):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except (OSError, ValueError) as e:
        print("Error al leer el archivo JSON:", e)
        return None
    

def blinking_led(led, custom_sleep=0.1):
        led.on()
        time.sleep(custom_sleep)
        led.off()
        time.sleep(custom_sleep)
        
def get_core_data():
    return read_json(DATA_CORE_PATH)
        
def merge_objects(original, updates):
    for key, value in updates.items():
        original[key] = value
    return original

def update_core_data(updates):
    new_data = merge_objects(get_core_data(), updates)
    write_json(DATA_CORE_PATH, new_data)
    

        
def reset_device():
    off_led_core()
#     off_led_devices()
    machine.reset()
    
    