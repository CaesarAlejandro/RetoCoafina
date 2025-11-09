import json
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# --- Configuración ---
app = FastAPI()

# Ruta al JSON generado por el notebook
JSON_FILE_PATH = os.path.join("ArchivosPython", "datos_analisis.json")

# --- 1. API Endpoint (El Backend) ---
@app.get("/api/data")
async def get_analysis_data():
    """
    Lee el archivo JSON generado por el notebook y lo devuelve.
    """
    if not os.path.exists(JSON_FILE_PATH):
        return {"error": "Datos de análisis no encontrados. El build pudo fallar."}
    
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data

# --- 2. Servidor de Archivos (El Frontend) ---
# Esto sirve el index.html, JS, CSS desde la carpeta 'Front/'
app.mount("/", StaticFiles(directory="Front", html=True), name="static")

print("Servidor FastAPI listo.")