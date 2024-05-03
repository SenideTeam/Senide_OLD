# guardar_respuesta.py

import os
from datetime import datetime

# Lista para almacenar las conversaciones durante la ejecución del programa
conversaciones_temporales = []

def guardar_conversacion_temporal(pregunta, respuesta):
    conversaciones_temporales.append((pregunta, respuesta))

def guardar_conversaciones_en_archivo():
    directorio_actual = os.path.dirname(__file__)
    directorio = "respuestas_asistente"
    ruta_directorio = os.path.join(directorio_actual, directorio)

    if not os.path.exists(ruta_directorio):
        os.makedirs(ruta_directorio)

    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"conversacion_{fecha_actual}.txt"
    ruta_archivo = os.path.join(ruta_directorio, nombre_archivo)

    with open(ruta_archivo, "a", encoding="utf-8") as file:
        for pregunta, respuesta in conversaciones_temporales:
            file.write(f"Pregunta: {pregunta}\n")
            file.write(f"Respuesta: {respuesta}\n\n")
