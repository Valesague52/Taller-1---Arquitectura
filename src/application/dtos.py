"""
Módulo de DTOs (Data Transfer Objects) de la capa de aplicación.

Los DTOs validan y transfieren datos entre capas de forma segura
usando Pydantic V2 para validación automática de tipos y restricciones.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos entre capas.

    Pydantic V2 valida automáticamente los tipos de datos y aplica
    las validaciones definidas con @field_validator.

    Atributos:
        id: Identificador único (opcional al crear).
        name: Nombre del producto.
        brand: Marca del producto.
        category: Categoría (Running, Casual, Formal).
        size: Talla en formato string (ej: "42").
        color: Color del producto.
        price: Precio en dólares, debe ser mayor a 0.
        stock: Unidades disponibles, no puede ser negativo.
        description: Descripción detallada del producto.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str = Field(..., min_length=1, description="Nombre del producto")
    brand: str = Field(..., min_length=1, description="Marca del producto")
    category: str = Field(..., min_length=1, description="Categoría del producto")
    size: str = Field(..., min_length=1, description="Talla del zapato")
    color: str = Field(..., min_length=1, description="Color del producto")
    price: float = Field(..., description="Precio en dólares")
    stock: int = Field(..., description="Unidades en inventario")
    description: str = Field(default="", description="Descripción del producto")

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """Valida que el precio sea mayor a 0."""
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0.")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        """Valida que el stock no sea negativo."""
        if v < 0:
            raise ValueError("El stock no puede ser negativo.")
        return v


class ProductFilterDTO(BaseModel):
    """
    DTO para aplicar filtros en la búsqueda de productos.

    Atributos:
        brand: Filtrar por marca.
        category: Filtrar por categoría.
        available_only: Si True, solo retorna productos con stock > 0.
    """

    brand: Optional[str] = None
    category: Optional[str] = None
    available_only: bool = False


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes del usuario en el endpoint de chat.

    Atributos:
        session_id: Identificador único de la sesión del usuario.
        message: Mensaje enviado por el usuario.
    """

    session_id: str = Field(..., description="Identificador único de sesión")
    message: str = Field(..., description="Mensaje del usuario")

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío o solo con espacios."""
        if not v or not v.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        """Valida que el session_id no esté vacío."""
        if not v or not v.strip():
            raise ValueError("El session_id no puede estar vacío.")
        return v.strip()


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para enviar la respuesta del chat al cliente.

    Atributos:
        session_id: Identificador de la sesión de conversación.
        user_message: Mensaje original enviado por el usuario.
        assistant_message: Respuesta generada por Gemini AI.
        timestamp: Momento en que se generó la respuesta.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para exponer el historial de conversación de una sesión.

    Atributos:
        id: Identificador único del mensaje.
        role: Rol del emisor ('user' o 'assistant').
        message: Contenido del mensaje.
        timestamp: Fecha y hora del mensaje.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    timestamp: datetime