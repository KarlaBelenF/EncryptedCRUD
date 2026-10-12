import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import date

# Lee mi archivo .env y carga las variables en memoria
load_dotenv()

app = FastAPI() #Crea un servidor web que escucha peticiones HTTP y devuelve respuestas HTTP.
 
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
        print(f"Error al conectar: {err}")
        return None

# Definimos un modelo de datos para la creación de usuarios, que será usado para validar los datos que el frontend envíe al backend
# No pedimos id porque la base de datos lo genera automáticamente ni estado porque por default es true
class UsuarioCrear(BaseModel):
    nombre: str
    apellidoPaterno: str
    apellidoMaterno: str
    rol: str
    correoElectronico: str
    telefono: str
    fechaNacimiento: date
    direccion: str
    rfc: str
    contrasenia: str
    numeroCuenta: str
    cvv: str
    nip: str

@app.post("/usuarios/crear") # Cuando el frontend haga una petición POST a la ruta /usuarios/crear, se ejecutará la función crear_usuario()
def crear_usuario(usuario: UsuarioCrear):
    conexion = obtener_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = conexion.cursor() # Un cursor es un objeto que nos permite ejecutar sentencias SQL en la base de datos
        
        # SHA2() y AES_ENCRYPT() se ejecutan directamente en el motor de la base de datos de Azure
        sql = """
            INSERT INTO usuarios (
                nombre, apellidoPaterno, apellidoMaterno, rol, correoElectronico, telefono, 
                fechaNacimiento, direccion, rfc, contrasenia, numeroCuenta, cvv, nip
            ) VALUES (
                %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, 
                SHA2(%s, 256), 
                AES_ENCRYPT(%s, 'MesaVerdeSecretKey'), 
                AES_ENCRYPT(%s, 'MesaVerdeSecretKey'), 
                AES_ENCRYPT(%s, 'MesaVerdeSecretKey')
            )
        """
        
        valores = (
            usuario.nombre, usuario.apellidoPaterno, usuario.apellidoMaterno, usuario.rol, 
            usuario.correoElectronico, usuario.telefono, usuario.fechaNacimiento, 
            usuario.direccion, usuario.rfc, 
            usuario.contrasenia, # Se irá al %s de SHA2
            usuario.numeroCuenta, # Se irá al %s de AES_ENCRYPT
            usuario.cvv,          # Se irá al %s de AES_ENCRYPT
            usuario.nip     # Se irá al %s de AES_ENCRYPT
        )
        
        cursor.execute(sql, valores) # Mandamos la sentencia SQL y los valores separados por seguridad, para evitar inyecciones SQL.
        conexion.commit() # Para que los cambios se guarden en la base de datos. Si no se hace, los cambios se perderán al cerrar la conexión.
        
        return {"status": "success", "mensaje": "Usuario creado y datos encriptados correctamente"}
        
    except mysql.connector.Error as err: # Si hay un error al ejecutar la sentencia SQL, devolvemos un error 400 al frontend
        raise HTTPException(status_code=400, detail=f"Error al guardar: {err}") # error 400 significa que la petición del cliente es incorrecta, en este caso porque los datos que envió no cumplen con las reglas de la base de datos
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.get("/usuarios") # Cuando el frontend haga una petición GET a la ruta /usuarios, se ejecutará la función obtener_usuarios()
def obtener_usuarios(rol_solicitante: str):
    conexion = obtener_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cursor = conexion.cursor(dictionary=True) # dictionary es un parámetro que hace que el cursor devuelva los resultados como diccionarios en lugar de tuplas. Esto facilita el acceso a los datos por nombre de columna.

        # Usamos AES_DECRYPT con la misma llave y casteamos a CHAR porque AES_DECRYPT devuelve datos binarios
        sql = """
            SELECT 
                id, nombre, apellidoPaterno, apellidoMaterno, rol, correoElectronico, 
                telefono, fechaNacimiento, direccion, rfc, estatus,
                CAST(AES_DECRYPT(numeroCuenta, 'MesaVerdeSecretKey') AS CHAR) as numeroCuenta,
                CAST(AES_DECRYPT(cvv, 'MesaVerdeSecretKey') AS CHAR) as cvv,
                CAST(AES_DECRYPT(nip, 'MesaVerdeSecretKey') AS CHAR) as nip
            FROM usuarios
        """
        
        cursor.execute(sql)
        usuarios = cursor.fetchall() # devuelve todos los resultados de la consulta como una lista de diccionarios, donde cada diccionario representa un usuario.
        
        # Si el rol del solicitante es "empleado", ocultamos los datos sensibles de los usuarios antes de enviarlos al frontend
        if rol_solicitante == "empleado":
            for usuario in usuarios:
                usuario["numeroCuenta"] = "PROTEGIDO"
                usuario["cvv"] = "***"
                usuario["nip"] = "****"
                
        return {"status": "success", "data": usuarios} # Retorna JSON con los datos de los usuarios al frontend
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {err}")
    finally:
        if conexion.is_connected(): 
            cursor.close()
            conexion.close()

@app.get("/test-db") # Cuando el frontend haga una petición GET a la ruta /test-db, se ejecutará la función probar_conexion()
def probar_conexion():
    conexion = obtener_conexion()
    
    # Si la conexión es exitosa, cerramos la conexión y devolvemos un mensaje de éxito
    if conexion and conexion.is_connected():
        conexion.close()
        return {"status": "success", "mensaje": "Conexion a la base de datos exitosa"} # Retorna JSON con un mensaje de éxito al frontend
    
    # Si falla, mandamos un error 500 al frontend
    raise HTTPException(status_code=500, detail="Error conectando a la base de datos")

#uvicorn main:app --reload