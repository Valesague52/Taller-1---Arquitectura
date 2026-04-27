"""
Módulo de implementación del repositorio de productos con SQLAlchemy.

Implementa la interfaz IProductRepository usando SQLite como motor
de base de datos a través de SQLAlchemy ORM.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementación concreta del repositorio de productos usando SQLAlchemy.

    Convierte entre entidades del dominio y modelos ORM para mantener
    la separación entre capas. La capa de dominio nunca ve modelos ORM.

    Args:
        db: Sesión de SQLAlchemy para ejecutar operaciones en la base de datos.

    Ejemplo:
        >>> repo = SQLProductRepository(db_session)
        >>> productos = repo.get_all()
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con la sesión de base de datos.

        Args:
            db: Sesión activa de SQLAlchemy.
        """
        self._db = db

    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos de la base de datos.

        Returns:
            List[Product]: Lista de todas las entidades Product disponibles.
        """
        models = self._db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador único.

        Args:
            product_id: ID del producto a buscar.

        Returns:
            Optional[Product]: La entidad Product si existe, None si no se encontró.
        """
        model = (
            self._db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        if not model:
            return None
        return self._model_to_entity(model)

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene todos los productos de una marca específica.

        La búsqueda es insensible a mayúsculas/minúsculas.

        Args:
            brand: Nombre de la marca a filtrar.

        Returns:
            List[Product]: Lista de productos de la marca indicada.
        """
        models = (
            self._db.query(ProductModel)
            .filter(ProductModel.brand.ilike(f"%{brand}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene todos los productos de una categoría específica.

        La búsqueda es insensible a mayúsculas/minúsculas.

        Args:
            category: Categoría a filtrar (Running, Casual, Formal).

        Returns:
            List[Product]: Lista de productos de la categoría indicada.
        """
        models = (
            self._db.query(ProductModel)
            .filter(ProductModel.category.ilike(f"%{category}%"))
            .all()
        )
        return [self._model_to_entity(m) for m in models]

    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en la base de datos.

        Si el producto tiene ID, actualiza el registro existente.
        Si no tiene ID (es nuevo), crea un nuevo registro.

        Args:
            product: Entidad de dominio a persistir.

        Returns:
            Product: La entidad guardada con su ID asignado.
        """
        if product.id:
            # Actualizar producto existente
            model = (
                self._db.query(ProductModel)
                .filter(ProductModel.id == product.id)
                .first()
            )
            if model:
                model.name = product.name
                model.brand = product.brand
                model.category = product.category
                model.size = product.size
                model.color = product.color
                model.price = product.price
                model.stock = product.stock
                model.description = product.description
        else:
            # Crear nuevo producto
            model = self._entity_to_model(product)
            self._db.add(model)

        self._db.commit()
        self._db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto de la base de datos por su ID.

        Args:
            product_id: ID del producto a eliminar.

        Returns:
            bool: True si se eliminó, False si el producto no existía.
        """
        model = (
            self._db.query(ProductModel)
            .filter(ProductModel.id == product_id)
            .first()
        )
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM ProductModel a entidad de dominio Product.

        Mantiene la separación de capas: el dominio nunca conoce ProductModel.

        Args:
            model: Instancia del modelo ORM.

        Returns:
            Product: Entidad de dominio correspondiente.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description or "",
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """
        Convierte una entidad de dominio Product a modelo ORM ProductModel.

        Args:
            entity: Entidad de dominio a convertir.

        Returns:
            ProductModel: Instancia del modelo ORM lista para persistir.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )