# ...existing code...
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar herramientas del sistema si hacen falta para compilar paquetes
RUN apt-get update && apt-get install -y build-essential --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

# Copiar todo el repo (respetando .dockerignore)
COPY . .

# Actualizar pip y instalar dependencias:
# - Si existe requirements.txt, usarlo (cacheable si se mantiene)
# - Si no existe, instalar un conjunto mínimo necesario para ejecutar notebooks y el backend
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ -f requirements.txt ]; then \
      pip install --no-cache-dir -r requirements.txt ; \
    else \
      pip install --no-cache-dir fastapi "uvicorn[standard]" jupyter nbconvert papermill matplotlib numpy pandas ; \
    fi

# Asegurar start.sh ejecutable
RUN if [ -f /start.sh ]; then chmod +x /start.sh; fi

EXPOSE 10000

# Ejecutar el script de arranque (ejecuta notebook y levanta FastAPI/uvicorn)
CMD ["/start.sh"]
# ...existing code...