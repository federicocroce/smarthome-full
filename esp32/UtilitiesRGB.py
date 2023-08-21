import math
from DimmerPWM import DimmerPWM

def calc_rgb_brightness(spectrumrgb, brightness):
    real_percent = ((spectrumrgb * 100) / 255)
    real_brightness = brightness/100
    return real_percent * brightness


def spectrumrgb_to_rgb(spectrumrgb):
    red = (spectrumrgb >> 16) & 0xFF
    green = (spectrumrgb >> 8) & 0xFF
    blue = spectrumrgb & 0xFF
    return red, green, blue


def spectrumrgb_to_rgb_limit_100(spectrumrgb, brightness):
    red = (spectrumrgb >> 16) & 0xFF
    green = (spectrumrgb >> 8) & 0xFF
    blue = spectrumrgb & 0xFF
    brightnessResult = brightness/100
    return calc_rgb_brightness(red,brightnessResult), calc_rgb_brightness(green,brightnessResult), calc_rgb_brightness(blue,brightnessResult)


def configurar_temperatura_color(temperatura):
    # Convertir la temperatura a una escala entre 0 y 1
    temperatura_normalizada = (temperatura - 2000) / (6500 - 2000) * 100

    # Calcular los valores RGB utilizando el algoritmo de McCamy
    red = 1.2929361860627455 * math.pow(temperatura_normalizada, -0.733)
    green = 0.8734649745276875 * math.pow(temperatura_normalizada, -0.445)
    blue = 0.4920593168104703 * math.pow(temperatura_normalizada, -0.376)

    # Ajustar los valores RGB a un rango entre 0 y 1
    red = min(max(red, 0), 100)
    green = min(max(green, 0), 100)
    blue = min(max(blue, 0), 100)
    
    return red * 100, green * 100, blue * 100
    # return int(red * 255 / 100), int(green * 255 / 100), int(blue * 255 / 100)

def limit_duty(duty):
    # Limitar el valor mínimo a 0
    duty = max(duty, 0)
    # Limitar el valor máximo a 100
    duty = min(duty, 100)
    return duty

def format_led_rgb(pin_red, pin_green, pin_blue, led_name):
    red = DimmerPWM(pin_red, default=0)
    green = DimmerPWM(pin_green, default=0)
    blue = DimmerPWM(pin_blue, default=0)
    spectrumrgb = 16777215
    brightness = 100
    is_on = False
    temperature = None
    led_name= led_name
        
    def set_led_values(new_spectrumrgb, new_brightness, new_is_on, new_temperature ):
        nonlocal spectrumrgb
        nonlocal brightness
        nonlocal is_on
        nonlocal temperature
        
        spectrumrgb=new_spectrumrgb
        brightness=new_brightness
        is_on=new_is_on
        temperature=new_temperature
        color_red, color_green, color_blue = 0, 0, 0
        
#         print('brightness', brightness)
#         print('is_on', is_on)
#         print('spectrumrgb', spectrumrgb)
        
        if not spectrumrgb and temperature:
            color_red, color_green, color_blue = configurar_temperatura_color(temperature)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                spectrumrgb, brightness)
#         print('red, green, blue', color_red, color_green, color_blue)
        red.set_dimmer(color_red, is_on)
        green.set_dimmer(color_green, is_on)
        blue.set_dimmer(color_blue, is_on)
        
    

    
    def increase_decrease_touch(touch_increase, touch_decrease, update_device):
#         print('touch_increase', touch_increase)
#         print('touch_decrease', touch_decrease)
#         mqtt_client.publish('update_device', 'UPDATE')
#         mqtt_client.publish('update_device', {"Brightness": {"brightness": brightness}})
        
        def callback():

            update_device(led_name, {"Brightness": {"brightness": brightness}})
            # mqtt_client.publish('update_device', 'UPDATE')
            print("Envío al servidor", led_name, brightness )

        is_touching_increase = touch_increase.is_touching(callback)
        is_touching_decrease = touch_decrease.is_touching(callback)
        
        if not is_touching_increase and not is_touching_decrease:
            return

        duty = brightness

        if (is_touching_increase and duty > 0):
            duty -= 2
        elif (is_touching_decrease and duty < 100):
            duty += 2
        duty = limit_duty(duty)
#         print('duty', duty)
        set_led_values(spectrumrgb, duty, is_on, temperature)
#         red.set_dimmer(duty)
#         green.set_dimmer(duty)
#         blue.set_dimmer(duty)
    return {'led': (red, green, blue), 'increase_decrease_touch': increase_decrease_touch, 'set_led_values': set_led_values}

