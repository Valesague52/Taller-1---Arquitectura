"""
Módulo de entidades del dominio.

Contiene las entidades principales del negocio: Product, ChatMessage y ChatContext.
Esta capa es completamente independiente de frameworks y bases de datos.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class Product:
    """
    Entidad que representa un producto (zapato) en el e-commerce.

    Contiene los datos y la lógica de negocio relacionada con productos.
    Aplica validaciones automáticas al momento de creación.

    Atributos:
        id: Identificador único del producto (None si no ha sido persistido).
        name: Nombre del producto.
        brand: Marca del producto (Nike, Adidas, Puma, etc.).
        category: Categoría del producto (Running, Casual, Formal).
        size: Talla del zapato.
        color: Color del producto.
        price: Precio del producto en dólares.
        stock: Cantidad disponible en inventario.
        description: Descripción detallada del producto.

    Ejemplo:
        >>> product = Product(id=None, name="Air Zoom", brand="Nike",
        ...     category="Running", size="42", color="Negro",
        ...     price=120.0, stock=5, description="Zapato deportivo")
    """

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """
        Valida los datos del producto inmediatamente después de la creación.

        Verifica que:
        - El precio sea mayor a 0.
        - El stock no sea negativo.
        - El nombre no esté vacío.

        Raises:
            ValueError: Si alguna validación falla.
        """
        if self.price <= 0:
            raise ValueError("El precio del producto debe ser mayor a 0.")
        if self.stock < 0:
            raise ValueError("El stock del producto no puede ser negativo.")
        if not self.name or not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")

    def is_available(self) -> bool:
        """
        Verifica si el producto tiene stock disponible para la venta.

        Returns:
            bool: True si el stock es mayor a 0, False en caso contrario.

        Ejemplo:
            >>> product.is_available()
            True
        """
        return self.stock > 0

    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock del producto después de una venta.

        Args:
            quantity: Cantidad a reducir. Debe ser un entero positivo.

        Raises:
            ValueError: Si la cantidad no es positiva o si no hay suficiente stock.

        Ejemplo:
            >>> product.reduce_stock(2)
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser un entero positivo.")
        if self.stock < quantity:
            raise ValueError(
                f"Stock insuficiente. Disponible: {self.stock}, solicitado: {quantity}."
            )
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock del producto (reabastecimiento).

        Args:
            quantity: Cantidad a agregar. Debe ser un entero positivo.

        Raises:
            ValueError: Si la cantidad no es positiva.

        Ejemplo:
            >>> product.increase_stock(10)
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser un entero positivo.")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje individual en el chat.

    Permite distinguir entre mensajes del usuario y del asistente de IA,
    y mantiene el registro del historial conversacional.

    Atributos:
        id: Identificador único del mensaje (None si no ha sido persistido).
        session_id: Identificador de la sesión de conversación.
        role: Rol del emisor del mensaje ('user' o 'assistant').
        message: Contenido textual del mensaje.
        timestamp: Fecha y hora en que se envió el mensaje.

    Ejemplo:
        >>> msg = ChatMessage(id=None, session_id="cliente_001",
        ...     role="user", message="Hola", timestamp=datetime.utcnow())
    """

    id: Optional[int]
    session_id: str
    role: str
    message: str
    timestamp: datetime

    def __post_init__(self) -> None:
        """
        Valida los datos del mensaje inmediatamente después de la creación.

        Verifica que:
        - El rol sea 'user' o 'assistant'.
        - El mensaje no esté vacío.
        - El session_id no esté vacío.

        Raises:
            ValueError: Si alguna validación falla.
        """
        if self.role not in ("user", "assistant"):
            raise ValueError("El rol debe ser 'user' o 'assistant'.")
        if not self.message or not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío.")

    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje proviene del usuario.

        Returns:
            bool: True si el rol es 'user'.
        """
        return self.role == "user"

    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje proviene del asistente de IA.

        Returns:
            bool: True si el rol es 'assistant'.
        """
        return self.role == "assistant"


@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto de una conversación.

    Mantiene los mensajes recientes para dar coherencia al chat con IA.
    Permite que el asistente tenga 'memoria' de la conversación actual.

    Atributos:
        messages: Lista completa de mensajes de la sesión.
        max_messages: Número máximo de mensajes recientes a considerar (por defecto 6).

    Ejemplo:
        >>> context = ChatContext(messages=historial)
        >>> context.format_for_prompt()
        'Usuario: Hola\\nAsistente: ¡Hola! ¿En qué puedo ayudarte?'
    """

    messages: List[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes del historial conversacional.

        Returns:
            List[ChatMessage]: Los últimos 'max_messages' mensajes en orden cronológico.
        """
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        """
        Formatea los mensajes recientes en texto legible para el prompt de IA.

        El formato resultante permite que el modelo de lenguaje comprenda
        el flujo de la conversación anterior.

        Returns:
            str: Historial formateado con prefijos 'Usuario:' y 'Asistente:'.

        Ejemplo de salida:
            'Usuario: Busco zapatos Nike\\nAsistente: Tenemos varias opciones...'
        """
        lines = []
        for msg in self.get_recent_messages():
            prefix = "Usuario" if msg.is_from_user() else "Asistente"
            lines.append(f"{prefix}: {msg.message}")
        return "\n".join(lines)
