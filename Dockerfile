# ─────────────────────────────────────────────
# Dockerfile para SneakerStore API
# Universidad EAFIT - Taller de Construcción
# ─────────────────────────────────────────────

# Imagen base oficial de Python 3.11 (slim para menor tamaño)
FROM python:3.11-slim

# Metadatos de la imagen
LABEL maintainer="Universidad EAFIT"
LABEL description="SneakerStore API - E-commerce con Chat IA"
LABEL version="1.0.0"

# Configurar variables de entorno del contenedor
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar archivo de dependencias primero (mejor caché de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Crear directorio para la base de datos SQLite
RUN mkdir -p /app/data

# Copiar el código fuente de la aplicación
COPY src/ ./src/
COPY tests/ ./tests/

# Copiar archivos de configuración
COPY pyproject.toml .

# Exponer el puerto en el que corre la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación con uvicorn
# --host 0.0.0.0 permite conexiones desde fuera del contenedor
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
