from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from database import obtener_conexion
from models import UsuarioCrear, UsuarioActualizar, UsuarioLogin
import os

SECRET_KEY = os.getenv("SECRET_KEY")

app = FastAPI() #Crea un servidor web que escucha peticiones HTTP y devuelve respuestas HTTP.

# Le decimos a la API que acepte peticiones desde cualquier lugar porque el frontend y el backend están en servidores diferentes, y los navegadores bloquean las peticiones entre dominios por seguridad
# CORS (Cross-Origin Resource Sharing) es un mecanismo que permite a los servidores indicar que permiten peticiones desde otros dominios
app.add_middleware( # Un middleware es un código que se ejecuta antes de que la petición llegue a la función que la maneja, y puede modificar la petición o la respuesta
    CORSMiddleware, 
    allow_origins=["*"],  # Permitir desde cualquier dirección
    allow_credentials=True, # Permitir que se envíen cookies y cabeceras de autenticación
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Permitir que nos manden datos en cualquier formato (JSON)
)


@app.post("/usuarios/crear") # Cuando el frontend haga una petición POST a la ruta /usuarios/crear, se ejecutará la función crear_usuario()
def crear_usuario(usuario: UsuarioCrear, rol_solicitante: str):
    if rol_solicitante != "administrador":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear usuarios")
    
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
                AES_ENCRYPT(%s, '%s'), 
                AES_ENCRYPT(%s, '%s'), 
                AES_ENCRYPT(%s, '%s')
            )
        """
        
        valores = (
            usuario.nombre, usuario.apellidoPaterno, usuario.apellidoMaterno, usuario.rol, 
            usuario.correoElectronico, usuario.telefono, usuario.fechaNacimiento, 
            usuario.direccion, usuario.rfc, 
            usuario.contrasenia, # Se irá al %s de SHA2
            usuario.numeroCuenta, SECRET_KEY, # Se irá al %s de AES_ENCRYPT
            usuario.cvv, SECRET_KEY,          # Se irá al %s de AES_ENCRYPT
            usuario.nip, SECRET_KEY     # Se irá al %s de AES_ENCRYPT
        )
        
        cursor.execute(sql, valores) # Mandamos la sentencia SQL y los valores separados por seguridad, para evitar inyecciones SQL.
        conexion.commit() # Para que los cambios se guarden en la base de datos. Si no se hace, los cambios se perderán al cerrar la conexión.
        
        return {"status": "success", "mensaje": "Usuario creado y datos encriptados correctamente"}
        
    except mysql.connector.Error as err: # Si hay un error al ejecutar la sentencia SQL, devolvemos un error 400 al frontend
        if err.errno == 1062: # 1062 es el código de error de MySQL para "Duplicate entry", es decir, que ya existe un registro con ese correo electrónico
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
        else:
            raise HTTPException(status_code=500, detail=f"Error al guardar: {err}") # Si es otro error, devolvemos un error 500 al frontend con el mensaje de error que nos dio MySQL
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
                CAST(AES_DECRYPT(numeroCuenta, %s) AS CHAR) as numeroCuenta,
                CAST(AES_DECRYPT(cvv, %s) AS CHAR) as cvv,
                CAST(AES_DECRYPT(nip, %s) AS CHAR) as nip
            FROM usuarios
        """
        
        cursor.execute(sql, (SECRET_KEY, SECRET_KEY, SECRET_KEY)) # Mandamos la llave de encriptación como parámetro para que MySQL pueda desencriptar los datos correctamente
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

