"""
Tests unitarios para las entidades del dominio y servicios de aplicación.

Valida el comportamiento de las reglas de negocio, validaciones
y la lógica de cada capa de la arquitectura limpia.
"""

import pytest
from datetime import datetime, timezone

from src.domain.entities import Product, ChatMessage, ChatContext
from src.domain.exceptions import ProductNotFoundError
from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
)
from src.application.product_service import ProductService


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────


def _now() -> datetime:
    """Retorna la fecha/hora actual con timezone UTC (sin deprecation warning)."""
    return datetime.now(timezone.utc)


def _make_msg(role: str, message: str, session: str = "test") -> ChatMessage:
    """
    Crea una entidad ChatMessage lista para usar en tests.

    Args:
        role: 'user' o 'assistant'.
        message: Contenido del mensaje.
        session: Identificador de sesión (por defecto 'test').

    Returns:
        ChatMessage: Entidad de dominio con datos de prueba.
    """
    return ChatMessage(
        id=None,
        session_id=session,
        role=role,
        message=message,
        timestamp=_now(),
    )


# ─────────────────────────────────────────────
# TESTS DE ENTIDAD PRODUCT
# ─────────────────────────────────────────────


class TestProductEntity:
    """Tests unitarios para la entidad de dominio Product."""

    def test_crear_producto_valido(self, sample_product: Product) -> None:
        """Verifica que un producto con datos válidos se crea correctamente."""
        assert sample_product.name == "Air Zoom Test"
        assert sample_product.price == 120.0
        assert sample_product.stock == 5

    def test_precio_negativo_lanza_error(self) -> None:
        """Verifica que un precio negativo lanza ValueError."""
        with pytest.raises(ValueError, match="mayor a 0"):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=-10.0,
                stock=5,
                description="Test",
            )

    def test_precio_cero_lanza_error(self) -> None:
        """Verifica que precio igual a cero lanza ValueError."""
        with pytest.raises(ValueError):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=0.0,
                stock=5,
                description="",
            )

    def test_stock_negativo_lanza_error(self) -> None:
        """Verifica que un stock negativo lanza ValueError."""
        with pytest.raises(ValueError, match="negativo"):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=100.0,
                stock=-1,
                description="",
            )

    def test_nombre_vacio_lanza_error(self) -> None:
        """Verifica que un nombre vacío lanza ValueError."""
        with pytest.raises(ValueError):
            Product(
                id=None,
                name="",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=100.0,
                stock=5,
                description="",
            )

    def test_is_available_con_stock(self, sample_product: Product) -> None:
        """Verifica que is_available retorna True cuando hay stock."""
        assert sample_product.is_available() is True

    def test_is_available_sin_stock(self) -> None:
        """Verifica que is_available retorna False cuando el stock es 0."""
        product = Product(
            id=None,
            name="Agotado",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=100.0,
            stock=0,
            description="",
        )
        assert product.is_available() is False

    def test_reduce_stock_exitoso(self, sample_product: Product) -> None:
        """Verifica que reduce_stock disminuye el stock correctamente."""
        stock_inicial = sample_product.stock
        sample_product.reduce_stock(2)
        assert sample_product.stock == stock_inicial - 2

    def test_reduce_stock_insuficiente_lanza_error(self, sample_product: Product) -> None:
        """Verifica que reducir más stock del disponible lanza ValueError."""
        with pytest.raises(ValueError):
            sample_product.reduce_stock(100)

    def test_reduce_stock_cantidad_negativa_lanza_error(self, sample_product: Product) -> None:
        """Verifica que reducir con cantidad negativa lanza ValueError."""
        with pytest.raises(ValueError):
            sample_product.reduce_stock(-1)

    def test_increase_stock(self, sample_product: Product) -> None:
        """Verifica que increase_stock aumenta el stock correctamente."""
        stock_inicial = sample_product.stock
        sample_product.increase_stock(10)
        assert sample_product.stock == stock_inicial + 10

    def test_increase_stock_cantidad_negativa_lanza_error(self, sample_product: Product) -> None:
        """Verifica que aumentar con cantidad negativa lanza ValueError."""
        with pytest.raises(ValueError):
            sample_product.increase_stock(-5)


# ─────────────────────────────────────────────
# TESTS DE ENTIDAD CHAT MESSAGE
# ─────────────────────────────────────────────


