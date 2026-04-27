"""
Módulo de implementación del repositorio de chat con SQLAlchemy.

Implementa la interfaz IChatRepository para persistir y recuperar
el historial de conversaciones del chat con IA.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Implementación concreta del repositorio de chat usando SQLAlchemy.

    Gestiona la persistencia del historial de conversaciones, permitiendo
    que el asistente de IA mantenga memoria entre mensajes.

    Args:
        db: Sesión de SQLAlchemy para ejecutar operaciones en la base de datos.

    Ejemplo:
        >>> repo = SQLChatRepository(db_session)
        >>> repo.save_message(chat_message)
        >>> historial = repo.get_session_history("cliente_001")
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con la sesión de base de datos.

        Args:
            db: Sesión activa de SQLAlchemy.
        """
        self._db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje del chat en la base de datos.

        Args:
            message: Entidad ChatMessage a persistir.

        Returns:
            ChatMessage: El mensaje guardado con su ID asignado.
        """
        model = self._entity_to_model(message)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo o parcial de una sesión de conversación.

        Los mensajes se retornan en orden cronológico (del más antiguo al más reciente).

        Args:
            session_id: Identificador de la sesión a consultar.
            limit: Si se especifica, retorna solo los últimos N mensajes.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico ascendente.
        """
        if limit:
            models = (
                self._db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.desc())
                .limit(limit)
                .all()
            )
            models.reverse()
        else:
            models = (
                self._db.query(ChatMemoryModel)
                .filter(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.timestamp.asc())
                .all()
            )
        return [self._model_to_entity(m) for m in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.

        Args:
            session_id: Identificador de la sesión a limpiar.

        Returns:
            int: Número de mensajes eliminados.
        """
        deleted_count = (
            self._db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete()
        )
        self._db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión en orden cronológico.

        Este método es el más usado para construir el contexto conversacional
        antes de llamar al modelo de IA.

        Args:
            session_id: Identificador de la sesión.
            count: Número máximo de mensajes recientes a retornar.

        Returns:
            List[ChatMessage]: Los N mensajes más recientes en orden ascendente.
        """
        models = (
            self._db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        models.reverse()
        return [self._model_to_entity(m) for m in models]

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM ChatMemoryModel a entidad de dominio ChatMessage.

        Args:
            model: Instancia del modelo ORM.

        Returns:
            ChatMessage: Entidad de dominio correspondiente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad de dominio ChatMessage a modelo ORM ChatMemoryModel.

        Args:
            entity: Entidad de dominio a convertir.

        Returns:
            ChatMemoryModel: Instancia del modelo ORM lista para persistir.
        """
        ts = entity.timestamp if entity.timestamp else datetime.now(timezone.utc)
        # Convertir a naive datetime si tiene tzinfo (SQLite no maneja tz)
        if ts.tzinfo is not None:
            ts = ts.replace(tzinfo=None)
        return ChatMemoryModel(
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=ts,
        )