"""
Módulo del servicio de chat de la capa de aplicación.

Implementa el caso de uso principal del sistema: procesar mensajes de usuario,
obtener contexto conversacional, llamar a la IA de Gemini y persistir el historial.
"""

from datetime import datetime
from typing import List, Optional

from src.domain.entities import ChatMessage, ChatContext
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.exceptions import ChatServiceError
from src.application.dtos import (
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)


class ChatService:
    """
    Servicio de aplicación para el chat inteligente con IA.

    Orquesta el flujo completo de una conversación:
    1. Recupera productos disponibles del repositorio.
    2. Obtiene el historial reciente de la sesión.
    3. Construye el contexto conversacional.
    4. Llama al servicio de IA (Gemini) con el contexto.
    5. Persiste los mensajes del usuario y del asistente.
    6. Retorna la respuesta al cliente.

    Args:
        product_repository: Repositorio de productos para contexto del chat.
        chat_repository: Repositorio para persistir el historial de mensajes.
        ai_service: Servicio de IA (GeminiService) para generar respuestas.

    Ejemplo:
        >>> service = ChatService(product_repo, chat_repo, gemini_service)
        >>> respuesta = await service.process_message(request_dto)
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service,
    ) -> None:
        """
        Inicializa el servicio con sus dependencias inyectadas.

        Args:
            product_repository: Repositorio de productos.
            chat_repository: Repositorio de historial de chat.
            ai_service: Servicio de generación de respuestas IA.
        """
        self._product_repository = product_repository
        self._chat_repository = chat_repository
        self._ai_service = ai_service

    async def process_message(
        self, request: ChatMessageRequestDTO
    ) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje de usuario y genera una respuesta con IA.

        Flujo completo:
        1. Obtiene lista de productos disponibles para contexto.
        2. Recupera los últimos 6 mensajes del historial de la sesión.
        3. Crea un ChatContext con el historial.
        4. Llama a Gemini AI con el mensaje, productos y contexto.
        5. Guarda el mensaje del usuario en la base de datos.
        6. Guarda la respuesta del asistente en la base de datos.
        7. Retorna el DTO de respuesta al cliente.

        Args:
            request: DTO con session_id y message del usuario.

        Returns:
            ChatMessageResponseDTO: Respuesta con el mensaje del asistente.

        Raises:
            ChatServiceError: Si ocurre un error durante el procesamiento.
        """
        try:
            # 1. Obtener productos disponibles para dar contexto a la IA
            products = self._product_repository.get_all()

            # 2. Recuperar historial reciente de la sesión (últimos 6 mensajes)
            recent_messages = self._chat_repository.get_recent_messages(
                session_id=request.session_id, count=6
            )

            # 3. Crear contexto conversacional
            context = ChatContext(messages=recent_messages)

            # 4. Llamar al servicio de IA con el mensaje, productos y contexto
            assistant_response = await self._ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            timestamp = datetime.utcnow()

            # 5. Guardar mensaje del usuario
            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=timestamp,
            )
            self._chat_repository.save_message(user_message)

            # 6. Guardar respuesta del asistente
            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=datetime.utcnow(),
            )
            self._chat_repository.save_message(assistant_message)

            # 7. Retornar DTO de respuesta
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=timestamp,
            )

        except Exception as e:
            raise ChatServiceError(
                f"Error al procesar el mensaje de chat: {str(e)}"
            )

    def get_session_history(
        self, session_id: str, limit: Optional[int] = 10
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial de conversación de una sesión.

        Args:
            session_id: Identificador de la sesión de usuario.
            limit: Número máximo de mensajes a retornar (default: 10).

        Returns:
            List[ChatHistoryDTO]: Lista de mensajes del historial.
        """
        messages = self._chat_repository.get_session_history(
            session_id=session_id, limit=limit
        )
        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de conversación de una sesión.

        Útil para reiniciar conversaciones o gestionar el almacenamiento.

        Args:
            session_id: Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        return self._chat_repository.delete_session_history(session_id=session_id)