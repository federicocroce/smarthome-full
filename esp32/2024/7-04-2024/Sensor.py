######################################
import machine
from machine import Pin, 
import time

# Función para manejar la detección de movimiento
def sensor_init(name, sensor_pin, alert_pin, max_reset_count=3, reset_peroid=10000, deactive_period=5000):
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
        
        print("handle_motion")
        def reset_alarm_count(timer):
            nonlocal count
            print("Se reinicia el contador porque trancurrieron", reset_peroid)
            count = 0
            
        def deactive_alarm(timer):
            nonlocal count
            nonlocal alarm_is_active
            print("se desactivó la alarma porque transcurrieron", deactive_period)
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
                timer.init(mode=machine.Timer.ONE_SHOT, period=reset_peroid, callback=reset_alarm_count)
            if count >= max_reset_count:
                print("SUENA LA ALARMA")
                alarm_is_active = True
                timer.deinit()
                timer.init(mode=machine.Timer.ONE_SHOT, period=deactive_period, callback=deactive_alarm)
            print("count", count)
        elif alarm_is_active == False and pin.value() != 1:
            print("No hay movimiento")
            ALERT_STATUS.off()  # Apaga el LED
    #         last_motion_time = current_time
            
    PIR.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_motion)


