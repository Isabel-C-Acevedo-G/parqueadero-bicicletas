from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from datetime import datetime

app = FastAPI(title="API Profesional de Parqueaderos con Seguridad")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "parqueadero_db.json"
TOTAL_CUPOS = 50  # Total de cupos disponibles en el parqueadero

# Estructuras de datos profesionales
class Transaccion(BaseModel):
    documento: str

class Credenciales(BaseModel):
    usuario: str
    contrasena: str

# Base de datos simulada de usuarios del parqueadero
USUARIOS_AUTORIZADOS = {
    "admin_usuario": "12345",
    "operario_medellin": "2026"
}

def cargar_base_datos():
    if not os.path.exists(DB_FILE):
        return {"activos": {}, "historial": []}
    with open(DB_FILE, "r") as file:
        return json.load(file)

def guardar_base_datos(data):
    with open(DB_FILE, "w") as file:
        json.dump(data, file, indent=4)

# NUEVO ENDPOINT: Validación de credenciales
@app.post("/login")
def validar_login(credenciales: Credenciales):
    usuario = credenciales.usuario
    contrasena = credenciales.contrasena
    
    if usuario in USUARIOS_AUTORIZADOS and USUARIOS_AUTORIZADOS[usuario] == contrasena:
        return {"status": "success", "mensaje": "Autenticación satisfactoria. Bienvenido."}
    
    return {"status": "error", "mensaje": "Usuario o contraseña incorrectos. Intente de nuevo."}

@app.get("/cupos")
def obtener_cupos():
    db = cargar_base_datos()
    vehiculos_adentro = len(db["activos"])
    cupos_libres = max(0, TOTAL_CUPOS - vehiculos_adentro)
    return {"cupos_libres": cupos_libres}

@app.post("/ingreso")
def registrar_ingreso(data: Transaccion):
    db = cargar_base_datos()
    if data.documento in db["activos"]:
        return {"status": "error", "mensaje": "Esta bicicleta ya registra un ingreso activo."}
    if len(db["activos"]) >= TOTAL_CUPOS:
        return {"status": "error", "mensaje": "Parqueadero lleno."}
    
    hora_entrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["activos"][data.documento] = {"hora_entrada": hora_entrada}
    guardar_base_datos(db)
    return {"status": "success", "mensaje": f"Ingreso exitoso a las {hora_entrada}."}

@app.post("/salida")
def registrar_salida(data: Transaccion):
    db = cargar_base_datos()
    if data.documento not in db["activos"]:
        return {"status": "error", "mensaje": "El documento no cuenta con bicicletas estacionadas."}
    
    hora_entrada = db["activos"][data.documento]["hora_entrada"]
    hora_salida = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db["historial"].append({"documento": data.documento, "entrada": hora_entrada, "salida": hora_salida})
    del db["activos"][data.documento]
    guardar_base_datos(db)
    return {"status": "success", "mensaje": f"Salida procesada. Estuvo desde: {hora_entrada}."}
