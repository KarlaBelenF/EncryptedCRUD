from pydantic import BaseModel
from datetime import date

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

class UsuarioLogin(BaseModel):
    correoElectronico: str
    contrasenia: str

class UsuarioActualizar(BaseModel):
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
    estatus: bool