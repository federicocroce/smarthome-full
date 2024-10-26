

from utilities.common import get_core_data
from utilities.mode import is_wbserver_mode, is_wifi_mode, is_local_mode
from core.const import on_led_core


def network_manager():
    
    core_data = get_core_data()
    
    SSID = core_data.get("ssid", '')
    PASSWORD = core_data.get("password", '')
#     
#     print("is_wifi_mode", is_wifi_mode())
#     print("is_wbserver_mode", is_wbserver_mode())
#     print("is_local_mode", is_local_mode())

    if is_wifi_mode():
        if SSID and PASSWORD:
            from . import wifi
            from core.mqtt_config import init_mqtt
            from core.device_config import set_values_device_from_server
            from core.const import LED_WIFI

            wifi.init_wifi(SSID, PASSWORD, LED_WIFI)
            
            if wifi.check_connection() is False:
                print("Could not initialize the network connection.")
                while True:
                    pass  # you shall not pass :D

            set_values_device_from_server()
            init_mqtt()
    elif is_wbserver_mode():
        from networks.webserver import run_web_server
        run_web_server()
    else:
        from core.device_config import init_config_devices
        init_config_devices()
        on_led_core()
    
#     return(SSID, PASSWORD)
    
#     if SSID and PASSWORD:
#         return (SSID, PASSWORD)
#     else:
#         webserver.run_web_server()
        
        
