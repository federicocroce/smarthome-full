import math
from utilities.dimmer_pwm import DimmerPWM
# import networks.wifimgr
import networks.wifi as wifi
from networks.mqtt import get_mqtt, get_mqtt_client

temperature_values = [2000, 4000, 6500]
current_index_temperature = 0


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
    return calc_rgb_brightness(red, brightnessResult), calc_rgb_brightness(green, brightnessResult), calc_rgb_brightness(blue, brightnessResult)


def calc_rgb_temperature(temperature, brightness):
    if temperature < 2000:
        red = 100
        green = max(0, min(100, (temperature - 2000) / (6600 - 2000) * 100))
        blue = 0
    elif temperature < 6600:
        red = max(0, min(100, 100 - (temperature - 2000) / (6600 - 2000) * 100))
        green = 100
        blue = max(0, min(100, (temperature - 2000) / (6600 - 2000) * 100))
    else:
        red = 0
        green = max(
            0, min(100, 100 - (temperature - 6600) / (6000 - 6600) * 100))
        blue = 100

    brightnessResult = brightness/100
    return calc_rgb_brightness(red, brightnessResult), calc_rgb_brightness(green, brightnessResult), calc_rgb_brightness(blue, brightnessResult)


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
    led_name = led_name
    is_growing = True
    flag_is_updating = False

    def get_status():
        return {
            "led_name": led_name,
            "spectrumrgb": spectrumrgb,
            "brightness": brightness,
            "temperature": temperature,
            "is_on": is_on
        }

    def set_led_values(is_local_mode, data=None):
        nonlocal spectrumrgb
        nonlocal brightness
        nonlocal is_on
        nonlocal temperature
        nonlocal is_growing
        
        print('set_led_values data', data)
        
        if data is not None:
            color = data.get('color', None)
            if color: 
                spectrumrgb = color.get('spectrumRGB', None)
                temperature = color.get('temperature', temperature_values[1])
                
            brightness = data.get('brightness', 100)
            is_on = data.get('on', True)
        
        color_red, color_green, color_blue = 0, 0, 0
        is_growing = brightness == 100

        print("set_led_values is_on", is_on)
        print("spectrumrgb", spectrumrgb)
        print("brightness", brightness)
        print("brightness", brightness)
        
#         print("Setea el brillo")
        

        if is_local_mode == True or (not spectrumrgb and temperature):
            color_red, color_green, color_blue = calc_rgb_temperature(
                temperature, brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                spectrumrgb, brightness)
        red.set_dimmer(color_red, is_on)
        green.set_dimmer(color_green, is_on)
        blue.set_dimmer(color_blue, is_on)

    def update_values():
        nonlocal spectrumrgb
        nonlocal brightness
        nonlocal is_on
        nonlocal temperature

        color_red, color_green, color_blue = 0, 0, 0

        print("spectrumrgb actualizado", spectrumrgb)
        print("brightness actualizado", brightness)

        if not spectrumrgb and temperature:
            color_red, color_green, color_blue = calc_rgb_temperature(
                temperature, brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                spectrumrgb, brightness)
        red.set_dimmer(color_red, is_on)
        green.set_dimmer(color_green, is_on)
        blue.set_dimmer(color_blue, is_on)

    def update_device():
        if wifi.is_connected:
            nonlocal brightness
            nonlocal is_on
            nonlocal spectrumrgb
            nonlocal temperature
            
            print('update_device brightness', brightness)
            print('update_device is_on', is_on)
            print('update_device spectrumrgb', spectrumrgb)
            print('update_device temperature', temperature)
            
    #         print("get_wifi FEDE", get_wifi)
#             if get_wifi() is not None:
#                 (wlan_sta, is_wifi_connected, handle_wifi_connection, is_wifi_network_connected) = get_wifi()
            mqtt = get_mqtt()
            
            json_data = {
                "OnOff": {"on": is_on}, 
                "Brightness": {"brightness": brightness},
                "ColorSetting": {}
            }
            
            if spectrumrgb is not None:
                json_data["ColorSetting"] = {
                    "color": {
                        "spectrumRGB": spectrumrgb
                    }
                }
            elif temperature is not None:
                json_data["ColorSetting"] = {
                    "color": {
                        "temperature": temperature
                    }
                }
                

            if "update_device" in mqtt:
                mqtt["update_device"](led_name, json_data)
                print("Envío al servidor", led_name, brightness, is_on)

    def dimmer_touch(dimmer_touch_pin):
        nonlocal brightness
        nonlocal is_on
        nonlocal is_growing
#         new_is_on = is_on
#         duty = brightness
#         new_is_growing

        def callback_update_server():
            nonlocal is_growing
            nonlocal flag_is_updating

            flag_is_updating = False
            update_values()
            update_device()
            is_growing = not is_growing

        def callback_pulse():
            nonlocal is_on
            print("APAGA o ENCIENDE EL LED")
            is_on = not is_on
            # update_values()

            
        def callback_two_touching():
            nonlocal temperature
            nonlocal spectrumrgb
            global current_index_temperature
            
            try:
                current_index_temperature += 1
                temperature_values[current_index_temperature]
                print('current_index_temperature', current_index_temperature)
            except IndexError:
                current_index_temperature = 0
                        
            temperature = temperature_values[current_index_temperature]

            
            print("cambia de temperatura", current_index_temperature)
            # temperature = temperature_values[current_index_temperature]
            print("temperature", temperature)
            spectrumrgb = None
            # 6000
            # 3000
            
            
        def callback_three_touching():
            nonlocal spectrumrgb
            nonlocal temperature
            print("cambia de color")
            spectrumrgb = 16711680
            temperature = None
            
        def callback_dimmer_increase():
            nonlocal brightness
#             nonlocal duty
            print("callback_dimmer_increase", brightness)
            if brightness < 100:
                print("callback_dimmer_increase")
                brightness += 2
            brightness = limit_duty(brightness)

        def callback_dimmer_decrease():
            nonlocal brightness
            print("callback_dimmer_decrease", brightness)
            if brightness > 0:
                print("callback_dimmer_decrease")
                brightness -= 2
            brightness = limit_duty(brightness)
            

        def callback_dimmer():
            nonlocal is_growing
            nonlocal is_on
            nonlocal brightness
            nonlocal flag_is_updating

            if flag_is_updating == True:
                return

            if is_on == False:
                flag_is_updating = True
                is_growing = False
                is_on = True
                brightness = 50
                update_values()
            else:
                print('callback_dimmer', is_growing)
                if (is_growing):
                    print('callback_dimmer IF', is_growing)
                    callback_dimmer_increase()
                else:
                    print('callback_dimmer ELSE', is_growing)
                    callback_dimmer_decrease()
                update_values()

        # dimmer_touch_pin.is_touching()
        dimmer_touch_pin.is_touching((callback_pulse, callback_two_touching, callback_three_touching),
            callback_update_server, callback_dimmer)

    return {'led': (red, green, blue), 'set_led_values': set_led_values, 'get_status': get_status, 'update_device': update_device, 'dimmer_touch': dimmer_touch}
