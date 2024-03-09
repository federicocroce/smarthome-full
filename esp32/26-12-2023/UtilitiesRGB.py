import math
from DimmerPWM import DimmerPWM
from WiFi import get_wifi
from MQTT import get_mqtt, get_mqtt_client

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


def configurar_temperatura_color(temperatura, brightness):
    if temperatura < 2000:
        red = 100
        green = max(0, min(100, (temperatura - 2000) / (6600 - 2000) * 100))
        blue = 0
    elif temperatura < 6600:
        red = max(0, min(100, 100 - (temperatura - 2000) / (6600 - 2000) * 100))
        green = 100
        blue = max(0, min(100, (temperatura - 2000) / (6600 - 2000) * 100))
    else:
        red = 0
        green = max(0, min(100, 100 - (temperatura - 6600) / (6000 - 6600) * 100))
        blue = 100
    
    brightnessResult = brightness/100
    return calc_rgb_brightness(red,brightnessResult), calc_rgb_brightness(green,brightnessResult), calc_rgb_brightness(blue,brightnessResult)

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
    
    def get_status():
        return {
            "led_name": led_name,
            "spectrumrgb":spectrumrgb,
            "brightness": brightness,
            "temperature": temperature,
            "is_on": is_on
            }

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
        
        print("set_led_values is_on", new_is_on)
        
        if not spectrumrgb and temperature:
            color_red, color_green, color_blue = configurar_temperatura_color(temperature, brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                spectrumrgb, brightness)
        red.set_dimmer(color_red, is_on)
        green.set_dimmer(color_green, is_on)
        blue.set_dimmer(color_blue, is_on)
        
    def update_device():
        nonlocal brightness
        nonlocal is_on
        print("keep_mqtt_connection_cbk")
        (handle_wifi_disconnect, is_wifi_connected) = get_wifi()
        mqtt = get_mqtt()

        if is_wifi_connected() and "update_device" in mqtt :
            mqtt["update_device"](led_name, {"OnOff": {"on": is_on}, "Brightness": {"brightness": brightness}})
            print("Envío al servidor", led_name, brightness )
    
    def increase_decrease_touch(touch_increase, touch_decrease):
        new_is_on = is_on
        duty = brightness
        def callback_update_server():
            update_device()
        
        def callback_pulse():
            print("APAGA EL LED")
            new_is_on = not is_on
            set_led_values(spectrumrgb, duty, new_is_on, temperature)
        
        def callback_dimmer_increase():
            nonlocal duty
            print("callback_dimmer_increase", duty)
            if duty < 100:
                print("callback_dimmer_increase")
                duty += 2
            duty = limit_duty(duty)
            set_led_values(spectrumrgb, duty, is_on, temperature)
        
        def callback_dimmer_decrease():
            nonlocal duty
            print("callback_dimmer_decrease", duty)
            if duty > 0:
                print("callback_dimmer_decrease")
                duty -= 2
            duty = limit_duty(duty)
            set_led_values(spectrumrgb, duty, is_on, temperature)
            
        def cbk_test():
            print("cbk_test")
        
        is_touching_increase = touch_increase.is_touching(callback_update_server, callback_pulse, callback_dimmer_increase)
        is_touching_decrease = touch_decrease.is_touching(callback_update_server, callback_pulse, callback_dimmer_decrease)

#         print("is_touching_increase['status']", is_touching_increase["status"])
#         print("is_touching_decrease['status']", is_touching_decrease["status"])
        
#         if not is_touching_increase and not is_touching_decrease:
#             return
        
#         print("is_touching_increase['touch_type']", is_touching_increase["touch_type"])
#         print("is_touching_decrease['touch_type']", is_touching_decrease["touch_type"])
#         print("is_on", is_on)
#         
#         if(is_touching_increase["touch_type"] == "pulse" or is_touching_decrease["touch_type"] == "pulse"):
#             new_is_on = not is_on
#             print("is_on", is_on)
            
#         if (is_touching_increase and duty > 0):
#             duty -= 2
#         elif (is_touching_decrease and duty < 100):
#             duty += 2
#         duty = limit_duty(duty)
#         
#         set_led_values(spectrumrgb, duty, False, temperature)

    return {'led': (red, green, blue), 'increase_decrease_touch': increase_decrease_touch, 'set_led_values': set_led_values, 'get_status': get_status, 'update_device': update_device}


