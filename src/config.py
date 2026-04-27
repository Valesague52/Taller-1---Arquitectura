"""
Módulo de configuración global de la aplicación.

Centraliza la lectura de variables de entorno y la configuración
de todos los parámetros de la aplicación usando python-dotenv.
"""

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env al entorno de Python
load_dotenv()


class Settings:
    """
    Clase de configuración global de la aplicación.

    Lee y expone todas las variables de configuración necesarias
    para el funcionamiento del sistema. Usa valores por defecto
    para entornos de desarrollo.

    Attributes:
        GEMINI_API_KEY: Clave de API de Google Gemini.
        DATABASE_URL: URL de conexión a la base de datos SQLite.
        ENVIRONMENT: Entorno de ejecución (development, production).
        APP_NAME: Nombre de la aplicación.
        APP_VERSION: Versión de la aplicación.

    Ejemplo:
        >>> settings = Settings()
        >>> print(settings.GEMINI_API_KEY)
        'AIzaSy...'
    """

    # API Key de Google Gemini (requerida para el chat con IA)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # URL de la base de datos SQLite
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///./data/ecommerce_chat.db"
    )

    # Entorno de ejecución
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Metadatos de la aplicación
    APP_NAME: str = "SneakerStore API"
    APP_VERSION: str = "1.0.0"

    # Configuración del chat
    CHAT_HISTORY_LIMIT: int = int(os.getenv("CHAT_HISTORY_LIMIT", "6"))

    @classmethod
    def is_development(cls) -> bool:
        """
        Verifica si la aplicación está en modo desarrollo.

        Returns:
            bool: True si el entorno es 'development'.
        """
        return cls.ENVIRONMENT == "development"

    @classmethod
    def validate(cls) -> None:
        """
        Valida que las variables de entorno críticas estén configuradas.

        Raises:
            ValueError: Si alguna variable requerida no está configurada.
        """
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY no está configurada. "
                "Por favor, agrega tu API key en el archivo .env"
            )


# Instancia global de configuración
settings = Settings()