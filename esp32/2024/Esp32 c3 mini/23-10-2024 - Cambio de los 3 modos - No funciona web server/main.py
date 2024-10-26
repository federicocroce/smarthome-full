# from networks.webserver import run_web_server
# 
# run_web_server()
# 

import machine
import time

from core.const import LED_STATUS, LED_WEB_SERVER, LED_MQTT, LED_WIFI
# from core.mqtt_config import init_mqtt
from utilities.mode import is_wifi_mode
from utilities.custom_button import set_custom_button
from networks.network_manager import network_manager



# SSID = 'WiFi-Arnet-knt5_2,4'
# PASSWORD = 'cmq3ntce'

# SSID = "Federico's Galaxy S22 Ultra"
# PASSWORD = '11111111'

LED_WEB_SERVER.off()
LED_WIFI.off()
LED_MQTT.off()
LED_STATUS.off()

set_custom_button()
network_manager()

# print("MODE IS LOCAL", is_local_mode)
# 
# if is_local_mode:
# #     init_config_devices()
# #     LED_WEB_SERVER.on()
# #     LED_MQTT.on()
# #     LED_WIFI.on()
# else:
#     network_manager()

#     wifi.init_wifi(SSID, PASSWORD, LED_WIFI)
#     
#     if wifi.check_connection() is False:
#         print("Could not initialize the network connection.")
#         while True:
#             pass  # you shall not pass :D
# 
#     set_values_device_from_server()
#     init_mqtt()


def main():
    from core.device_config import update_devices_status
    from utilities.common import reset_device
    from networks.wifi import check_connection
    from networks.mqtt import keep_mqtt_connection, queue_put, pause_mqtt
#     import networks.wifi as wifi
#     import networks.mqtt as mqtt

    def keep_mqtt_connection_cbk():
        update_devices_status()
        queue_put('reconnect', "Wifi y MQTT reconectado")
    while True:
        try:
            time.sleep(1)
            if check_connection():
                keep_mqtt_connection(keep_mqtt_connection_cbk)
            else:
                pause_mqtt()
        except OSError as e:
            print("OSError", e)
            reset_device()


if __name__ == "__main__":
    try:
        if is_wifi_mode:
            main()
    except OSError as e:
        print("OSError", e)
        reset_device()
    except KeyboardInterrupt as e:
        print("KeyboardInterrupt Fede", e)
        reset_device()
