from machine import Pin, PWM

MAX_CYCLE = 1023


class DimmerPWM:
    def __init__(self, pin, default=100, max_cycle=MAX_CYCLE):
        self.pwm_pin = PWM(Pin(pin))
        self.cycle_value = (default * max_cycle)/100
        self.max_cycle = max_cycle
        self.duty = default
        self.pwm_pin.duty(int(self.cycle_value))

    def set_dimmer(self, duty, is_on=True, freq=60):
        if is_on == False:
            duty = 0
        self.duty = duty
        pwm_pin = self.pwm_pin
        pwm_pin.freq(freq)
        cycle_value = (duty * self.max_cycle)/100
        pwm_pin.duty(int(cycle_value))
        self.percent = cycle_value
        return cycle_value

    def get_dimmer(self):
        return self.percent

    def get_duty(self):
        return self.duty
