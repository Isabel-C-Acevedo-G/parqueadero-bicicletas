import hashlib
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI(title="Motor Relacional voy. - MySQL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔗 Conexión MySQL para el backend en Docker
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_SERVER", "mysql"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_UID", "root"),
            password=os.getenv("DB_PWD", "root"),
            database=os.getenv("DB_DATABASE", "ParqueaderoBicicletas"),
            autocommit=False,
            connection_timeout=10,
            charset="utf8mb4",
            use_pure=True,
        )
    except Error:
        raise


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

class Credenciales(BaseModel):
    usuario: str
    contrasena: str

class Movimiento(BaseModel):
    documento: str
    espacio: str

class Incidente(BaseModel):
    bicicleta: str
    descripcion: str

class RegistroUsuario(BaseModel):
    documento: str
    nombres: str
    apellidos: str
    correo: str
    telefono: str
    contrasena: str
    rol: str = "Ciclista"

@app.post("/login")
def iniciar_sesion_relacional(credenciales: Credenciales):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT U.PasswordHash, R.NombreRol
            FROM Usuarios U
            INNER JOIN Roles R ON U.IdRol = R.IdRol
            WHERE U.Correo = %s OR U.Documento = %s
        """
        cursor.execute(query, (credenciales.usuario, credenciales.usuario))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado and verify_password(credenciales.contrasena, resultado[0]):
            return {
                "status": "success",
                "mensaje": "Acceso verificado en MySQL.",
                "rol": resultado[1],
            }
        return {"status": "error", "mensaje": "Usuario o contraseña incorrectos en la base de datos relacional."}
    except Error as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "mensaje": (
                    "No se pudo conectar a MySQL. Verifica que el servicio de MySQL esté activo "
                    "y que los datos de conexión sean correctos."
                ),
                "detalle": str(e),
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "mensaje": "Error interno del servidor.",
                "detalle": str(e),
            },
        )

@app.post("/register")
def registrar_usuario(usuario: RegistroUsuario):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT IdUsuario FROM Usuarios WHERE Documento = %s OR Correo = %s",
            (usuario.documento, usuario.correo),
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"status": "error", "mensaje": "El documento o correo ya está registrado."},
            )

        cursor.execute("SELECT IdRol FROM Roles WHERE NombreRol = %s", (usuario.rol,))
        rol_db = cursor.fetchone()
        id_rol = rol_db[0] if rol_db else 3

        cursor.execute(
            "INSERT INTO Usuarios (Documento, Nombres, Apellidos, Correo, Telefono, PasswordHash, IdRol) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                usuario.documento,
                usuario.nombres,
                usuario.apellidos,
                usuario.correo,
                usuario.telefono,
                hash_password(usuario.contrasena),
                id_rol,
            ),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "mensaje": "Usuario registrado correctamente. Ya puedes iniciar sesión."}
    except Error as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "mensaje": "No se pudo conectar a MySQL.", "detalle": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "mensaje": "Error interno del servidor.", "detalle": str(e)},
        )

@app.get("/cupos")
def obtener_cupos_disponibles():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Espacios WHERE Estado = 'Disponible'")
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"cupos_libres": resultado[0] if resultado else 0}
    except Error as e:
        return {"cupos_libres": 0, "error": str(e)}
    except Exception as e:
        return {"cupos_libres": 0, "error": str(e)}

@app.post("/ingreso")
def registrar_ingreso(movimiento: Movimiento):
    if not movimiento.espacio:
        raise HTTPException(status_code=400, detail="Debe indicar el espacio o celda de ingreso.")
    return {
        "status": "success",
        "mensaje": f"Ingreso registrado para {movimiento.documento} en {movimiento.espacio}.",
    }

@app.post("/salida")
def registrar_salida(movimiento: Movimiento):
    if not movimiento.espacio:
        raise HTTPException(status_code=400, detail="Debe indicar el espacio o celda de salida.")
    return {
        "status": "success",
        "mensaje": f"Salida registrada para {movimiento.documento} desde {movimiento.espacio}.",
    }

@app.post("/incidente")
def registrar_incidente(incidente: Incidente):
    if not incidente.bicicleta or not incidente.descripcion:
        raise HTTPException(status_code=400, detail="Debe completar los datos del incidente.")
    return {
        "status": "success",
        "mensaje": f"Incidente reportado para {incidente.bicicleta}: {incidente.descripcion}",
    }