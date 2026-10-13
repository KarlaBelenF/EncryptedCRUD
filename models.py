from datetime import date
from pydantic import BaseModel, EmailStr, Field

# Definimos un modelo de datos para la creación de usuarios, que será usado para validar los datos que el frontend envíe al backend
# No pedimos id porque la base de datos lo genera automáticamente ni estado porque por default es true
class UsuarioCrear(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidoPaterno: str = Field(..., min_length=2, max_length=50)
    apellidoMaterno: str = Field(..., min_length=2, max_length=50)
    rol: str = Field(..., min_length=3, max_length=20)
    correoElectronico: EmailStr
    telefono: str = Field(..., min_length=10, max_length=15)
    fechaNacimiento: date
    direccion: str = Field(..., min_length=5, max_length=255)
    rfc: str = Field(..., min_length=12, max_length=13)
    contrasenia: str = Field(..., min_length=8)
    numeroCuenta: str = Field(..., min_length=10, max_length=18)
    cvv: str = Field(..., min_length=3, max_length=4)
    nip: str = Field(..., min_length=4, max_length=4)

class UsuarioLogin(BaseModel):
    correoElectronico: str
    contrasenia: str

class UsuarioActualizar(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    apellidoPaterno: str = Field(..., min_length=2, max_length=50)
    apellidoMaterno: str = Field(..., min_length=2, max_length=50)
    rol: str = Field(..., min_length=3, max_length=20)
    correoElectronico: EmailStr
    telefono: str = Field(..., min_length=10, max_length=15)
    fechaNacimiento: date
    direccion: str = Field(..., min_length=5, max_length=255)
    rfc: str = Field(..., min_length=12, max_length=13)
    contrasenia: str | None = Field(default=None, min_length=8)
    numeroCuenta: str = Field(..., min_length=10, max_length=18)
    cvv: str = Field(..., min_length=3, max_length=4)
    nip: str = Field(..., min_length=4, max_length=4)
    estatus: bool