import os
from datetime import datetime

def guardar(pregunta, respuesta):
    # Obtener la ruta del directorio del script actual
    directorio_actual = os.path.dirname(__file__)

    # Nombre del directorio donde se guardarán los archivos
    directorio = "respuestas_asistente"

    # Crear la ruta completa del directorio
    ruta_directorio = os.path.join(directorio_actual, directorio)

    # Crear el directorio si no existe
    if not os.path.exists(ruta_directorio):
        os.makedirs(ruta_directorio)

    # Obtener la fecha y hora actual
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construir el nombre del archivo con la fecha actual
    nombre_archivo = f"conversacion_{fecha_actual}.txt"

    # Ruta completa del archivo
    ruta_archivo = os.path.join(ruta_directorio, nombre_archivo)

    # Escribir la pregunta y la respuesta en el archivo
    with open(ruta_archivo, "a") as file:
        file.write(f"Pregunta: {pregunta}\n")
        file.write(f"Respuesta: {respuesta}\n")
        file.write("\n")
