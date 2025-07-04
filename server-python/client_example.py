"""
Cliente de ejemplo para probar el servidor de IA
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any


class AIServerClient:
    """Cliente para interactuar con el servidor de IA"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def chat(
        self, 
        message: str, 
        conversation_id: str = None,
        use_context: bool = True,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de chat al servidor
        
        Args:
            message: Mensaje a enviar
            conversation_id: ID de la conversación
            use_context: Si usar contexto previo
            temperature: Temperatura del modelo
            
        Returns:
            Respuesta del servidor
        """
        payload = {
            "message": message,
            "use_context": use_context,
            "temperature": temperature
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        async with self.session.post(
            f"{self.base_url}/chat/",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            return await response.json()
    
    async def add_document(
        self, 
        content: str, 
        metadata: Dict[str, Any] = None,
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Añade un documento al contexto
        
        Args:
            content: Contenido del documento
            metadata: Metadatos del documento
            conversation_id: ID de la conversación
            
        Returns:
            Respuesta del servidor
        """
        payload = {
            "content": content,
            "metadata": metadata or {},
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        async with self.session.post(
            f"{self.base_url}/documents/",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            return await response.json()
    
    async def get_health(self) -> Dict[str, Any]:
        """
        Obtiene el estado del servidor
        
        Returns:
            Estado del servidor
        """
        async with self.session.get(f"{self.base_url}/health/") as response:
            return await response.json()
    
    async def get_conversation_history(
        self, 
        conversation_id: str, 
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Obtiene el historial de una conversación
        
        Args:
            conversation_id: ID de la conversación
            limit: Límite de mensajes
            
        Returns:
            Historial de la conversación
        """
        async with self.session.get(
            f"{self.base_url}/chat/history/{conversation_id}",
            params={"limit": limit}
        ) as response:
            return await response.json()


async def main():
    """Función principal de ejemplo"""
    
    async with AIServerClient() as client:
        print("=== Verificando estado del servidor ===")
        health = await client.get_health()
        print(f"Estado: {health}")
        
        print("\n=== Añadiendo documento de ejemplo ===")
        doc_response = await client.add_document(
            content="El servidor de IA utiliza phi3:3.8b como modelo de lenguaje principal y nomic-embed-text para generar embeddings. Está construido con FastAPI y LangChain.",
            metadata={"tipo": "documentación", "tema": "arquitectura"},
            conversation_id="ejemplo-123"
        )
        print(f"Documento añadido: {doc_response}")
        
        print("\n=== Enviando mensaje de chat ===")
        chat_response = await client.chat(
            message="¿Qué modelo de lenguaje utiliza el servidor?",
            conversation_id="ejemplo-123",
            use_context=True,
            temperature=0.7
        )
        print(f"Respuesta: {chat_response['response']}")
        print(f"Contexto usado: {chat_response['context_used']}")
        
        print("\n=== Enviando otro mensaje ===")
        chat_response2 = await client.chat(
            message="¿Y para embeddings?",
            conversation_id="ejemplo-123",
            use_context=True
        )
        print(f"Respuesta: {chat_response2['response']}")
        
        print("\n=== Obteniendo historial de conversación ===")
        history = await client.get_conversation_history("ejemplo-123")
        print(f"Mensajes en historial: {history['total']}")


if __name__ == "__main__":
    asyncio.run(main())
