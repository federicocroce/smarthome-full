from modules.touch_sensor import Touch as TouchSensor
import _thread

def dimmer_led(led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed = 20):
    print("Setea el brillo")
    while True:
        try:
            cbk_apply_in_led(touch_dimmer_sensor)
            time.sleep_ms(dimmer_speed)
            
            
        except KeyboardInterrupt:
            print("\nBucle interrumpido por el usuario.")


def set_dimmer_led(led_name, touch_dimmer_sensor_pin, cbk_apply_in_led, dimmer_speed = 20):
    touch_dimmer_sensor = TouchSensor(touch_dimmer_sensor_pin)
    return  _thread.start_new_thread(dimmer_led, (led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed))