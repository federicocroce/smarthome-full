
import network
from umqtt.robust import MQTTClient
import ssl
import ujson
import machine
from machine import Pin
from DimmerPWM import DimmerPWM
import utime as time
from UtilitiesRGB import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color
from WiFi import set_wifi, check_internet_connection



LED_WIFI = Pin(26, Pin.OUT)  # BLUE


LED_WIFI.off()

# Configurar la conexión Wi-Fi
# WiFi Setup
WIFI_SSID = "WiFi-Arnet-knt5_2,4"
WIFI_PASSWORD = "cmq3ntce"
# WIFI_SSID = "Federico's Galaxy S22 Ultra"
# WIFI_PASSWORD = "11111111"



(handle_wifi_disconnect, is_wifi_connected) = set_wifi(WIFI_SSID, WIFI_PASSWORD, LED_WIFI)

check_internet_connection()

import urequests
  
def main():
    cbk_dimmer = None

        
    while True:
        try:
            
            if is_wifi_connected():
                print("Conectado")
                
                time.sleep(0.5)
            else:
                print("ELSE")
                handle_wifi_disconnect()
        except OSError as e:
            print("OSError", e)
            reset()


if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("OSError", e)
        reset()
    except KeyboardInterrupt as e:
        _thread.interrupt(led_thread)
        print("KeyboardInterrupt Fede", e)
        reset()





# import urequests
# 
# def check_internet_connection():
#     try:
#         # Intenta hacer una solicitud a una dirección IP local (ejemplo: la dirección IP de tu router)
#         response = urequests.get('http://192.168.1.1', timeout=5)
#         response.close()
#         return True  # La solicitud tuvo éxito, por lo que hay conectividad a la red local.
#     except Exception as e:
#         return False  # La solicitud falló, lo que podría indicar la falta de acceso a Internet.
# 
# if check_internet_connection():
#     print("El ESP32 está conectado a la red local y tiene acceso a Internet.")
# else:
#     print("El ESP32 está conectado a la red local, pero podría no tener acceso a Internet.")





# import machine
# import time
# 
# # Configura el pin del sensor TCRT5000
# tcrt_pin = machine.Pin(16, machine.Pin.IN)  # Cambia el número de pin según tu configuración
# 
# flag_to_on_off = True
# is_on = False
# 
# # Función para leer el valor del sensor
# def leer_valor_tcrt():
#     return tcrt_pin.value()  # Lee el valor del pin
# 
# while True:
#     valor = leer_valor_tcrt()
# #     print(valor)
#     if valor == 0:
#         print("Nada detectado")
#         flag_to_on_off = True
#     else:
#         if flag_to_on_off == True:
#             print("Objecto detectado")
#             flag_to_on_off = False
#             is_on = not is_on
#     print("is_on", is_on)
#     time.sleep(1)
    
    
    


