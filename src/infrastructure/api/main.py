"""
Módulo principal de la API REST con FastAPI.

Define la aplicación FastAPI, configura el middleware CORS,
registra los endpoints y gestiona el ciclo de vida de la aplicación.
Este es el punto de entrada de la capa de infraestructura.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import (
    ProductDTO,
    ProductFilterDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)
from src.domain.exceptions import ProductNotFoundError, ChatServiceError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de la aplicación FastAPI.

    Ejecuta la inicialización de la base de datos al arrancar
    y puede ejecutar limpieza al apagar.

    Args:
        app: Instancia de la aplicación FastAPI.
    """
    # Código de inicio: inicializar base de datos y cargar datos de ejemplo
    init_db()
    yield
    # Código de apagado (si se necesita)


# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title="SneakerStore API",
    description=(
        "API REST de e-commerce de zapatos con chat inteligente powered by Google Gemini. "
        "Implementada con Clean Architecture (Domain, Application, Infrastructure layers). "
        "Universidad EAFIT - Taller de Construcción de Software."
    ),
    version="1.0.0",
    contact={
        "name": "SneakerStore Team",
        "email": "sneakerstore@eafit.edu.co",
    },
    lifespan=lifespan,
)

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ENDPOINTS DE INFORMACIÓN GENERAL
# ─────────────────────────────────────────────


@app.get(
    "/",
    tags=["General"],
    summary="Información de la API",
    description="Retorna información básica sobre la API y sus endpoints disponibles.",
)
def root():
    """
    Endpoint raíz que provee información general de la API.

    Returns:
        dict: Información de la API incluyendo versión, descripción y endpoints.
    """
    return {
        "nombre": "SneakerStore API",
        "version": "1.0.0",
        "descripcion": "E-commerce de zapatos con chat inteligente IA",
        "tecnologias": ["FastAPI", "SQLAlchemy", "Google Gemini", "SQLite"],
        "arquitectura": "Clean Architecture (Domain → Application → Infrastructure)",
        "endpoints": {
            "productos": {
                "GET /products": "Lista todos los productos",
                "GET /products/{id}": "Obtiene un producto por ID",
                "GET /products/brand/{brand}": "Filtra por marca",
                "GET /products/category/{category}": "Filtra por categoría",
            },
            "chat": {
                "POST /chat": "Envía mensaje al asistente de IA",
                "GET /chat/history/{session_id}": "Obtiene historial de conversación",
                "DELETE /chat/history/{session_id}": "Limpia historial de sesión",
            },
        },
        "documentacion": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
    }


# ─────────────────────────────────────────────
# ENDPOINTS DE PRODUCTOS
# ─────────────────────────────────────────────


@app.get(
    "/products",
    response_model=List[ProductDTO],
    tags=["Productos"],
    summary="Listar todos los productos",
    description="Retorna la lista completa de productos disponibles en el e-commerce. "
    "Opcionalmente filtra por marca, categoría o disponibilidad.",
)
def get_products(
    brand: Optional[str] = Query(None, description="Filtrar por marca (ej: Nike, Adidas)"),
    category: Optional[str] = Query(None, description="Filtrar por categoría (Running, Casual, Formal)"),
    available_only: bool = Query(False, description="Solo mostrar productos con stock disponible"),
    db: Session = Depends(get_db),
):
    """
    Lista todos los productos con filtros opcionales.

    Args:
        brand: Filtrar por marca específica.
        category: Filtrar por categoría de producto.
        available_only: Si True, solo retorna productos con stock > 0.
        db: Sesión de base de datos (inyectada por FastAPI).

    Returns:
        List[ProductDTO]: Lista de productos que cumplen los filtros.
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    filters = ProductFilterDTO(
        brand=brand,
        category=category,
        available_only=available_only,
    )
    return service.search_products(filters)


@app.get(
    "/products/{product_id}",
    response_model=ProductDTO,
    tags=["Productos"],
    summary="Obtener producto por ID",
    description="Retorna los detalles completos de un producto específico por su ID.",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto específico por su identificador único.

    Args:
        product_id: ID del producto a buscar.
        db: Sesión de base de datos (inyectada por FastAPI).

    Returns:
        ProductDTO: Datos completos del producto.

    Raises:
        HTTPException 404: Si el producto no existe en la base de datos.
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    try:
        return service.get_product_by_id(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─────────────────────────────────────────────
# ENDPOINTS DE CHAT CON IA
# ─────────────────────────────────────────────


@app.post(
    "/chat",
    response_model=ChatMessageResponseDTO,
    tags=["Chat IA"],
    summary="Enviar mensaje al asistente de IA",
    description=(
        "Envía un mensaje al asistente virtual de SneakerStore. "
        "El asistente tiene acceso al inventario completo y memoria conversacional. "
        "Usa el mismo session_id para mantener el contexto entre mensajes."
    ),
)
async def chat(request: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    """
    Procesa un mensaje del usuario y retorna la respuesta del asistente de IA.

    Flujo interno:
    1. Obtiene catálogo de productos para contexto.
    2. Recupera historial de conversación de la sesión.
    3. Envía contexto + mensaje a Google Gemini.
    4. Persiste la conversación en la base de datos.
    5. Retorna la respuesta generada.

    Args:
        request: DTO con session_id y message del usuario.
        db: Sesión de base de datos (inyectada por FastAPI).

    Returns:
        ChatMessageResponseDTO: Respuesta del asistente con el mensaje generado.

    Raises:
        HTTPException 500: Si ocurre un error al procesar el mensaje.
    """
    try:
        product_repo = SQLProductRepository(db)
        chat_repo = SQLChatRepository(db)
        gemini_service = GeminiService()
        service = ChatService(product_repo, chat_repo, gemini_service)
        return await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al procesar el chat: {str(e)}",
        )


@app.get(
    "/chat/history/{session_id}",
    response_model=List[ChatHistoryDTO],
    tags=["Chat IA"],
    summary="Obtener historial de conversación",
    description="Retorna el historial de mensajes de una sesión específica.",
)
def get_chat_history(
    session_id: str,
    limit: int = Query(10, ge=1, le=100, description="Número máximo de mensajes a retornar"),
    db: Session = Depends(get_db),
):
    """
    Obtiene el historial de conversación de una sesión.

    Args:
        session_id: Identificador único de la sesión de usuario.
        limit: Número máximo de mensajes a retornar (1-100).
        db: Sesión de base de datos (inyectada por FastAPI).

    Returns:
        List[ChatHistoryDTO]: Lista de mensajes del historial en orden cronológico.
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    gemini_service = GeminiService()
    service = ChatService(product_repo, chat_repo, gemini_service)
    return service.get_session_history(session_id=session_id, limit=limit)


@app.delete(
    "/chat/history/{session_id}",
    tags=["Chat IA"],
    summary="Limpiar historial de sesión",
    description="Elimina todos los mensajes del historial de una sesión específica.",
)
def clear_chat_history(session_id: str, db: Session = Depends(get_db)):
    """
    Elimina el historial completo de una sesión de conversación.

    Útil para reiniciar una conversación desde cero sin cambiar de session_id.

    Args:
        session_id: Identificador de la sesión a limpiar.
        db: Sesión de base de datos (inyectada por FastAPI).

    Returns:
        dict: Confirmación con el número de mensajes eliminados.
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    gemini_service = GeminiService()
    service = ChatService(product_repo, chat_repo, gemini_service)
    deleted = service.clear_session_history(session_id=session_id)
    return {
        "mensaje": f"Historial de sesión '{session_id}' eliminado exitosamente.",
        "mensajes_eliminados": deleted,
    }
