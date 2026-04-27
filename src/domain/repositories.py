"""
Módulo de interfaces (contratos) de repositorios del dominio.

Define los contratos abstractos que deben implementar los repositorios
en la capa de infraestructura. El dominio solo conoce estas interfaces,
no las implementaciones concretas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Interfaz que define el contrato para acceder y persistir productos.

    Las implementaciones concretas (SQLite, PostgreSQL, etc.) se ubican
    en la capa de infraestructura y deben respetar este contrato.
    """

    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos del repositorio.

        Returns:
            List[Product]: Lista de todos los productos disponibles.
        """
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador único.

        Args:
            product_id: Identificador único del producto.

        Returns:
            Optional[Product]: El producto si existe, None si no se encuentra.
        """
        pass

    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene todos los productos de una marca específica.

        Args:
            brand: Nombre de la marca (Nike, Adidas, Puma, etc.).

        Returns:
            List[Product]: Lista de productos de la marca indicada.
        """
        pass

    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene todos los productos de una categoría específica.

        Args:
            category: Categoría del producto (Running, Casual, Formal).

        Returns:
            List[Product]: Lista de productos de la categoría indicada.
        """
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en el repositorio.

        Si el producto tiene ID, lo actualiza. Si no tiene ID, lo crea.

        Args:
            product: Entidad de producto a persistir.

        Returns:
            Product: El producto guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto del repositorio por su ID.

        Args:
            product_id: Identificador único del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado, False si no existía.
        """
        pass


class IChatRepository(ABC):
    """
    Interfaz para gestionar el historial de conversaciones del chat.

    Permite persistir y recuperar mensajes para mantener la memoria
    conversacional entre múltiples requests del mismo usuario.
    """

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en el historial de la conversación.

        Args:
            message: Entidad ChatMessage a persistir.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado.
        """
        pass

    @abstractmethod
    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo de una sesión de conversación.

        Args:
            session_id: Identificador único de la sesión de usuario.
            limit: Si se especifica, retorna solo los últimos N mensajes.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico (más antiguos primero).
        """
        pass

    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión de conversación.

        Args:
            session_id: Identificador único de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        pass

    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión específica.

        Este método es crucial para mantener el contexto conversacional
        al llamar al modelo de IA.

        Args:
            session_id: Identificador de la sesión de conversación.
            count: Número máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Los N mensajes más recientes en orden cronológico.
        """
        pass