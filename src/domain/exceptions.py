"""
Excepciones específicas del dominio de negocio.

Representan errores de negocio, no errores técnicos. Su uso permite
distinguir claramente entre fallas de lógica empresarial y errores
de infraestructura o sistema.
"""


class ProductNotFoundError(Exception):
    """
    Excepción lanzada cuando se busca un producto que no existe en el repositorio.

    Args:
        product_id: Identificador del producto no encontrado (opcional).

    Ejemplo:
        >>> raise ProductNotFoundError(product_id=42)
        ProductNotFoundError: Producto con ID 42 no encontrado
    """

    def __init__(self, product_id: int = None) -> None:
        """
        Inicializa la excepción con un mensaje descriptivo.

        Args:
            product_id: ID del producto que no fue encontrado.
        """
        if product_id is not None:
            self.message = f"Producto con ID {product_id} no encontrado."
        else:
            self.message = "Producto no encontrado."
        super().__init__(self.message)


class InvalidProductDataError(Exception):
    """
    Excepción lanzada cuando los datos de un producto son inválidos.

    Se usa cuando los datos violan las reglas de negocio definidas
    en la entidad Product o en los DTOs.

    Args:
        message: Mensaje descriptivo del error de validación.

    Ejemplo:
        >>> raise InvalidProductDataError("El precio debe ser mayor a 0")
    """

    def __init__(self, message: str = "Datos de producto inválidos.") -> None:
        """
        Inicializa la excepción con un mensaje personalizable.

        Args:
            message: Descripción del error de validación.
        """
        self.message = message
        super().__init__(self.message)


class ChatServiceError(Exception):
    """
    Excepción lanzada cuando ocurre un error en el servicio de chat con IA.

    Puede indicar problemas con la API de Gemini, timeout, o cualquier
    falla en el procesamiento de mensajes.

    Args:
        message: Mensaje descriptivo del error ocurrido.

    Ejemplo:
        >>> raise ChatServiceError("Error al conectar con la API de Gemini")
    """

    def __init__(self, message: str = "Error en el servicio de chat.") -> None:
        """
        Inicializa la excepción con un mensaje personalizable.

        Args:
            message: Descripción del error de chat.
        """
        self.message = message
        super().__init__(self.message)


class InsufficientStockError(Exception):
    """
    Excepción lanzada cuando se intenta vender más unidades de las disponibles.

    Args:
        product_name: Nombre del producto sin stock suficiente.
        available: Stock disponible actualmente.
        requested: Cantidad solicitada.

    Ejemplo:
        >>> raise InsufficientStockError("Nike Air", available=2, requested=5)
    """

    def __init__(
        self,
        product_name: str = "",
        available: int = 0,
        requested: int = 0,
    ) -> None:
        """
        Inicializa la excepción con información del stock.

        Args:
            product_name: Nombre del producto.
            available: Unidades disponibles en inventario.
            requested: Unidades solicitadas por el usuario.
        """
        self.message = (
            f"Stock insuficiente para '{product_name}'. "
            f"Disponible: {available}, solicitado: {requested}."
        )
        super().__init__(self.message)