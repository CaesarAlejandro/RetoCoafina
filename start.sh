# ...existing code...
#!/bin/bash
set -euo pipefail

# Ir al directorio del repo (asegura rutas relativas)
cd "$(dirname "$0")"

# Configurables
NOTEBOOK="ArchivosPython/analysis.ipynb"
EXECUTED_NOTEBOOK="ArchivosPython/executed.ipynb"
FRONT_DIR="Front"
NB_TIMEOUT=600   # segundos para la ejecución del notebook

echo "=== START.SH: inicio ==="
echo "Notebook: $NOTEBOOK"
echo "Salida HTML en: $FRONT_DIR/index.html"

# Preparar carpeta de salida
mkdir -p "$FRONT_DIR"

# Ejecutar el notebook y convertir a HTML (fallar si hay errores)
if [ -f "$NOTEBOOK" ]; then
  echo "Iniciando build: ejecutando notebook de análisis..."
  python -m nbconvert --to notebook --execute "$NOTEBOOK" --output "$EXECUTED_NOTEBOOK" --ExecutePreprocessor.timeout=$NB_TIMEOUT
  echo "Notebook ejecutado: $EXECUTED_NOTEBOOK"

  echo "Convirtiendo notebook ejecutado a HTML..."
  python -m nbconvert --to html "$EXECUTED_NOTEBOOK" --output-dir="$FRONT_DIR" --output="index.html"
  echo "HTML generado en: $FRONT_DIR/index.html"
else
  echo "WARN: Notebook $NOTEBOOK no encontrado. Se salta la fase de build."
fi

# Verificar artefactos mínimos
if [ ! -f "$FRONT_DIR/index.html" ]; then
  echo "ERROR: Front/index.html no encontrado. Abortando startup."
  ls -la "$FRONT_DIR" || true
  exit 1
fi

echo "Contenido de $FRONT_DIR:"
ls -la "$FRONT_DIR"

# --- PASO 2: INICIAR SERVIDOR ---
echo "Iniciando Web Service (uvicorn)..."
# Usamos exec para que uvicorn reciba PID 1 (mejor manejo de señales)
exec uvicorn server:app --host 0.0.0.0 --port ${PORT:-10000}
# ...existing code...