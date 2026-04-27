"""
Módulo de configuración de la base de datos con SQLAlchemy.

Configura el motor de conexión, la sesión y la clase base
para los modelos ORM. Provee la función de dependencia get_db()
para ser usada con el sistema de inyección de dependencias de FastAPI.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# URL de conexión a SQLite. Se lee desde variable de entorno con valor por defecto.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./data/ecommerce_chat.db"
)

# Motor de base de datos SQLAlchemy
# connect_args es necesario para SQLite con múltiples hilos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  # Poner en True para ver las queries SQL en consola (debug)
)

# Factory de sesiones de base de datos
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Clase base para todos los modelos ORM del proyecto
Base = declarative_base()


def get_db():
    """
    Generador de dependencia para obtener una sesión de base de datos.

    Uso en FastAPI con Depends(get_db). Garantiza que la sesión
    se cierre correctamente después de cada request, incluso si
    ocurre un error.

    Yields:
        Session: Sesión activa de SQLAlchemy.

    Ejemplo:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas y cargando datos iniciales.

    Debe ser llamada al iniciar la aplicación (evento startup de FastAPI).
    Importa los modelos para que SQLAlchemy los registre antes de crear las tablas.
    """
    # Importar modelos para que SQLAlchemy los conozca antes de crear tablas
    from src.infrastructure.db import models  # noqa: F401
    from src.infrastructure.db.init_data import load_initial_data

    # Crear todas las tablas definidas en los modelos
    Base.metadata.create_all(bind=engine)

    # Cargar datos de ejemplo si la base de datos está vacía
    db = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()