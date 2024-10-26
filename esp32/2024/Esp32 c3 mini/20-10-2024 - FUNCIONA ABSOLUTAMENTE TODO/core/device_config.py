from core.const_led import leds_init
import urequests
import ujson


device_config = {}


def get_device(key):
    if key in device_config:
        return device_config[key]
    else:
        print("La key '{}' no existe en el diccionario.".format(key))
        return None


def get_devices_status():
    status = {}
    for key, value in device_config.items():
        if 'device' in value and 'get_status' in value['device']:
            status[key] = value['device']['get_status']()
            print(f'Clave: {key}, Valor de Device: {value["device"]}')
    return status


def update_devices_status():
    print("device_config.items()", device_config.items())
#     for key, value in device_config.items():
#         if 'device' in value and 'update_device' in value['device']:
#             value['device']["update_device"]()
#             print(f'Clave: {key}, Valor de Device: {value["device"]}')


def get_device_config():
    return device_config


def update_device_config(device_setting):
    device_config.update(device_setting)


def set_device(data):
    print('device_config', device_config)
    for key, device in device_config.items():
        value = data.get(key)
#         print("device_config", device_config)
#         print("device", device)
        if (value and device):
            device["set_value_device"](value, device["device"])


def init_config_devices():
    leds_init(update_device_config)
    
    for key, device in device_config.items():
        device["set_value_device"](None, device["device"])


def set_values_device_from_server():

    init_config_devices()

    #     firebase.setURL("https://smart-home-fc-76670-default-rtdb.firebaseio.com/")
#     print("device_config.keys()", device_config.keys())
    devices_id = ','.join(device_config.keys())
    try:
        response = urequests.get('https://www.smarthome-fc.com.ar:8443/getDevicesValue?devicesId=' +
                                 devices_id, headers={'content-type': 'application/json'})
        res = ujson.loads(response.content)

        for device_id in res.keys():
            deviceStatus = {}
            deviceStatus[device_id] = {}
            device_data = res[device_id]
            if device_data:
                for key in device_data.keys():
                    deviceStatus[device_id].update(device_data[key])
                set_device(deviceStatus)
    except OSError as e:
        print("OSError", e)
