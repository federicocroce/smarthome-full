#!/bin/bash

# Verificar si hay procesos de node en ejecución
if pgrep -x "node" >/dev/null; then
  echo "Hay procesos de node en ejecución. Deteniendo..."
  # Ejecutar el comando killall node para detener todos los procesos de node
  killall node
else
  echo "No hay procesos de node en ejecución."
fi
