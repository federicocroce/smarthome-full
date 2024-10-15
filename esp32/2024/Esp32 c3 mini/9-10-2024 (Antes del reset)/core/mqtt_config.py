
from networks.mqtt import set_mqtt, get_mqtt_client
from core.const import LED_MQTT
from core.device_config import set_device, get_devices_status
import ujson


# # Configurar los detalles del broker MQTT
mqtt_server = "afdc512217a942639f02c4cf4cce5fd0.s1.eu.hivemq.cloud"
mqtt_port = 8883  # Puerto predeterminado para MQTT
mqtt_user = "fcroce"
mqtt_password = "34023936Fc"

# Nombre de cliente MQTT
client_id = "esp32_client"

# Callback que se llama cuando se recibe un mensaje MQTT


def callbackMQTT(topic, msg):
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

def init_mqtt():
    return set_mqtt(client_id, mqtt_server, mqtt_user, mqtt_password, [
                "mi_topic", "device_status"], callbackMQTT, LED_MQTT)
