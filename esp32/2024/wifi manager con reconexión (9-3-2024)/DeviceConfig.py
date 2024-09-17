from UtilitiesRGB import spectrumrgb_to_rgb_limit_100, configurar_temperatura_color, format_led_rgb
import Ufirebase as firebase
import urequests
import ujson

def config_led_rgb(led_data, led_device):
    print("led_device",led_device)
    print("led_data",led_data)
    
    if led_data:
        brightness = led_data.get('brightness')
        spectrumrgb = led_data.get('color', {}).get('spectrumRGB')
        color_name = led_data.get('color', {}).get('name')
        temperature = led_data.get('color', {}).get('temperature')
        is_on = led_data.get('on')
#         print('Brightness:', brightness)
#         print('Color:', spectrumrgb)
#         print('Is On:', is_on)
        
#         (red, green, blue) = led_device['led']
        
#         color_red, color_green, color_blue = 0, 0, 0
        if color_name == 'blanco':
            spectrumrgb = 16777215
            
        led_device['set_led_values'](spectrumrgb, brightness, is_on, temperature)
        
        
#         if not spectrumrgb and temperature:
#             color_red, color_green, color_blue = configurar_temperatura_color(temperature)
#         else:
#             color_red, color_green, color_blue = spectrumrgb_to_rgb_limit_100(
#                 spectrumrgb, brightness)
#         print('red, green, blue', color_red, color_green, color_blue)
#         red.set_dimmer(color_red, is_on)
#         green.set_dimmer(color_green, is_on)
#         blue.set_dimmer(color_blue, is_on)

    


device_config = {
    'led1': {
        'device': format_led_rgb(5, 18, 19, 'led1'),
        'set_value_device': config_led_rgb
    },
}


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
    for key, value in device_config.items():
        if 'device' in value and 'update_device' in value['device']:
            value['device']["update_device"]()
            print(f'Clave: {key}, Valor de Device: {value["device"]}')

def get_device_config():
    return device_config

#Refactorizar, se debe hacer el for en device_config y no en data.items()
def set_device(data): 
    print('device_config', device_config)
    for key, value in data.items():
        device = device_config.get(key)
        print("device_config",device_config)
        print("device", device)
        if(value and device):
            device["set_value_device"](value, device["device"])  



def init_device():
#     firebase.setURL("https://smart-home-fc-76670-default-rtdb.firebaseio.com/")
    devices_id = {"devicesId":[key for key in device_config.keys()]}
    params_json = ujson.dumps(devices_id)
    try:
        response = urequests.get('https://www.smarthome-fc.com.ar:8443/getAllDevices', headers = {'content-type': 'application/json'}, data=params_json)
        res = ujson.loads(response.content)
#         print("res", res)
        
        for device_id in res.keys():
            deviceStatus = {}
            deviceStatus[device_id] = {}
#             print('init_device 1', deviceStatus)
    #         firebase.get(device_id, device_id, bg=False, id=0, cb=None, limit=False)
            device_data = res[device_id]
            print('init_device 2', device_data)
            for key in device_data.keys():
                deviceStatus[device_id].update(device_data[key])
            print("deviceStatus", deviceStatus)
            set_device(deviceStatus)	
    except OSError as e:
        print("OSError", e)
        
# def init_device():
#     firebase.setURL("https://smart-home-fc-76670-default-rtdb.firebaseio.com/")
#     devices_id = device_config.keys()
#     
#     for device_id in devices_id:
#         deviceStatus = {}
#         deviceStatus[device_id] = {}
#         print('init_device 1')
#         firebase.get(device_id, device_id, bg=False, id=0, cb=None, limit=False)
#         device_data = getattr(firebase, device_id, None)
#         print('init_device 2')
#         for key in device_data.keys():
#             deviceStatus[device_id].update(device_data[key])
#         print(deviceStatus)
#         set_device(deviceStatus)

    
    