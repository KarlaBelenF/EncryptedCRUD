import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=3306,
            ssl_disabled=False
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
        return None