@app.get("/usuarios/{id_usuario}")
def obtener_usuario_por_id(id_usuario: int, rol_solicitante: str):
    if rol_solicitante != "administrador":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden consultar esta informacion")
        
    conexion = obtener_conexion()
    if not conexion: 
        raise HTTPException(status_code=500, detail="Error de BD")
    
    try:
        cursor = conexion.cursor(dictionary=True)
        sql = """
            SELECT id, nombre, apellidoPaterno, apellidoMaterno, rol, correoElectronico, 
            telefono, fechaNacimiento, direccion, rfc, estatus,
            CAST(AES_DECRYPT(numeroCuenta, %s) AS CHAR) as numeroCuenta,
            CAST(AES_DECRYPT(cvv, %s) AS CHAR) as cvv,
            CAST(AES_DECRYPT(nip, %s) AS CHAR) as nip
            FROM usuarios
            WHERE id = %s
        """
        cursor.execute(sql, (SECRET_KEY, SECRET_KEY, SECRET_KEY, id_usuario))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {"status": "success", "data": usuario}
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al consultar: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.post("/login") # Cuando el frontend haga una petición POST a la ruta /login, se ejecutará la función iniciar_sesion()
def iniciar_sesion(credenciales: UsuarioLogin):
    conexion = obtener_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la BD")
    
    try:
        cursor = conexion.cursor(dictionary=True)
        
        # Comparamos el correo y la contraseña encriptada con SHA2
        sql = """
            SELECT id, nombre, rol, estatus
            FROM usuarios 
            WHERE correoElectronico = %s AND contrasenia = SHA2(%s, 256)
        """
        
        valores = (credenciales.correoElectronico, credenciales.contrasenia)
        cursor.execute(sql, valores)
        
        # Devuelve un diccionario con los datos del usuario si las credenciales son correctas
        usuario = cursor.fetchone() 
        
        if usuario and usuario["estatus"]:
            # Si encontró un usuario con esas credenciales, devolvemos un mensaje de éxito y los datos del usuario al frontend
            return {
                "status": "success", 
                "mensaje": "Bienvenido a Mesa Verde", 
                "datos": usuario 
            }
        elif usuario: # Si encontró un usuario con esas credenciales pero está inactivo, devolvemos un error 403 al frontend
            raise HTTPException(status_code=403, detail="Usuario inactivo. Contacte al administrador.")
        else: # Si no encontró un usuario con esas credenciales, devolvemos un error 401 al frontend
            raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
            
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.put("/usuarios/{id_usuario}") # Cuando el frontend haga una petición PUT a la ruta /usuarios/{id_usuario}, se ejecutará la función modificar_usuario()
def modificar_usuario(id_usuario: int, datos: UsuarioActualizar, rol_solicitante: str):
    if rol_solicitante != "administrador":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden modificar usuarios")
    
    conexion = obtener_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la BD")
    
    try:
        cursor = conexion.cursor()
        
        # Usamos SHA2 y AES_ENCRYPT para encriptar la contraseña, el número de cuenta, el CVV y el NIP antes de guardarlos en la base de datos
        sql = """
            UPDATE usuarios 
            SET nombre = %s, 
                apellidoPaterno = %s, 
                apellidoMaterno = %s, 
                rol = %s, 
                correoElectronico = %s, 
                telefono = %s, 
                fechaNacimiento = %s, 
                direccion = %s, 
                rfc = %s, 
                estatus = %s,
                contrasenia = SHA2(%s, 256),
                numeroCuenta = AES_ENCRYPT(%s, %s),
                cvv = AES_ENCRYPT(%s, %s),
                nip = AES_ENCRYPT(%s, %s)
            WHERE id = %s
        """
        
        
        valores = ( 
            datos.nombre, datos.apellidoPaterno, datos.apellidoMaterno, datos.rol,
            datos.correoElectronico, datos.telefono, datos.fechaNacimiento,
            datos.direccion, datos.rfc, datos.estatus,
            datos.contrasenia, datos.numeroCuenta, SECRET_KEY, datos.cvv, SECRET_KEY, datos.nip, SECRET_KEY,
            id_usuario
        )
        
        cursor.execute(sql, valores)
        conexion.commit()
        
        if cursor.rowcount == 0: # Si no se modificó ningún registro, significa que el usuario con ese id no existe
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {"status": "success", "mensaje": "Los datos del usuario fueron actualizados"}
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al modificar: {err}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.delete("/usuarios/{id_usuario}") # Cuando el frontend haga una petición DELETE a la ruta /usuarios/{id_usuario}, se ejecutará la función eliminar_usuario()
def eliminar_usuario(id_usuario: int, rol_solicitante: str):
    if rol_solicitante != "administrador":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar usuarios")
    
    conexion = obtener_conexion()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión a la BD")
    
    try:
        cursor = conexion.cursor()
        
        sql = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(sql, (id_usuario,)) #Hay una coma después de id_usuario para que Python lo interprete como una tupla de un solo elemento
        conexion.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
        return {"status": "success", "mensaje": "Usuario eliminado del sistema"}
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {err}")
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

# uvicorn main:app --reload
# http://localhost:8000/docs