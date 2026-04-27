"""
Módulo de configuración de fixtures para pruebas unitarias.

Provee fixtures reutilizables de pytest para los tests del proyecto,
incluyendo base de datos en memoria, repositorios y servicios de prueba.
"""

import pytest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.infrastructure.db.database import Base
from src.infrastructure.db.models import ProductModel, ChatMemoryModel
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.domain.entities import Product, ChatMessage


# ─────────────────────────────────────────────
# FIXTURES DE BASE DE DATOS EN MEMORIA
# ─────────────────────────────────────────────


@pytest.fixture(scope="function")
def test_engine():
    """
    Crea un motor de base de datos SQLite en memoria para pruebas.

    Usa SQLite en memoria (:memory:) para aislar las pruebas y
    garantizar que no afecten datos reales.

    Yields:
        Engine: Motor de base de datos SQLAlchemy en memoria.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """
    Provee una sesión de base de datos para cada test.

    Crea y cierra la sesión automáticamente para cada función de test,
    garantizando aislamiento entre pruebas.

    Args:
        test_engine: Motor de base de datos en memoria.

    Yields:
        Session: Sesión activa de SQLAlchemy para el test.
    """
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()


# ─────────────────────────────────────────────
# FIXTURES DE DATOS DE EJEMPLO
# ─────────────────────────────────────────────


@pytest.fixture
def sample_product():
    """
    Provee un producto de ejemplo para pruebas de dominio.

    Returns:
        Product: Entidad de dominio Product con datos válidos.
    """
    return Product(
        id=None,
        name="Air Zoom Test",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapato de prueba para tests unitarios",
    )


@pytest.fixture
def sample_product_model(test_db):
    """
    Persiste un producto de ejemplo en la base de datos de prueba.

    Args:
        test_db: Sesión de base de datos en memoria.

    Returns:
        ProductModel: Modelo ORM con el producto guardado y su ID asignado.
    """
    model = ProductModel(
        name="Air Zoom Test",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapato de prueba",
    )
    test_db.add(model)
    test_db.commit()
    test_db.refresh(model)
    return model


@pytest.fixture
def sample_chat_message():
    """
    Provee un mensaje de chat de ejemplo para pruebas.

    Returns:
        ChatMessage: Entidad de dominio ChatMessage con datos válidos.
    """
    return ChatMessage(
        id=None,
        session_id="test_session_001",
        role="user",
        message="Busco zapatos para correr",
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture
def product_repository(test_db):
    """
    Provee una instancia del repositorio de productos con base de datos de prueba.

    Args:
        test_db: Sesión de base de datos en memoria.

    Returns:
        SQLProductRepository: Repositorio configurado con BD de prueba.
    """
    return SQLProductRepository(test_db)


@pytest.fixture
def chat_repository(test_db):
    """
    Provee una instancia del repositorio de chat con base de datos de prueba.

    Args:
        test_db: Sesión de base de datos en memoria.

    Returns:
        SQLChatRepository: Repositorio configurado con BD de prueba.
    """
    return SQLChatRepository(test_db)