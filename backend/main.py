from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI(title="API Profesional de Parqueaderos con Base de Datos SQL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "parqueadero_sena.db"
TOTAL_CUPOS = 50

class Transaccion(BaseModel):
    documento: str

class Credenciales(BaseModel):
    usuario: str
    contrasena: str

# Configuración e Inicialización de la Base de Datos SQL
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Tabla 1: Usuarios del sistema (Login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            contrasena TEXT NOT NULL
        )
    ''')
    # Tabla 2: Registro activo de bicicletas parqueadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parqueadero_activos (
            documento TEXT PRIMARY KEY,
            hora_entrada TEXT NOT NULL
        )
    ''')
    # Tabla 3: Historial permanente de uso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historial_parqueadero (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            documento TEXT NOT NULL,
            hora_entrada TEXT NOT NULL,
            hora_salida TEXT NOT NULL
        )
    ''')
    # Insertar usuarios de prueba por defecto si no existen
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('admin_usuario', '12345')")
    cursor.execute("INSERT OR IGNORE INTO usuarios VALUES ('operario_medellin', '2026')")
    conn.commit()
    conn.close()

# Ejecutar inicialización de tablas SQL
init_db()

@app.post("/login")
def validar_login(credenciales: Credenciales):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (credenciales.usuario, credenciales.contrasena))
    usuario_encontrado = cursor.fetchone()
    conn.close()
    
    if usuario_encontrado:
        return {"status": "success", "mensaje": "Autenticación satisfactoria SQL. Bienvenido."}
    return {"status": "error", "mensaje": "Usuario o contraseña incorrectos en base de datos SQL."}

@app.get("/cupos")
def obtener_cupos():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM parqueadero_activos")
    vehiculos_adentro = cursor.fetchone()[0]
    conn.close()
    
    cupos_libres = max(0, TOTAL_CUPOS - vehiculos_adentro)
    return {"cupos_libres": cupos_libres}

@app.post("/ingreso")
def registrar_ingreso(data: Transaccion):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Validación SQL: Ver si ya está registrado adentro
    cursor.execute("SELECT * FROM parqueadero_activos WHERE documento = ?", (data.documento,))
    if cursor.fetchone():
        conn.close()
        return {"status": "error", "mensaje": "Esta bicicleta ya registra un ingreso activo en la base de datos."}
    
    # Validación SQL: Control de aforo
    cursor.execute("SELECT COUNT(*) FROM parqueadero_activos")
    if cursor.fetchone()[0] >= TOTAL_CUPOS:
        conn.close()
        return {"status": "error", "mensaje": "Lo sentimos, no hay cupos SQL disponibles."}
    
    hora_entrada = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO parqueadero_activos VALUES (?, ?)", (data.documento, hora_entrada))
    conn.commit()
    conn.close()
    return {"status": "success", "mensaje": f"Ingreso SQL exitoso a las {hora_entrada}."}

@app.post("/salida")
def registrar_salida(data: Transaccion):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Buscar registro activo
    cursor.execute("SELECT hora_entrada FROM parqueadero_activos WHERE documento = ?", (data.documento,))
    registro = cursor.fetchone()
    
        # 1. Verificar si el registro existe en la base de datos SQL
    if not registro:
        conn.close()
        return {"status": "error", "mensaje": "El documento no cuenta con parqueos activos en el sistema SQL."}
    
    # 2. Extraer la hora de entrada real de la consulta SQL
    hora_entrada = registro[0]

    hora_salida = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Transacción SQL: Mover al historial permanente y remover del activo
    cursor.execute("INSERT INTO historial_parqueadero (documento, hora_entrada, hora_salida) VALUES (?, ?, ?)", (data.documento, hora_entrada, hora_salida))
    cursor.execute("DELETE FROM parqueadero_activos WHERE documento = ?", (data.documento,))
    conn.commit()
    conn.close()
    return {"status": "success", "mensaje": f"Salida SQL procesada. Estuvo desde: {hora_entrada}."}
