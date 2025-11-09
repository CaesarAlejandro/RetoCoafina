# --- Etapa 1: Builder ---
# Instala dependencias y ejecuta el script de análisis.
FROM python:3.10 AS builder

WORKDIR /app
# Copiar el frontend
COPY Front/ ./Front/
# Instalar dependencias para el análisis
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de análisis
COPY ArchivosPython/ ./ArchivosPython/

# Ejecutar el script de análisis directamente.
# Si este script falla, el build se detendrá y mostrará el error.
RUN python ArchivosPython/analysis.py

# --- Etapa 2: Final ---
# Usa una imagen ligera de Python para ejecutar el servidor web.
FROM python:3.10-slim

WORKDIR /app

# Instalar solo las dependencias del servidor
RUN pip install --no-cache-dir "fastapi[all]" uvicorn

# Copiar el frontend
COPY Front/ ./Front/

# Copiar el script del servidor
COPY server.py .

# Crear el directorio de datos y copiar los JSON generados desde la etapa 'builder'
RUN mkdir -p ./ArchivosPython
COPY --from=builder /app/*.json ./ArchivosPython/

# Exponer el puerto del servidor
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]