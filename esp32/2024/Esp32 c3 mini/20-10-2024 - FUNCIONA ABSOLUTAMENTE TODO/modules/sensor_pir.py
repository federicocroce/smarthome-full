######################################
import machine
from machine import Pin
import time
import networks.mqtt as mqtt
import ujson

# Función para manejar la detección de movimiento


def sensor_init(params):

    name = params.get('name', 'Unknown')
    sensor_pin = params.get('sensor_pin', 'Unknown')
    alert_pin = params.get('alert_pin', 'Unknown')
    max_reset_count = params.get('max_reset_count', 3)
    reset_peroid = params.get('reset_peroid', 10000)
    deactive_period = params.get('deactive_period', 5000)

    PIR = Pin(sensor_pin, Pin.IN)
    ALERT_STATUS = Pin(alert_pin, Pin.OUT)
    # Inicializar un temporizador
    timer = machine.Timer(-1)
    alarm_is_active = False
    count = 0
    print("sensor_init")

    def handle_motion(pin):
        nonlocal count
        nonlocal alarm_is_active
        nonlocal PIR
        nonlocal ALERT_STATUS

        client = mqtt.client
        print('client', client)
        if client:
            client.publish('sendTelegramMessage',
                           'sendTelegramMessage Sensor ' + name)

        print("handle_motion")

        def reset_alarm_count(timer):
            nonlocal count
            client = get_mqtt_client()
            if client:
                client = get_mqtt_client()
            print("Se reinicia el contador porque trancurrieron", reset_peroid)
            client.publish('sendTelegramMessage', ujson.dumps(
                {'message': "Se reinicia el contador", 'name': name}))
            count = 0

        def deactive_alarm(timer):
            nonlocal count
            nonlocal alarm_is_active
            client = get_mqtt_client()
            if client:
                client = get_mqtt_client()
            print("se desactivó la alarma porque transcurrieron", deactive_period)
            client.publish('sendTelegramMessage', ujson.dumps(
                {'message': "se desactivó la alarma porque transcurrieron", 'name': name}))
            alarm_is_active = False
            ALERT_STATUS.off()
            count = 0

    #     current_time = time.time()
    #     if current_time - last_motion_time > MIN_MOTION_DELAY:
        if pin.value() == 1:
            print("¡Movimiento detectado!")
            ALERT_STATUS.on()  # Enciende el LED
            count = count + 1
            if count == 1:
                timer.init(mode=machine.Timer.ONE_SHOT,
                           period=reset_peroid, callback=reset_alarm_count)
            if count >= max_reset_count:
                print("SUENA LA ALARMA")
                client = get_mqtt_client()
                if client:
                    client.publish('sendTelegramMessage', ujson.dumps(
                        {'message': "ALARMA ACTIVADA!!", 'name': name}))
                alarm_is_active = True
                timer.deinit()
                timer.init(mode=machine.Timer.ONE_SHOT,
                           period=deactive_period, callback=deactive_alarm)
            print("count", count)
        elif alarm_is_active == False and pin.value() != 1:
            print("No hay movimiento")
            ALERT_STATUS.off()  # Apaga el LED
    #         last_motion_time = current_time

    PIR.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_motion)
