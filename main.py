import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Esto lee tu archivo .env y carga las variables en memoria
load_dotenv()

app = FastAPI()

# Función reutilizable para conectarnos a la base de datos
def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Error al conectar: {err}")
        return None

@app.get("/test-db")
def probar_conexion():
    conexion = obtener_conexion()
    
    # Verificamos si la conexión fue exitosa
    if conexion and conexion.is_connected():
        conexion.close() # Siempre hay que cerrar la puerta al terminar
        return {"status": "success", "mensaje": "¡Conexión exitosa a Mesa Verde en Azure!"}
    
    # Si falla, le mandamos un error 500 al frontend
    raise HTTPException(status_code=500, detail="Error conectando a la base de datos")