import os
import mysql.connector
from dotenv import load_dotenv

# Lee mi archivo .env y carga las variables en memoria
load_dotenv()

# Nos conectamos a la base de datos usando las variables de entorno que cargamos desde el archivo .env
def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conexion
    except mysql.connector.Error as err: #Si hay un error al conectar, lo imprime en consola y devuelve None
        print(f"Error al conectar: {err}") # f es para formatear el string y mostrar el error
        return None