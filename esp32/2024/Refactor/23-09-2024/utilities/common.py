import os


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