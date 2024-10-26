from machine import Pin, Timer

DEBOUNCE_TIME = 50


class Touch:
    def __init__(self, pin):
        self.touch_pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.value = False
        self.touch_type = 'pulse'
        self.flag_touch = False
        self.touching_time = 0
        self.touch_2_max = 2
        self.touch_3_max = 3
        self.touch_count = 0
        # Tiempo entre doble pulsación (en ms)
        self.touch_reset_count_threshold = 400
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
                if callback_pulse:
                    callback_pulse()
            if callback_touch_end_touch:
                callback_touch_end_touch()
            self.touch_count = 0
        return inner_callback

    def is_touching(self, callbacks_pulse, callback_touch_end_touch, callback_dimmer, time_threshold=0.5):
        touch_pin = self.touch_pin
        value = False

        try:  # Try getting Touch state
            if touch_pin.value() == 1:
                self.flag_touch = True
                self.touching_time = self.touching_time + 0.02

                if self.touching_time > 0.1:
                    #                     print("self.touching_time > 1", self.touching_time)

                    self.touch_type = 'dimmer'
                    if callback_dimmer:
                        callback_dimmer()
            else:
                if self.flag_touch == False:
                    return
                self.flag_touch = False
                self.touching_time = 0
                if self.touch_type == "pulse":
                    self.timer.init(mode=Timer.ONE_SHOT,
                                    period=self.touch_reset_count_threshold,
                                    callback=self.reset_threshold_cbk(callbacks_pulse, callback_touch_end_touch, time_threshold))
                    self.touch_count += 1
                else:
                    if callback_touch_end_touch:
                        self.touch_type = 'pulse'
                        callback_touch_end_touch()

        except Exception as e:
            print("Error getting Touch state", e)
