import network
from umqtt.robust import MQTTClient
import ssl
import ujson
import usocket as socket
import ure
import machine
from machine import Pin
from utilities.dimmer_pwm import DimmerPWM
import utime as time
from utilities.utilities_rgb import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color
from network.WiFi import set_wifi, check_internet_connection
from network.MQTT import set_mqtt, get_mqtt, reset_mqtt, get_mqtt_client
from utilities.Delay import delay_seconds
from core.device_config import set_device, init_device, device_config, get_device, get_devices_status, update_devices_status
from modules.touch_sensor import Touch as TouchSensor
import network.wifimgr as wifimgr
import utime
from modules.Sensor_PIR import sensor_init

import _thread
import urequests

LED_STATUS = Pin(2, Pin.OUT)
LED_WEB_SERVER = Pin(25, Pin.OUT)  # GREEN
LED_MQTT = Pin(27, Pin.OUT)  # RED
LED_WIFI = Pin(26, Pin.OUT)  # BLUE
INFRA = Pin(16, Pin.IN)

# touch_decrease = TouchSensor(15)
touch_dimmer_sensor = TouchSensor(13)
# sensor_init('sensor Pir prueba',34, 15)

LED_WEB_SERVER.off()
LED_WIFI.off()
LED_MQTT.off()

# Configurar la conexión Wi-Fi
# WiFi Setup
# WIFI_SSID = "Fibertel WiFi828 2.4GHz"
# WIFI_PASSWORD = "00434023936"
# WIFI_SSID = "WiFi-Arnet-knt5_2,4"
# WIFI_PASSWORD = "cmq3ntce"
# WIFI_SSID = "Federico's Galaxy S22 Ultra"
# WIFI_PASSWORD = "11111111"
# WIFI_SSID = "DAT 4479"
# WIFI_PASSWORD = "
#
# # Configurar los detalles del broker MQTT
mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
mqtt_port = 8883  # Puerto predeterminado para MQTT
mqtt_user = "fcroce"
mqtt_password = "34023936Fc"

# Nombre de cliente MQTT
client_id = "esp32_client"

wifi_manager = wifimgr.get_connection(LED_WEB_SERVER, LED_WIFI)
if wifi_manager is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


# print("wifi_manager from main", wifi_manager)
(wlan_sta, is_wifi_connected, handle_wifi_connection,
 is_wifi_network_connected) = wifi_manager
# print("is_wifi_connected from main", is_wifi_connected)

# SENSORCDE ALARMA, NO ELIMINAR
# sensor_init({'name': 'sensor Pir prueba', 'sensor_pin': 34, 'alert_pin': 15})


# Callback que se llama cuando se recibe un mensaje MQTT
def callback(topic, msg):
    print("Mensaje recibido: Topic = {}, Mensaje = {}".format(topic, msg))

    try:
        # Intentar decodificar el JSON
        topic_formatted = str(topic, 'utf-8')

        print("topic_formatted", topic_formatted)

        if topic_formatted == "mi_topic":
            data = ujson.loads(msg)
            set_device(data)
        if topic_formatted == "device_status":
            print("get_device", get_devices_status())
            data = get_devices_status()
            print("get_status", data)
            client = get_mqtt_client()
            client.publish('status', ujson.dumps(data))

    except ValueError:
        # Si no es un JSON válido, imprimir el mensaje como texto simple
        print('Mensaje recibido ERROR:', msg.decode('utf-8'))
    except KeyError as e:
        # Si hay un error al intentar acceder a un atributo de led1_data
        print('Error: No se pudo acceder al atributo de LED1 -', e)


# (handle_wifi_disconnect, is_wifi_connected) = set_wifi(WIFI_SSID, WIFI_PASSWORD, LED_WIFI)
init_device()

mqtt = set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password, [
                "mi_topic", "device_status"], callback, LED_MQTT)


# send_message("Fede")


def dimmer_led():
    print("Setea el brillo")
    while True:
        try:
            device_config['led1']['device']['dimmer_touch'](
                touch_dimmer_sensor)
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
    client = get_mqtt_client()

    def keep_mqtt_connection_cbk():
        update_devices_status()
        client.publish('reconnect', "Wifi y MQTT reconectado")

#     nonlocal mqtt
    while True:
        try:
            if is_wifi_network_connected():
                mqtt["keep_mqtt_connection"](keep_mqtt_connection_cbk)
                time.sleep(1)
            else:
                mqtt["pause_mqtt"]()
                handle_wifi_connection()
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
#         _thread.interrupt(internet_thread)
        print("KeyboardInterrupt Fede", e)
        reset()


######################################


# import machine
# import utime
#
# Tiempo de espera para considerar que se ha pulsado el botón por 3 segundos
# RESET_THRESHOLD = 3000  # en milisegundos
#
# # Configuración del pin del botón de reset
# reset_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
#
# # Función para detectar el reset prolongado
# def detect_reset_long_press(pin):
#     start_time = utime.ticks_ms()
#     while reset_pin.value() == 0:  # Espera hasta que el botón de reset se suelte
#         if utime.ticks_diff(utime.ticks_ms(), start_time) >= RESET_THRESHOLD:
#             print("Reset")
#             return
#     print("No reset")
#
# # Configura una interrupción para detectar la pulsación del botón de reset
# reset_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=detect_reset_long_press)
#
# # Bucle principal
# while True:
#     utime.sleep(1)  # Espera un segundo antes de volver a comprobar la interrupción
#
#
# detect_reset_long_press


######################################


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
# import utime as time
#
# # Configurar el pin táctil
# touch_pin = Pin(13, Pin.IN)
#
# print("¡Touch detectado!")

# Definir la sensibilidad (ajustar según sea necesario)
# sensibilidad = 500

# Configurar el umbral de detección
# umbral = 1000

# Ajustar la sensibilidad del TouchPad
# touch_pin.config(sensibilidad)

# Leer el valor del TouchPad


# # Verificar si se ha tocado el TouchPad
# if valor_touch < umbral:
#     print("¡Touch detectado!")
#

# while True:
#     try: #Try getting Touch state
#         print("Entra")
#         if(touch_pin.value() < 1):
#             print("Es menor a 1")
#         else:
#             print("Es mayor a 1")
#         print(touch_pin.value())
#     except: #If error, return True
#         print('ERROR', touch_pin)
#
#     time.sleep(0.5)
#
