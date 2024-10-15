from machine import Pin
from time import sleep
import dht

class TemperatureHumidity:
    def __init__(self, pin):
        self.sensor = dht.DHT22(Pin(pin))
        self.temperature = 0
        self.humidity = 0

    def get_temperature_humidity(self, delay=1):
        sensor = self.sensor
        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        self.temperature = temperature
        self.humidity = humidity
        return ({'temperature': temperature, 'humidity': humidity})
    
    def get_temperature(self):
        return self.temperature

    def get_humidity(self):
        return self.humidity