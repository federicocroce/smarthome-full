import machine
import time
from machine import Pin
from time import sleep
from utilities.delay import delay_seconds
from machine import Timer
from networks.mqtt import get_mqtt, get_mqtt_client
import networks.wifi as wifi


DEBOUNCE_TIME = 50

class Touch:
    def __init__(self, pin):
#         self.touch_pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.touch_pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        self.value = False
        self.touch_type = 'pulse'
        self.flag_touch = False
        self.touching_time = 0
        self.touch_2_max = 2
        self.touch_3_max = 3
        self.touch_count = 0
        self.touch_reset_count_threshold = 400  # Tiempo entre doble pulsación (en ms)
        self.last_press_time = 0
        self.timer = Timer(0)

    def reset_threshold_cbk(self, callbacks_pulse, callback_touch_end_touch, time_threshold):
        def inner_callback(pin):
            callback_pulse, callback_two_touching, callback_three_touching = callbacks_pulse
            if self.touch_count == self.touch_3_max:
                if callback_three_touching:
                    callback_three_touching()
            elif self.touch_count == self.touch_2_max:
                if callback_two_touching:
                    callback_two_touching()
            else:
                print('RESET TIME TOUCH')
                if callback_pulse is not None and self.touch_type == 'pulse':
                    callback_pulse()
                self.touch_type = 'pulse'
            if callback_touch_end_touch is not None:
                delay_seconds(callback_touch_end_touch, time_threshold)
            self.touch_count = 0

    
    def test(self):
        mqtt = get_mqtt()
    
        if wifi.is_connected and mqtt and "update_device" in mqtt:
            mqtt["update_device"]("test", "asd")
           
    def is_touching(self, callbacks_pulse, callback_touch_end_touch, callback_dimmer, time_threshold=0.5):
        touch_pin = self.touch_pin
        value = False
        
        try:  # Try getting Touch state
            if touch_pin.value() == 1:
                #                 print("self.touching_time", self.touching_time)
                self.touching_time = self.touching_time + 0.02

                if self.touching_time > 1:
                #                     print("self.touching_time > 1", self.touching_time)

                    self.touch_type = 'dimmer'
                    if callback_dimmer is not None:
                        #                         print("Ejecuta callback_dimmer")
                        callback_dimmer()
#                     print("Touching")
                value = True

        except:  # If error, return True
            value = True
            return True

        if value == True and self.flag_touch == False:
            self.flag_touch = True

        elif value == False and self.flag_touch == True:
            print("Not Touching")
            self.flag_touch = False
            self.touching_time = 0
#             print("self.touch_type", self.touch_type)

#             # Si se detecta una pulsación corta
            self.timer.init(mode=machine.Timer.ONE_SHOT,
                    period=self.touch_reset_count_threshold,
                    callback=self.reset_threshold_cbk(callbacks_pulse, self.test, time_threshold))
            self.touch_count += 1
                # print("Esperando segunda pulsación...")
        # self.timer.deinit()
        self.value = value
        return {"value": value, "touch_count": self.touch_count}

