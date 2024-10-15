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
from networks.wifi import set_wifi, check_internet_connection
from networks.mqtt import set_mqtt, get_mqtt, reset_mqtt, get_mqtt_client
from utilities.delay import delay_seconds
from core.device_config import set_device, init_device, device_config, get_device, get_devices_status, update_devices_status
from core.mqtt_config import mqtt
from core.const import LED_STATUS, LED_WEB_SERVER, LED_MQTT, LED_WIFI, TOUCH_DIMER_SENSOR_PIN
from modules.touch_sensor import Touch as TouchSensor
import networks.wifimgr as wifimgr
import utime
from modules.sensor_pir import sensor_init

import _thread
import urequests

touch_dimmer_sensor = TouchSensor(TOUCH_DIMER_SENSOR_PIN)

LED_WEB_SERVER.off()
LED_WIFI.off()
LED_MQTT.off()


# # # Configurar los detalles del broker MQTT
# mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
# mqtt_port = 8883  # Puerto predeterminado para MQTT
# mqtt_user = "fcroce"
# mqtt_password = "34023936Fc"

# # Nombre de cliente MQTT
# client_id = "esp32_client"

wifi_manager = wifimgr.get_connection(LED_WEB_SERVER, LED_WIFI)
if wifi_manager is None:
    print("Could not initialize the network connection.")
    while True:
        pass  # you shall not pass :D


(wlan_sta, is_wifi_connected, handle_wifi_connection,
 is_wifi_network_connected) = wifi_manager

# SENSOR DE ALARMA, NO ELIMINAR
# sensor_init({'name': 'sensor Pir prueba', 'sensor_pin': 34, 'alert_pin': 15})

init_device()

# # Callback que se llama cuando se recibe un mensaje MQTT
# def callbackMQTT(topic, msg):
#     print("Mensaje recibido: Topic = {}, Mensaje = {}".format(topic, msg))

#     try:
#         # Intentar decodificar el JSON
#         topic_formatted = str(topic, 'utf-8')

#         print("topic_formatted", topic_formatted)

#         if topic_formatted == "mi_topic":
#             data = ujson.loads(msg)
#             set_device(data)
#         if topic_formatted == "device_status":
#             print("get_device", get_devices_status())
#             data = get_devices_status()
#             print("get_status", data)
#             client = get_mqtt_client()
#             client.publish('status', ujson.dumps(data))

#     except ValueError:
#         # Si no es un JSON válido, imprimir el mensaje como texto simple
#         print('Mensaje recibido ERROR:', msg.decode('utf-8'))
#     except KeyError as e:
#         # Si hay un error al intentar acceder a un atributo de led1_data
#         print('Error: No se pudo acceder al atributo de LED1 -', e)


# # (handle_wifi_disconnect, is_wifi_connected) = set_wifi(WIFI_SSID, WIFI_PASSWORD, LED_WIFI)


# mqtt = set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password, [
#                 "mi_topic", "device_status"], callbackMQTT, LED_MQTT)


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
