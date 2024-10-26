from utilities.utilities_rgb import LedRGB
from utilities.dimmer_led import set_dimmer_led
from utilities.mode import is_local_mode
from utilities.common import get_core_data

# led_name = get_core_data().get('name', 'led')
led_name = 'led1'

RED_PIN = 4
GREEN_PIN = 2
BLUE_PIN = 1
TOUCH_DIMER_SENSOR_PIN = 6
# TOUCH_DIMER_SENSOR_PIN_1 = 34
# TOUCH_DIMER_SENSOR_PIN_1 = 12

led_devices = []

def off_led_devices():
    for led_device in led_devices:
        led_device.is_on = False
        

def config_led_rgb(led_device, led_data=None):
    led_device.set_led_values(is_local_mode(), led_data)


def led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin_list):
    # Crear la estructura del dispositivo led
    led_device = LedRGB(red_pin, green_pin, blue_pin, led_name)
    
    led_devices.append(led_device)

    if isinstance(dimmer_pin_list, list):
        for current_dimmer_pin in dimmer_pin_list:
            set_dimmer_led(led_device, current_dimmer_pin)
    else:
        set_dimmer_led(led_device, dimmer_pin)

    # Retornar la estructura en formato diccionario
    return {
        led_name: {
            'device': led_device,  # estructura del dispositivo led
            # thread del dimmer del led
            'set_value_device': config_led_rgb  # seteo y actualización del estado del led
        }
    }


led_devices_settings = {
    led_name: (RED_PIN, GREEN_PIN, BLUE_PIN, [TOUCH_DIMER_SENSOR_PIN])
    #     'led1': (RED_PIN, GREEN_PIN, BLUE_PIN, [TOUCH_DIMER_SENSOR_PIN, TOUCH_DIMER_SENSOR_PIN_1])
}


def leds_init(update_device_config):
    for led_name, values in led_devices_settings.items():
        red_pin, green_pin, blue_pin, dimmer_pin = values
        update_device_config(
            led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin))
