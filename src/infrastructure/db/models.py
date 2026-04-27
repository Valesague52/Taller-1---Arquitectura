"""
Módulo de modelos ORM de la capa de infraestructura.

Define la representación de las tablas de base de datos usando SQLAlchemy.
Estos modelos son específicos de la infraestructura y no deben usarse
directamente en el dominio o la capa de aplicación.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from src.infrastructure.db.database import Base


class ProductModel(Base):
    """
    Modelo ORM que representa la tabla 'products' en la base de datos.

    Almacena todos los zapatos disponibles en el e-commerce con sus
    atributos de inventario.

    Tabla: products

    Columnas:
        id: Clave primaria autoincremental.
        name: Nombre del producto (max 200 caracteres).
        brand: Marca del producto (max 100 caracteres).
        category: Categoría del producto (max 100 caracteres).
        size: Talla del zapato (max 20 caracteres).
        color: Color del producto (max 50 caracteres).
        price: Precio en dólares (punto flotante).
        stock: Unidades disponibles en inventario.
        description: Descripción detallada (texto largo).
    """

    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identificador único del producto",
    )
    name = Column(
        String(200),
        nullable=False,
        comment="Nombre del producto",
    )
    brand = Column(
        String(100),
        nullable=False,
        comment="Marca del producto",
    )
    category = Column(
        String(100),
        nullable=False,
        comment="Categoría del producto (Running, Casual, Formal)",
    )
    size = Column(
        String(20),
        nullable=False,
        comment="Talla del zapato",
    )
    color = Column(
        String(50),
        nullable=False,
        comment="Color del producto",
    )
    price = Column(
        Float,
        nullable=False,
        comment="Precio en dólares",
    )
    stock = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Unidades disponibles en inventario",
    )
    description = Column(
        Text,
        nullable=True,
        default="",
        comment="Descripción detallada del producto",
    )

    # Índice en brand y category para búsquedas frecuentes
    __table_args__ = (
        Index("ix_products_brand", "brand"),
        Index("ix_products_category", "category"),
    )

    def __repr__(self) -> str:
        """Representación legible del modelo para debugging."""
        return f"<ProductModel(id={self.id}, name='{self.name}', brand='{self.brand}')>"


class ChatMemoryModel(Base):
    """
    Modelo ORM que representa la tabla 'chat_memory' en la base de datos.

    Almacena el historial de mensajes de todas las conversaciones
    para mantener la memoria conversacional del asistente de IA.

    Tabla: chat_memory

    Columnas:
        id: Clave primaria autoincremental.
        session_id: Identificador único de la sesión del usuario.
        role: Rol del emisor ('user' o 'assistant').
        message: Contenido del mensaje (texto largo).
        timestamp: Fecha y hora del mensaje (UTC).
    """

    __tablename__ = "chat_memory"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Identificador único del mensaje",
    )
    session_id = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Identificador de la sesión de conversación",
    )
    role = Column(
        String(20),
        nullable=False,
        comment="Rol del emisor: user o assistant",
    )
    message = Column(
        Text,
        nullable=False,
        comment="Contenido del mensaje",
    )
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora del mensaje en UTC",
    )

    # Índice compuesto para consultas de historial por sesión y tiempo
    __table_args__ = (
        Index("ix_chat_memory_session_time", "session_id", "timestamp"),
    )

    def __repr__(self) -> str:
        """Representación legible del modelo para debugging."""
        return (
            f"<ChatMemoryModel(id={self.id}, session='{self.session_id}', "
            f"role='{self.role}')>"
        )