class TestChatMessageEntity:
    """Tests unitarios para la entidad de dominio ChatMessage."""

    def test_crear_mensaje_valido(self, sample_chat_message: ChatMessage) -> None:
        """Verifica que un mensaje con datos válidos se crea correctamente."""
        assert sample_chat_message.role == "user"
        assert sample_chat_message.message == "Busco zapatos para correr"

    def test_rol_invalido_lanza_error(self) -> None:
        """Verifica que un rol inválido lanza ValueError."""
        with pytest.raises(ValueError, match="user.*assistant"):
            ChatMessage(
                id=None,
                session_id="session_001",
                role="admin",
                message="Hola",
                timestamp=_now(),
            )

    def test_mensaje_vacio_lanza_error(self) -> None:
        """Verifica que un mensaje vacío lanza ValueError."""
        with pytest.raises(ValueError):
            ChatMessage(
                id=None,
                session_id="session_001",
                role="user",
                message="",
                timestamp=_now(),
            )

    def test_session_id_vacio_lanza_error(self) -> None:
        """Verifica que un session_id vacío lanza ValueError."""
        with pytest.raises(ValueError):
            ChatMessage(
                id=None,
                session_id="",
                role="user",
                message="Hola",
                timestamp=_now(),
            )

    def test_is_from_user(self, sample_chat_message: ChatMessage) -> None:
        """Verifica que is_from_user retorna True para mensajes de usuario."""
        assert sample_chat_message.is_from_user() is True
        assert sample_chat_message.is_from_assistant() is False

    def test_is_from_assistant(self) -> None:
        """Verifica que is_from_assistant retorna True para mensajes del asistente."""
        msg = _make_msg("assistant", "¡Hola! ¿En qué puedo ayudarte?")
        assert msg.is_from_assistant() is True
        assert msg.is_from_user() is False


# ─────────────────────────────────────────────
# TESTS DE CHAT CONTEXT
# ─────────────────────────────────────────────


class TestChatContext:
    """Tests unitarios para el value object ChatContext."""

    def test_get_recent_messages_limita_cantidad(self) -> None:
        """Verifica que get_recent_messages respeta el límite max_messages."""
        messages = [_make_msg("user", f"Mensaje {i}") for i in range(10)]
        context = ChatContext(messages=messages, max_messages=4)
        recent = context.get_recent_messages()
        assert len(recent) == 4

    def test_format_for_prompt_formato_correcto(self) -> None:
        """Verifica que format_for_prompt genera el texto correctamente formateado."""
        messages = [
            _make_msg("user", "Hola"),
            _make_msg("assistant", "¡Hola! ¿En qué puedo ayudarte?"),
        ]
        context = ChatContext(messages=messages)
        resultado = context.format_for_prompt()
        assert "Usuario: Hola" in resultado
        assert "Asistente: ¡Hola! ¿En qué puedo ayudarte?" in resultado

    def test_format_for_prompt_sin_mensajes(self) -> None:
        """Verifica que format_for_prompt retorna string vacío sin mensajes."""
        context = ChatContext(messages=[])
        assert context.format_for_prompt() == ""


# ─────────────────────────────────────────────
# TESTS DE REPOSITORIOS
# ─────────────────────────────────────────────


class TestSQLProductRepository:
    """Tests de integración para el repositorio de productos con SQLite."""

    def test_save_y_get_all(self, product_repository, sample_product: Product) -> None:
        """Verifica que se puede guardar y recuperar un producto."""
        product_repository.save(sample_product)
        all_products = product_repository.get_all()
        assert len(all_products) >= 1
        assert any(p.name == "Air Zoom Test" for p in all_products)

    def test_get_by_id_existente(self, product_repository, sample_product: Product) -> None:
        """Verifica que get_by_id retorna el producto correcto."""
        saved = product_repository.save(sample_product)
        found = product_repository.get_by_id(saved.id)
        assert found is not None
        assert found.name == saved.name

    def test_get_by_id_inexistente(self, product_repository) -> None:
        """Verifica que get_by_id retorna None para un ID que no existe."""
        result = product_repository.get_by_id(99999)
        assert result is None

    def test_get_by_brand(self, product_repository, sample_product: Product) -> None:
        """Verifica que get_by_brand filtra correctamente por marca."""
        product_repository.save(sample_product)
        results = product_repository.get_by_brand("Nike")
        assert len(results) > 0
        assert all(p.brand == "Nike" for p in results)

    def test_delete_existente(self, product_repository, sample_product: Product) -> None:
        """Verifica que se puede eliminar un producto existente."""
        saved = product_repository.save(sample_product)
        deleted = product_repository.delete(saved.id)
        assert deleted is True
        assert product_repository.get_by_id(saved.id) is None

    def test_delete_inexistente(self, product_repository) -> None:
        """Verifica que delete retorna False para un ID que no existe."""
        result = product_repository.delete(99999)
        assert result is False


