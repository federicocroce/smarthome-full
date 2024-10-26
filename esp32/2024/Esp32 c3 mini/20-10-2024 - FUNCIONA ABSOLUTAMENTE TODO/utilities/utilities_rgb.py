from utilities.dimmer_pwm import DimmerPWM
from utilities.utilities_rgb_colors import calc_rgb_brightness, spectrumrgb_to_rgb, spectrumrgb_to_rgb_limit_100, calc_rgb_temperature, temperature_values


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
    def set_status(data):
        if data is not None:
            self.spectrumrgb = data.get('spectrumrgb', self.spectrumrgb)
            self.brightness = data.get('brightness', self.brightness)
            self.temperature = data.get('temperature', self.temperature)
            self.is_on = data.get('is_on', self.is_on)
            update_values()
        

    def set_led_values(self, is_local_mode, data=None):

        print('set_led_values data', data)

        if data is not None:
            color = data.get('color', None)
            if color:
                self.spectrumrgb = color.get('spectrumRGB', None)
                self.temperature = color.get('temperature', temperature_values[1])

            self.brightness = data.get('brightness', 100)
            self.is_on = data.get('on', True)

        color_red, color_green, color_blue = 0, 0, 0
#         self.is_growing = brightness == 100

        print("set_led_values is_on", self.is_on)
        print("spectrumrgb", self.spectrumrgb)
        print("brightness", self.brightness)


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
#         print("spectrumrgb actualizado", self.spectrumrgb)
#         print("brightness actualizado", self.brightness)

        if not self.spectrumrgb and self.temperature:
            color_red, color_green, color_blue = calc_rgb_temperature(
                self.temperature, self.brightness)
        else:
            color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
                self.spectrumrgb, self.brightness)
        self.red.set_dimmer(color_red, self.is_on)
        self.green.set_dimmer(color_green, self.is_on)
        self.blue.set_dimmer(color_blue, self.is_on)
