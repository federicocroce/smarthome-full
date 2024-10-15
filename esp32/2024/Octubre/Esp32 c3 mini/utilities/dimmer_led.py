from modules.touch_sensor import Touch as TouchSensor
import time
import _thread


def dimmer_led(led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed):
    print("Setea el brillo")
    while True:
        try:
            print("entra")
            cbk_apply_in_led(touch_dimmer_sensor)
            # touch_dimmer_sensor.check_touch_reset_press()
            time.sleep_ms(dimmer_speed)
            print("fin")
        except KeyboardInterrupt:
            print("\nBucle del Thread interrumpido por el usuario.")


def set_dimmer_led(led_name, touch_dimmer_sensor_pin, cbk_apply_in_led, dimmer_speed=500):
    touch_dimmer_sensor = TouchSensor(touch_dimmer_sensor_pin)
    return _thread.start_new_thread(dimmer_led, (led_name, touch_dimmer_sensor, cbk_apply_in_led, dimmer_speed))
