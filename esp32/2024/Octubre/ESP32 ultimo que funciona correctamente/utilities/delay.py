import machine
import utime


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
