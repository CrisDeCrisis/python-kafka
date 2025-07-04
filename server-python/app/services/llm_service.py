"""
Servicio de modelo de lenguaje usando LangChain y Ollama
"""
import logging
from typing import List, Optional, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Servicio para interactuar con el modelo de lenguaje"""
    
    def __init__(self):
        self.llm = OllamaLLM(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=0.7
        )
        self.output_parser = StrOutputParser()
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Configura los templates de prompts"""
        self.chat_prompt = PromptTemplate.from_template(
            """Eres un asistente de IA útil y amigable. Responde de manera clara y concisa.

Usuario: {question}

Asistente:"""
        )
        
        self.context_prompt = PromptTemplate.from_template(
            """Eres un asistente de IA útil y amigable. Usa el contexto proporcionado para responder la pregunta de manera precisa.

Contexto:
{context}

Pregunta: {question}

Respuesta:"""
        )
    
    async def generate_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Genera una respuesta usando el modelo de lenguaje
        
        Args:
            question: Pregunta del usuario
            context: Contexto opcional para la respuesta
            temperature: Temperatura del modelo (opcional)
            
        Returns:
            Respuesta generada por el modelo
        """
        try:
            # Configurar temperatura si se especifica
            if temperature is not None:
                self.llm.temperature = temperature
            
            # Seleccionar prompt según si hay contexto
            if context:
                prompt = self.context_prompt
                input_vars = {"question": question, "context": context}
                logger.info(f"Generando respuesta con contexto para: {question[:50]}...")
            else:
                prompt = self.chat_prompt
                input_vars = {"question": question}
                logger.info(f"Generando respuesta sin contexto para: {question[:50]}...")
            
            # Crear cadena de procesamiento
            chain = prompt | self.llm | self.output_parser
            
            # Generar respuesta
            response = await chain.ainvoke(input_vars)
            
            logger.info("Respuesta generada exitosamente")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            raise
    
    async def generate_streaming_response(
        self, 
        question: str, 
        context: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        Genera una respuesta streaming usando el modelo de lenguaje
        
        Args:
            question: Pregunta del usuario
            context: Contexto opcional para la respuesta
            temperature: Temperatura del modelo (opcional)
            
        Yields:
            Chunks de la respuesta generada
        """
        try:
            # Configurar temperatura si se especifica
            if temperature is not None:
                self.llm.temperature = temperature
            
            # Seleccionar prompt según si hay contexto
            if context:
                prompt = self.context_prompt
                input_vars = {"question": question, "context": context}
                logger.info(f"Generando respuesta streaming con contexto para: {question[:50]}...")
            else:
                prompt = self.chat_prompt
                input_vars = {"question": question}
                logger.info(f"Generando respuesta streaming sin contexto para: {question[:50]}...")
            
            # Crear cadena de procesamiento
            chain = prompt | self.llm | self.output_parser
            
            # Generar respuesta streaming
            async for chunk in chain.astream(input_vars):
                yield chunk
            
            logger.info("Respuesta streaming generada exitosamente")
            
        except Exception as e:
            logger.error(f"Error generando respuesta streaming: {str(e)}")
            raise
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Formatea los documentos de contexto en un string
        
        Args:
            documents: Lista de documentos con contenido y metadatos
            
        Returns:
            String formateado con el contexto
        """
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            # Añadir información del documento
            context_part = f"Documento {i}:\n{content}"
            
            # Añadir metadatos si existen
            if metadata:
                context_part += f"\nMetadatos: {metadata}"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    async def check_model_availability(self) -> bool:
        """
        Verifica si el modelo está disponible
        
        Returns:
            True si el modelo está disponible, False en caso contrario
        """
        try:
            # Intentar generar una respuesta simple
            response = await self.generate_response("Test")
            return bool(response)
        except Exception as e:
            logger.error(f"Modelo no disponible: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información del modelo
        
        Returns:
            Diccionario con información del modelo
        """
        return {
            "model": settings.llm_model,
            "base_url": settings.ollama_base_url,
            "temperature": self.llm.temperature
        }
