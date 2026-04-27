"""
Módulo del servicio de productos de la capa de aplicación.

Implementa los casos de uso relacionados con la gestión de productos,
orquestando las operaciones entre el dominio y los repositorios.
"""

from typing import List, Optional

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError, InvalidProductDataError
from src.application.dtos import ProductDTO, ProductFilterDTO


class ProductService:
    """
    Servicio de aplicación para la gestión de productos del e-commerce.

    Orquesta los casos de uso de productos usando el repositorio inyectado.
    No contiene lógica de acceso a datos; delega esa responsabilidad al repositorio.

    Args:
        product_repository: Implementación del repositorio de productos.

    Ejemplo:
        >>> repo = SQLProductRepository(db)
        >>> service = ProductService(repo)
        >>> productos = service.get_all_products()
    """

    def __init__(self, product_repository: IProductRepository) -> None:
        """
        Inicializa el servicio con el repositorio de productos.

        Args:
            product_repository: Repositorio que implementa IProductRepository.
        """
        self._repository = product_repository

    def get_all_products(self) -> List[ProductDTO]:
        """
        Obtiene todos los productos disponibles en el e-commerce.

        Returns:
            List[ProductDTO]: Lista de todos los productos convertidos a DTO.
        """
        products = self._repository.get_all()
        return [self._entity_to_dto(p) for p in products]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        """
        Obtiene un producto específico por su identificador único.

        Args:
            product_id: Identificador del producto a buscar.

        Returns:
            ProductDTO: Datos del producto encontrado.

        Raises:
            ProductNotFoundError: Si el producto no existe en el repositorio.
        """
        product = self._repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id=product_id)
        return self._entity_to_dto(product)

    def search_products(self, filters: ProductFilterDTO) -> List[ProductDTO]:
        """
        Busca productos aplicando filtros opcionales de marca y categoría.

        Args:
            filters: DTO con los criterios de filtrado.

        Returns:
            List[ProductDTO]: Lista de productos que cumplen los filtros.
        """
        if filters.brand:
            products = self._repository.get_by_brand(filters.brand)
        elif filters.category:
            products = self._repository.get_by_category(filters.category)
        else:
            products = self._repository.get_all()

        if filters.available_only:
            products = [p for p in products if p.is_available()]

        return [self._entity_to_dto(p) for p in products]

    def get_available_products(self) -> List[ProductDTO]:
        """
        Obtiene únicamente los productos con stock disponible (stock > 0).

        Returns:
            List[ProductDTO]: Lista de productos disponibles para compra.
        """
        products = self._repository.get_all()
        available = [p for p in products if p.is_available()]
        return [self._entity_to_dto(p) for p in available]

    def create_product(self, product_dto: ProductDTO) -> ProductDTO:
        """
        Crea un nuevo producto en el repositorio.

        Convierte el DTO en una entidad de dominio para aplicar
        validaciones de negocio antes de persistir.

        Args:
            product_dto: DTO con los datos del nuevo producto.

        Returns:
            ProductDTO: El producto creado con su ID asignado.

        Raises:
            InvalidProductDataError: Si los datos del producto son inválidos.
        """
        try:
            product = self._dto_to_entity(product_dto)
            saved = self._repository.save(product)
            return self._entity_to_dto(saved)
        except ValueError as e:
            raise InvalidProductDataError(str(e))

    def update_product(self, product_id: int, product_dto: ProductDTO) -> ProductDTO:
        """
        Actualiza un producto existente en el repositorio.

        Primero verifica que el producto exista, luego aplica los cambios.

        Args:
            product_id: ID del producto a actualizar.
            product_dto: DTO con los nuevos datos del producto.

        Returns:
            ProductDTO: El producto actualizado.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los datos son inválidos.
        """
        existing = self._repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id=product_id)

        try:
            product = self._dto_to_entity(product_dto)
            product.id = product_id
            updated = self._repository.save(product)
            return self._entity_to_dto(updated)
        except ValueError as e:
            raise InvalidProductDataError(str(e))

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto del repositorio.

        Args:
            product_id: ID del producto a eliminar.

        Returns:
            bool: True si se eliminó correctamente.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        existing = self._repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id=product_id)
        return self._repository.delete(product_id)

    def _entity_to_dto(self, product: Product) -> ProductDTO:
        """
        Convierte una entidad de dominio Product a ProductDTO.

        Args:
            product: Entidad de dominio a convertir.

        Returns:
            ProductDTO: DTO con los datos del producto.
        """
        return ProductDTO(
            id=product.id,
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )

    def _dto_to_entity(self, dto: ProductDTO) -> Product:
        """
        Convierte un ProductDTO a entidad de dominio Product.

        Args:
            dto: DTO a convertir en entidad.

        Returns:
            Product: Entidad de dominio con los datos del DTO.
        """
        return Product(
            id=dto.id,
            name=dto.name,
            brand=dto.brand,
            category=dto.category,
            size=dto.size,
            color=dto.color,
            price=dto.price,
            stock=dto.stock,
            description=dto.description,
        )