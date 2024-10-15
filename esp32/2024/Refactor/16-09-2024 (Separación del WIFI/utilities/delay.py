import machine
import utime

from time import ticks_add, ticks_ms, ticks_diff

# def delay_init():
#     limit_time = 0
#         
#     def set_delay(cbk, limit_time_ms):
#         nonlocal limit_time
#         if(ticks_diff(limit_time, ticks_ms()) <= 0):
#             cbk()
#             limit_time = ticks_add(ticks_ms(), limit_time_ms)
#             
#     return set_delay


# def delay_seconds(callback, seconds):
#     # Convierte segundos a microsegundos
#     microseconds = seconds * 1000000
#     start_time = utime.ticks_us()

#     while True:
#         current_time = utime.ticks_us()
#         elapsed_time = utime.ticks_diff(current_time, start_time)

#         if elapsed_time >= microseconds:
#             break

#         # Realiza otras tareas aquí si es necesario
#         if callback is not None:
#             callback()

#         # Pequeña pausa para no ocupar completamente la CPU
#         utime.sleep_us(100)


def delay_seconds(callback, seconds):
    # Convierte segundos a milisegundos
    milliseconds = seconds * 1000
    # Obtiene el tiempo de inicio
    start_time = utime.ticks_ms()

    # Realiza el retraso
    while utime.ticks_diff(utime.ticks_ms(), start_time) < milliseconds:
        pass

    if callback is not None:
        callback()


# def delay_seconds(callback, seconds):
#     # Convierte segundos a milisegundos
#     milliseconds = seconds * 1000
#     # Obtiene el tiempo de inicio
#     start_time = ticks_ms()

#     # Realiza el retraso
#     while ticks_diff(ticks_ms(), start_time) < milliseconds:
#         pass
#     if callback is not None:
#         callback()
 
 
# Implementación:

#led_red = Pin(32, Pin.OUT)

#delay = delay_init()
# while True:
#     delay(lambda:led_red.value(not led_red.value()) , 50)