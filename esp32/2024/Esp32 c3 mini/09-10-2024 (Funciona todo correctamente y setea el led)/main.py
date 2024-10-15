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
from core.const import LED_STATUS, LED_WEB_SERVER, LED_MQTT, LED_WIFI
from core.mqtt_config import init_mqtt
from networks.wifi import set_wifi, check_internet_connection
from networks.mqtt import set_mqtt, get_mqtt, reset_mqtt, get_mqtt_client
from utilities.delay import delay_seconds
from core.device_config import set_values_device_from_server, update_devices_status, init_config_devices
from modules.touch_sensor import Touch as TouchSensor
import networks.wifimgr as wifimgr
import utime
from modules.sensor_pir import sensor_init
from utilities.mode import get_is_local_mode
from utilities.custom_button import set_custom_button


import _thread
import urequests

# touch_dimmer_sensor = TouchSensor(TOUCH_DIMER_SENSOR_PIN)

LED_WEB_SERVER.off()
LED_WIFI.off()
LED_MQTT.off()
LED_STATUS.off()

# # # Configurar los detalles del broker MQTT
# mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
# mqtt_port = 8883  # Puerto predeterminado para MQTT
# mqtt_user = "fcroce"
# mqtt_password = "34023936Fc"

# # Nombre de cliente MQTT
# client_id = "esp32_client"

set_custom_button()

is_local_mode = get_is_local_mode()

if is_local_mode == True:
    init_config_devices()
    LED_WEB_SERVER.on()
    LED_MQTT.on()
    LED_WIFI.on()

else:

    wifi_manager = wifimgr.get_connection(LED_WEB_SERVER, LED_WIFI)
    if wifi_manager is None:
        print("Could not initialize the network connection.")
        while True:
            pass  # you shall not pass :D

    (wlan_sta, is_wifi_connected, handle_wifi_connection,
     is_wifi_network_connected) = wifi_manager

    # SENSOR DE ALARMA, NO ELIMINAR
    # sensor_init({'name': 'sensor Pir prueba', 'sensor_pin': 34, 'alert_pin': 15})

    set_values_device_from_server()

    mqtt = init_mqtt()


def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()


def main():
    client = get_mqtt_client()

    def keep_mqtt_connection_cbk():
        update_devices_status()
        client.publish('reconnect', "Wifi y MQTT reconectado")

#     nonlocal mqtt
    while True:
        try:
            if is_wifi_network_connected():
                mqtt["keep_mqtt_connection"](keep_mqtt_connection_cbk)
                time.sleep(5)
            else:
                mqtt["pause_mqtt"]()
                handle_wifi_connection()
        except OSError as e:
            print("OSError", e)
            reset()


if __name__ == "__main__":
    try:
        if not is_local_mode:
            main()
    except OSError as e:
        print("OSError", e)
        reset()
    except KeyboardInterrupt as e:
        #         _thread.interrupt(led_thread)
        #         _thread.interrupt(internet_thread)
        print("KeyboardInterrupt Fede", e)
        reset()



