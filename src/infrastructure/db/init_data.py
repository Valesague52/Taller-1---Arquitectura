"""
Módulo de carga de datos iniciales para la base de datos.

Popula la base de datos con productos de ejemplo al iniciar la aplicación
por primera vez. Solo carga datos si la tabla de productos está vacía.
"""

from sqlalchemy.orm import Session
from src.infrastructure.db.models import ProductModel


def load_initial_data(db: Session) -> None:
    """
    Carga productos de ejemplo en la base de datos si está vacía.

    Verifica si ya existen productos antes de insertar para evitar
    duplicados en reinicios de la aplicación.

    Args:
        db: Sesión activa de SQLAlchemy para realizar las operaciones.

    Ejemplo:
        >>> db = SessionLocal()
        >>> load_initial_data(db)
        # Inserta 12 productos si la tabla está vacía
    """
    # Verificar si ya existen productos para no duplicar datos
    existing_count = db.query(ProductModel).count()
    if existing_count > 0:
        return

    # Lista de productos iniciales variados por marca, categoría y precio
    productos_iniciales = [
        ProductModel(
            name="Air Zoom Pegasus 40",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro/Blanco",
            price=120.00,
            stock=5,
            description="Zapatilla de running de alta amortiguación. Ideal para corredores de distancia media y larga. Suela reactiva Zoom Air.",
        ),
        ProductModel(
            name="Air Force 1 Low",
            brand="Nike",
            category="Casual",
            size="41",
            color="Blanco",
            price=95.00,
            stock=8,
            description="Clásico icónico de Nike para uso diario. Cuero premium, suela de goma resistente y estilo atemporal.",
        ),
        ProductModel(
            name="Ultraboost 22",
            brand="Adidas",
            category="Running",
            size="43",
            color="Gris/Naranja",
            price=150.00,
            stock=3,
            description="Máxima energía de retorno con tecnología Boost. Tejido Primeknit adaptable y suela Continental™.",
        ),
        ProductModel(
            name="Stan Smith",
            brand="Adidas",
            category="Casual",
            size="40",
            color="Blanco/Verde",
            price=80.00,
            stock=10,
            description="El clásico tenis de tenis convertido en ícono de la moda. Cuero suave y diseño minimalista.",
        ),
        ProductModel(
            name="Suede Classic XXI",
            brand="Puma",
            category="Casual",
            size="41",
            color="Azul Navy",
            price=75.00,
            stock=12,
            description="Diseño retro con gamuza premium. Amortiguación SoftFoam+ para comodidad todo el día.",
        ),
        ProductModel(
            name="RS-X Toys",
            brand="Puma",
            category="Running",
            size="42",
            color="Multicolor",
            price=110.00,
            stock=4,
            description="Zapatilla chunky con tecnología RS (Running System) renovada. Diseño futurista y llamativo.",
        ),
        ProductModel(
            name="Chuck Taylor All Star",
            brand="Converse",
            category="Casual",
            size="39",
            color="Rojo",
            price=65.00,
            stock=15,
            description="El botín de lona más icónico de la historia. Suela vulcanizada y puntera de goma.",
        ),
        ProductModel(
            name="New Balance 574",
            brand="New Balance",
            category="Casual",
            size="43",
            color="Gris/Borgoña",
            price=90.00,
            stock=6,
            description="Estilo heritage con tecnología moderna. Entresuela ENCAP para soporte y amortiguación duradera.",
        ),
        ProductModel(
            name="Fresh Foam 1080v12",
            brand="New Balance",
            category="Running",
            size="44",
            color="Negro/Amarillo",
            price=165.00,
            stock=2,
            description="La zapatilla de running premium de New Balance. Espuma Fresh Foam X para máxima suavidad en cada zancada.",
        ),
        ProductModel(
            name="Old Skool",
            brand="Vans",
            category="Casual",
            size="40",
            color="Negro/Blanco",
            price=70.00,
            stock=20,
            description="El clásico botín con la icónica línea lateral. Lona y gamuza, suela de goma Waffle.",
        ),
        ProductModel(
            name="Gel-Nimbus 25",
            brand="ASICS",
            category="Running",
            size="42",
            color="Azul/Plata",
            price=180.00,
            stock=3,
            description="La zapatilla de running de larga distancia de ASICS. Tecnología GEL™ para máxima amortiguación.",
        ),
        ProductModel(
            name="Cloudstratus",
            brand="On Running",
            category="Running",
            size="41",
            color="Blanco/Gris",
            price=200.00,
            stock=1,
            description="Doble capa de CloudTec® para máxima amortiguación y estabilidad. Para corredores que buscan lo mejor.",
        ),
    ]

    # Insertar todos los productos en una sola operación
    db.add_all(productos_iniciales)
    db.commit()