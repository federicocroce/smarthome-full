from modules.touch_sensor import Touch as TouchSensor
import time
import _thread
# import json

def dimmer_led(led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed):
    while True:
        try:
            cbk_apply_in_led(touch_dimmer_sensor)
            # touch_dimmer_sensor.check_touch_reset_press()
            time.sleep_ms(dimmer_speed)
#             value = {
#                 'OnOff': {'on': True},
#                 'Brightness': {'brightness': 100},
#                 'ColorSetting': {'color': {'spectrumRGB': 16777215}}
#             }
#             data_formatted = json.dumps({"device": "device_name", "value": value})
# 
#             print(data_formatted)
        except KeyboardInterrupt:
            print("\nBucle del Thread interrumpido por el usuario.")


def set_dimmer_led(led_name, touch_dimmer_sensor_pin, cbk_apply_in_led, dimmer_speed=20):
    touch_dimmer_sensor = TouchSensor(touch_dimmer_sensor_pin)
    return _thread.start_new_thread(dimmer_led, (led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed))
