from core.device_config import update_device_config

RED_PIN = 5
GREEN_PIN = 18
BLUE_PIN = 19
TOUCH_DIMER_SENSOR_PIN = 13


def config_led_rgb(led_data, led_device):
    print("led_device", led_device)
    print("led_data", led_data)

    if led_data:
        brightness = led_data.get('brightness')
        spectrumrgb = led_data.get('color', {}).get('spectrumRGB')
        color_name = led_data.get('color', {}).get('name')
        temperature = led_data.get('color', {}).get('temperature')
        is_on = led_data.get('on')
#         print('Brightness:', brightness)
#         print('Color:', spectrumrgb)
#         print('Is On:', is_on)

#         (red, green, blue) = led_device['led']

#         color_red, color_green, color_blue = 0, 0, 0
        if color_name == 'blanco':
            spectrumrgb = 16777215

        led_device['set_led_values'](
            spectrumrgb, brightness, is_on, temperature)


#         if not spectrumrgb and temperature:
#             color_red, color_green, color_blue = configurar_temperatura_color(temperature)
#         else:
#             color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
#                 spectrumrgb, brightness)
#         print('red, green, blue', color_red, color_green, color_blue)
#         red.set_dimmer(color_red, is_on)
#         green.set_dimmer(color_green, is_on)
#         blue.set_dimmer(color_blue, is_on)

def led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin):
    # Crear la estructura del dispositivo LED
    led_device = format_led_rgb(red_pin, green_pin, blue_pin, led_name)
    
    # Retornar la estructura en formato diccionario
    return {
        led_name: {
            'device': led_device,
            'dimmer': set_dimmer_led(led_name, dimmer_pin, led_device['dimmer_touch']),
            'set_value_device': config_led_rgb
        }
    }


led_devices_settings = {
    'led1': (5, 18, 19, TOUCH_DIMER_SENSOR_PIN)
    'led2': (6, 7, 8, TOUCH_DIMER_2_SENSOR_PIN)
}


leds_init():
    for led_name, values in led_devices_settings.items():
        red_pin, green_pin, blue_pin, dimmer_pin = values
        update_device_config(led_init(led_name, red_pin, green_pin, blue_pin, dimmer_pin))
    





