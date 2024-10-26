

from utilities.common import update_core_data, get_core_data, reset_device

def network_manager():
    
    core_data = get_core_data()
    
    SSID = core_data.get("ssid", '')
    PASSWORD = core_data.get("password", '')
    
    
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
    else:
        from . import webserver
        webserver.run_web_server()
    
#     return(SSID, PASSWORD)
    
#     if SSID and PASSWORD:
#         return (SSID, PASSWORD)
#     else:
#         webserver.run_web_server()
        
        
