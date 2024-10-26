from utilities.dimmer_pwm import DimmerPWM
from utilities.utilities_rgb_colors import spectrumrgb_to_rgb_limit_100, calc_rgb_temperature, temperature_values


class LedRGB:
    def __init__(self, pin_red, pin_green, pin_blue, led_name):
        self.red = DimmerPWM(pin_red, default=0)
        self.green = DimmerPWM(pin_green, default=0)
        self.blue = DimmerPWM(pin_blue, default=0)
        self.spectrumrgb = 16777215
        self.brightness = 100
        self.is_on = False
        self.temperature = None
        self.led_name = led_name

    def get_status(self):
        return {
            "led_name": self.led_name,
            "spectrumrgb": self.spectrumrgb,
            "brightness": self.brightness,
            "temperature": self.temperature,
            "is_on": self.is_on
        }

    def set_led_values(self, is_local_mode, data=None):

        if data is not None:
            color = data.get('color', None)
            if color:
                color_name = led_data.get('color', {}).get('name')
                if color_name and color_name == 'blanco':
                    self.spectrumrgb = 16777215
                else:
                    self.spectrumrgb = color.get('spectrumRGB', None)
                    self.temperature = color.get(
                        'temperature', temperature_values[1])

            self.brightness = data.get('brightness', 100)
            self.is_on = data.get('on', True)

        color_red, color_green, color_blue = 0, 0, 0

        if is_local_mode == True or (not self.spectrumrgb and self.temperature):
            color_red, color_green, color_blue = calc_rgb_temperature(
                self.temperature, self.brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                self.spectrumrgb, self.brightness)
        self.red.set_dimmer(color_red, self.is_on)
        self.green.set_dimmer(color_green, self.is_on)
        self.blue.set_dimmer(color_blue, self.is_on)

    def update_values(self):
        color_red, color_green, color_blue = 0, 0, 0

        if not self.spectrumrgb and self.temperature:
            color_red, color_green, color_blue = calc_rgb_temperature(
                self.temperature, self.brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                self.spectrumrgb, self.brightness)
        self.red.set_dimmer(color_red, self.is_on)
        self.green.set_dimmer(color_green, self.is_on)
        self.blue.set_dimmer(color_blue, self.is_on)
