"""
Módulo del servicio de IA con Google Gemini.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

from google import genai
#import google.generativeai as genai
from src.domain.entities import Product, ChatContext

# Forzar carga del .env usando ruta absoluta desde este archivo
_env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class GeminiService:
    """
    Servicio de inteligencia artificial usando Google Gemini (SDK v2).

    Encapsula la comunicación con la API de Gemini para generar
    respuestas contextualizadas en el chat del e-commerce.
    """

    def __init__(self) -> None:
        """
        Inicializa el servicio cargando la API key y configurando el cliente.

        Raises:
            ValueError: Si GEMINI_API_KEY no está configurada.
        """
        api_key = os.environ.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key or not api_key.strip():
            raise ValueError(
                "La variable de entorno GEMINI_API_KEY no está configurada."
            )
        self._client = genai.Client(api_key=api_key.strip())
        self._model = "gemini-2.5-flash"

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta de IA basada en el mensaje del usuario y el contexto.

        Args:
            user_message: Mensaje enviado por el usuario en este turno.
            products: Lista de productos disponibles en el inventario.
            context: Contexto conversacional con el historial reciente.

        Returns:
            str: Respuesta generada por el modelo de IA.

        Raises:
            Exception: Si ocurre un error al llamar a la API de Gemini.
        """
        try:
            productos_texto = self._format_products_info(products)
            historial_texto = context.format_for_prompt()
            prompt = self._build_prompt(user_message, productos_texto, historial_texto)

            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
            return response.text

        except Exception as e:
            raise Exception(f"Error al generar respuesta con Gemini: {str(e)}")

    def _format_products_info(self, products: List[Product]) -> str:
        """
        Formatea la lista de productos en texto legible para el prompt.

        Args:
            products: Lista de entidades Product a formatear.

        Returns:
            str: Texto formateado con la información de todos los productos.
        """
        if not products:
            return "No hay productos disponibles actualmente."
        lineas = []
        for p in products:
            disponibilidad = "Disponible" if p.is_available() else "Agotado"
            lineas.append(
                f"- {p.name} | {p.brand} | {p.category} | "
                f"Talla: {p.size} | {p.color} | "
                f"${p.price:.2f} | Stock: {p.stock} ({disponibilidad})"
            )
        return "\n".join(lineas)

    def _build_prompt(
        self,
        user_message: str,
        productos_texto: str,
        historial_texto: str,
    ) -> str:
        """
        Construye el prompt completo para enviar al modelo de Gemini.

        Args:
            user_message: Mensaje actual del usuario.
            productos_texto: Catálogo de productos formateado.
            historial_texto: Historial de conversación formateado.

        Returns:
            str: Prompt completo listo para enviar a Gemini.
        """
        historial_section = ""
        if historial_texto.strip():
            historial_section = (
                f"\nHISTORIAL DE CONVERSACIÓN RECIENTE:\n{historial_texto}\n"
            )

        return f"""Eres un asistente virtual experto en ventas de zapatos para SneakerStore.

PRODUCTOS DISPONIBLES:
{productos_texto}

INSTRUCCIONES:
- Sé amigable y profesional
- Recomienda productos específicos con nombre, precio y disponibilidad
- Si un producto está agotado, sugiere alternativas
- Responde siempre en español, máximo 3-4 oraciones
{historial_section}
MENSAJE DEL CLIENTE: {user_message}

RESPUESTA DEL ASISTENTE:"""