class TestSQLChatRepository:
    """Tests de integración para el repositorio de chat con SQLite."""

    def test_save_message(self, chat_repository, sample_chat_message: ChatMessage) -> None:
        """Verifica que se puede guardar un mensaje de chat."""
        saved = chat_repository.save_message(sample_chat_message)
        assert saved.id is not None
        assert saved.message == sample_chat_message.message

    def test_get_session_history(self, chat_repository, sample_chat_message: ChatMessage) -> None:
        """Verifica que se puede recuperar el historial de una sesión."""
        chat_repository.save_message(sample_chat_message)
        history = chat_repository.get_session_history("test_session_001")
        assert len(history) >= 1

    def test_delete_session_history(self, chat_repository, sample_chat_message: ChatMessage) -> None:
        """Verifica que se puede eliminar el historial de una sesión."""
        chat_repository.save_message(sample_chat_message)
        deleted = chat_repository.delete_session_history("test_session_001")
        assert deleted >= 1
        history = chat_repository.get_session_history("test_session_001")
        assert len(history) == 0


# ─────────────────────────────────────────────
# TESTS DE PRODUCT SERVICE
# ─────────────────────────────────────────────


class TestProductService:
    """Tests unitarios para el servicio de aplicación ProductService."""

    def test_get_all_products(self, product_repository, sample_product: Product) -> None:
        """Verifica que get_all_products retorna todos los productos."""
        product_repository.save(sample_product)
        service = ProductService(product_repository)
        products = service.get_all_products()
        assert len(products) >= 1

    def test_get_product_by_id_existente(self, product_repository, sample_product: Product) -> None:
        """Verifica que get_product_by_id retorna el producto correcto."""
        saved = product_repository.save(sample_product)
        service = ProductService(product_repository)
        result = service.get_product_by_id(saved.id)
        assert result.name == "Air Zoom Test"

    def test_get_product_by_id_inexistente(self, product_repository) -> None:
        """Verifica que get_product_by_id lanza ProductNotFoundError si no existe."""
        service = ProductService(product_repository)
        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(99999)

    def test_get_available_products(self, product_repository) -> None:
        """Verifica que get_available_products solo retorna productos con stock."""
        agotado = Product(
            id=None,
            name="Agotado",
            brand="Test",
            category="Casual",
            size="40",
            color="Rojo",
            price=50.0,
            stock=0,
            description="",
        )
        disponible = Product(
            id=None,
            name="Disponible",
            brand="Test",
            category="Casual",
            size="40",
            color="Azul",
            price=60.0,
            stock=3,
            description="",
        )
        product_repository.save(agotado)
        product_repository.save(disponible)
        service = ProductService(product_repository)
        available = service.get_available_products()
        assert all(p.stock > 0 for p in available)


# ─────────────────────────────────────────────
# TESTS DE DTOs
# ─────────────────────────────────────────────


class TestDTOs:
    """Tests de validación de los DTOs de la capa de aplicación."""

    def test_product_dto_valido(self) -> None:
        """Verifica que un ProductDTO con datos válidos se crea correctamente."""
        dto = ProductDTO(
            name="Test",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=100.0,
            stock=5,
            description="",
        )
        assert dto.price == 100.0
        assert dto.stock == 5

    def test_product_dto_precio_invalido(self) -> None:
        """Verifica que ProductDTO rechaza precios negativos."""
        with pytest.raises(Exception):
            ProductDTO(
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=-10.0,
                stock=5,
                description="",
            )

    def test_product_dto_stock_invalido(self) -> None:
        """Verifica que ProductDTO rechaza stock negativo."""
        with pytest.raises(Exception):
            ProductDTO(
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=100.0,
                stock=-1,
                description="",
            )

    def test_chat_request_dto_valido(self) -> None:
        """Verifica que ChatMessageRequestDTO con datos válidos se crea correctamente."""
        dto = ChatMessageRequestDTO(
            session_id="sesion_001",
            message="Busco zapatos Nike",
        )
        assert dto.session_id == "sesion_001"
        assert dto.message == "Busco zapatos Nike"

    def test_chat_request_dto_mensaje_vacio(self) -> None:
        """Verifica que ChatMessageRequestDTO rechaza mensajes vacíos."""
        with pytest.raises(Exception):
            ChatMessageRequestDTO(session_id="sesion_001", message="")

    def test_chat_request_dto_session_vacia(self) -> None:
        """Verifica que ChatMessageRequestDTO rechaza session_id vacío."""
        with pytest.raises(Exception):
            ChatMessageRequestDTO(session_id="", message="Hola")