from utilities.utilities_rgb import format_led_rgb
from utilities.dimmer_led import set_dimmer_led
from utilities.mode import get_is_local_mode


RED_PIN = 4
GREEN_PIN = 2
BLUE_PIN = 1
TOUCH_DIMER_SENSOR_PIN = 6
# TOUCH_DIMER_SENSOR_PIN_1 = 34
# TOUCH_DIMER_SENSOR_PIN_1 = 12


def config_led_rgb(led_data, led_device):
#     print("led_device", led_device)
#     print("led_data", led_data)

    is_local_mode = get_is_local_mode()

    if led_data:
#         brightness = led_data.get('brightness')
#         spectrumrgb = led_data.get('color', {}).get('spectrumRGB')
        color_name = led_data.get('color', {}).get('name')
#         temperature = led_data.get('color', {}).get('temperature')
#         is_on = led_data.get('on')

        if color_name == 'blanco':
            spectrumrgb = 16777215

        led_device['set_led_values'](is_local_mode, led_data)
    else:
        led_device['set_led_values'](is_local_mode)


def led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin_list):
    # Crear la estructura del dispositivo led
    led_device = format_led_rgb(red_pin, green_pin, blue_pin, led_name)
    
    if isinstance(dimmer_pin_list, list):
        for current_dimmer_pin in dimmer_pin_list:
            set_dimmer_led(led_name, current_dimmer_pin, led_device['dimmer_touch'])
    else:
        set_dimmer_led(led_name, dimmer_pin, led_device['dimmer_touch'])
    
    

    # Retornar la estructura en formato diccionario
    return {
        led_name: {
            'device': led_device,  # estructura del dispositivo led
            # thread del dimmer del led
            'set_value_device': config_led_rgb  # seteo y actualización del estado del led
        }
    }


led_devices_settings = {
    'led1': (RED_PIN, GREEN_PIN, BLUE_PIN, [TOUCH_DIMER_SENSOR_PIN])
#     'led1': (RED_PIN, GREEN_PIN, BLUE_PIN, [TOUCH_DIMER_SENSOR_PIN, TOUCH_DIMER_SENSOR_PIN_1])
}


def leds_init(update_device_config):
    for led_name, values in led_devices_settings.items():
        red_pin, green_pin, blue_pin, dimmer_pin = values
        update_device_config(
            led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin))
