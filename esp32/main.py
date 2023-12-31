
import network
from umqtt.robust import MQTTClient
import ssl
import ujson
import machine
from machine import Pin
from DimmerPWM import DimmerPWM
import utime as time
from UtilitiesRGB import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color
from WiFi import set_wifi, get_wifi
# import WiFi
from MQTT import connect_mqtt
from Delay import delay_seconds
from DeviceConfig import set_device, init_device, device_config
from Touch import Touch
import _thread
# import Ufirebase as firebase
# import urequests


LED_STATUS = Pin(2, Pin.OUT)
LED_MQTT = Pin(27, Pin.OUT)  # RED
LED_WIFI = Pin(26, Pin.OUT)  # BLUE
INFRA = Pin(16, Pin.IN)

touch_increase = Touch(15)
touch_decrease = Touch(4)

LED_WIFI.off()
LED_MQTT.off()

# device_config = get_device_config()

# Configurar la conexión Wi-Fi
# WiFi Setup
# WIFI_SSID = "WiFi-Arnet-knt5_2,4"
# WIFI_PASSWORD = "cmq3ntce"
WIFI_SSID = "Federico's Galaxy S22 Ultra"
WIFI_PASSWORD = "11111111"

# Configurar los detalles del broker MQTT
mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
mqtt_port = 8883  # Puerto predeterminado para MQTT
mqtt_user = "fcroce"
mqtt_password = "34023936Fc"

# Nombre de cliente MQTT
client_id = "esp32_client"

# def verificar_conexion_mqtt(client, COUNT):
#     try:
#         client.ping()
#         print("Conexión MQTT activa", COUNT)
#         return True
#     except OSError as e:
#         print("Error en la conexión MQTT:", e)
#         LED_MQTT.off()
#         return False

# firebase.setURL("https://smart-home-fc-76670-default-rtdb.firebaseio.com/")
# firebase.patch("led1", {"Brightness": {"brightness": 1}}, bg=False, id=1, cb=None)
# print("Setea el brillo")


# def dimmer_led():
#     firebase.patch("led1", {"Brightness": {"brightness": 1}}, bg=False, id=100, cb=None)
#     print("Setea el brillo")
#     try:
#         device_config['led1']['device']['increase_decrease_touch'](touch_increase, touch_decrease)
#         time.sleep_ms(20)
#     except KeyboardInterrupt:
#         print("\nBucle interrumpido por el usuario.")

# dimmer_led()

# Callback que se llama cuando se recibe un mensaje MQTT
def callback(topic, msg):
    print("Mensaje recibido: Topic = {}, Mensaje = {}".format(topic, msg))
    try:
        # Intentar decodificar el JSON
        data = ujson.loads(msg)
        print('DATA:', data)
        set_device(data)

    except ValueError:
        # Si no es un JSON válido, imprimir el mensaje como texto simple
        print('Mensaje recibido:', msg.decode('utf-8'))
    except KeyError as e:
        # Si hay un error al intentar acceder a un atributo de led1_data
        print('Error: No se pudo acceder al atributo de LED1 -', e)


(handle_wifi_disconnect, is_wifi_connected) = set_wifi(WIFI_SSID, WIFI_PASSWORD, LED_WIFI)

# response = urequests.get('http://23.22.177.181:3000/')
# 
# print(response.content)


init_device()

# ssl_params["cert_reqs"] = ssl.CERT_REQUIRED
# ssl_params = dict()
# # ssl_params["cadata"] = CERTIFICATE
# ssl_params["server_hostname"] = mqtt_server
# Conectar al broker MQTT
(mqtt_client, check_mqtt_connection, reconnect_mqtt, update_device) = connect_mqtt(
    client_id, mqtt_server, mqtt_user, mqtt_password, LED_MQTT)

# Establecer la función de callback
mqtt_client.set_callback(callback)


# Suscribirse a un topic
mqtt_topic = "mi_topic"
mqtt_client.subscribe(mqtt_topic)

# Publicar un mensaje
# mqtt_client.publish(mqtt_topic, "Hola desde ESP32")
# mqtt_client.publish("get_devices_state", ujson.dumps(["led1"]))


def dimmer_led():
#     firebase.patch("led1", {"Brightness": {"brightness": 50}}, bg=False, id=1, cb=None)
    print("Setea el brillo")
    mqtt_client.publish(mqtt_topic, "Hola desde ESP32")
    while True:
        try:
#             print('Entra #al thread', device_config['led1']['device']['increase_decrease_touch'])
            # Controla la intensidad del LED
            device_config['led1']['device']['increase_decrease_touch'](touch_increase, touch_decrease, update_device)
            time.sleep_ms(20)
        except KeyboardInterrupt:
            print("\nBucle interrumpido por el usuario.")

led_thread = _thread.start_new_thread(dimmer_led, ())


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()

def main():
    cbk_dimmer = None
    COUNT = 0
    # nonlocal mqtt_client
    while True:
        try:
            # Check for MQTT messages and perform non-blocking tasks
            if is_wifi_connected():
                print("is_wifi_connected()", is_wifi_connected())
                # if COUNT == 0 and not mqtt_client.ping():
                #    reset()
#                 delay_seconds(dimmer_led, 0.5)
                check_mqtt_connection()
                mqtt_client.check_msg()
                # mqtt_client.wait_msg()
#                 print("Check msg", COUNT)
                COUNT = COUNT + 1                
                time.sleep(0.5)
            else:
                print("ELSE")
                COUNT = 0
                handle_wifi_disconnect()
        except OSError as e:
            print("OSError", e)
            handle_wifi_disconnect()


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

# while True:
#     # print('Entra 1')
#     try:
#         # print('Entra 2')
#         # time.sleep(0.01)
#         # current_time = time.time()
#         if not is_wifi_connected():

#             handle_wifi_disconnect()

#         else:
#             try:
#                 # Verificar si


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
    
    
    

# from machine import Pin
# 
# red = Pin(5, Pin.OUT) 
# green = Pin(18, Pin.OUT)
# blue = Pin(19, Pin.OUT)  
# 
# red.on()
# green.on()
# blue.on()
    