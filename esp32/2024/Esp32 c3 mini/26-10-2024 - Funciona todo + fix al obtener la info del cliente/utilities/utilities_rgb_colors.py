import math

temperature_values = [2000, 4000, 6500]

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
