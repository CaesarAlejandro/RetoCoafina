# Dockerfile
# 1. Empezar desde una imagen oficial de Python
FROM python:3.10-slim

# 2. Establecer un directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar e instalar SOLAMENTE los requisitos
# (Asumiendo que requirements.txt está en la raíz)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- FIN ---
# Ya no copiamos analisis.py ni usamos CMD.
# Le dejamos esa responsabilidad a la GitHub Action.