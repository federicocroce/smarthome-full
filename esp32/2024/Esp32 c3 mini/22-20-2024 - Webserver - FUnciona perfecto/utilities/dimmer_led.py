import time
import _thread

from modules.touch_sensor import Touch as TouchSensor
import networks.wifi as wifi
import networks.mqtt as mqtt
from utilities.utilities_rgb_colors import limit_duty, temperature_values

increase_decrease_brightness_value = 5

def dimmer_led(led_device, touch_dimmer_sensor, dimmer_speed):
    is_growing = not led_device.brightness == 100
    flag_is_updating = False
    current_index_temperature = 0

    def callback_touch_end(data_touch):
        nonlocal flag_is_updating, is_growing, current_index_temperature
        flag_is_updating = False
        
        if data_touch.touch_type == "dimmer":
            is_growing = not is_growing
            
        led_device.update_values()

        if wifi.is_connected:
            json_data = {
                "OnOff": {"on": led_device.is_on},
                "Brightness": {"brightness": led_device.brightness},
                "ColorSetting": {}
            }

            if led_device.spectrumrgb is not None:
                json_data["ColorSetting"] = {
                    "color": {
                        "spectrumRGB": led_device.spectrumrgb
                    }
                }
            elif led_device.temperature is not None:
                json_data["ColorSetting"] = {
                    "color": {
                        "temperature": led_device.temperature
                    }
                }

            if mqtt.queue_put_update_device:
                mqtt.queue_put_update_device(led_device.led_name, json_data)
        else:
            print("No se puede enviar la data del led xq no hay internet o esta en modo local")

    def callback_pulse():
        print("APAGA o ENCIENDE EL LED")
        led_device.is_on = not led_device.is_on

    def callback_two_touching():
        nonlocal current_index_temperature

        try:
            current_index_temperature += 1
            temperature_values[current_index_temperature]
            print('current_index_temperature', current_index_temperature)
        except IndexError:
            current_index_temperature = 0

        led_device.temperature = temperature_values[current_index_temperature]

        print("cambia de temperatura", current_index_temperature)
        print("temperature", led_device.temperature)
        led_device.spectrumrgb = None

    def callback_three_touching():
        print("cambia de color")
        led_device.spectrumrgb = 16711680
        led_device.temperature = None

    def callback_dimmer_increase():
        print("callback_dimmer_increase", led_device.brightness)
        if led_device.brightness < 100:
            print("callback_dimmer_increase")
            led_device.brightness += increase_decrease_brightness_value
        led_device.brightness = limit_duty(led_device.brightness)

    def callback_dimmer_decrease():
        print("callback_dimmer_decrease", led_device.brightness)
        if led_device.brightness > 0:
            print("callback_dimmer_decrease")
            led_device.brightness -= increase_decrease_brightness_value
        led_device.brightness = limit_duty(led_device.brightness)

    def callback_dimmer():
        nonlocal flag_is_updating, is_growing
        print("Ejecuta callback_dimmer")
        
        if flag_is_updating == True:
            return

        if led_device.is_on == False:
            flag_is_updating = True
            is_growing = False
            led_device.is_on = True
            led_device.brightness = 50
        else:
            print('callback_dimmer', is_growing)
            if (is_growing):
                print('callback_dimmer IF', is_growing)
                callback_dimmer_increase()
            else:
                print('callback_dimmer ELSE', is_growing)
                callback_dimmer_decrease()
        led_device.update_values()

    while True:
        try:
            touch_dimmer_sensor.is_touching(
                (callback_pulse, callback_two_touching, callback_three_touching), callback_touch_end, callback_dimmer)
            time.sleep_ms(dimmer_speed)

        except KeyboardInterrupt:
            print("\nBucle del Thread interrumpido por el usuario.")


def set_dimmer_led(led_device, touch_dimmer_sensor_pin, dimmer_speed=1):
    touch_dimmer_sensor = TouchSensor(touch_dimmer_sensor_pin)
    return _thread.start_new_thread(dimmer_led, (led_device, touch_dimmer_sensor, dimmer_speed))
