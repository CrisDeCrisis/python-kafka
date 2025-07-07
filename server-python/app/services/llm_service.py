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

# Constantes
DEFAULT_TEMPERATURE = 0.4
QUESTION_PREVIEW_LENGTH = 50
TEST_QUESTION = "¿Estás funcionando?"


class LLMService:
    """Servicio para interactuar con el modelo de lenguaje"""
    
    def __init__(self):
        self.llm = OllamaLLM(
            model=settings.llm_model,
            base_url=settings.ollama_base_url,
            temperature=DEFAULT_TEMPERATURE
        )
        self.output_parser = StrOutputParser()
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Configura los templates de prompts"""
        self.chat_prompt = PromptTemplate.from_template(
            "Eres un guia turistico en la provincia de Formosa, Argentina. Tu nombre es JabiTur. Responde de manera clara y concisa.\n\n"
            "Usuario: {question}\n\n"
            "Asistente:"
        )
        
        self.context_prompt = PromptTemplate.from_template(
            "Eres un asistente de IA útil y amigable. Usa el contexto proporcionado para responder la pregunta de manera precisa.\n\n"
            "Contexto:\n{context}\n\n"
            "Pregunta: {question}\n\n"
            "Respuesta:"
        )
    
    def _prepare_chain(self, question: str, context: Optional[str] = None, temperature: Optional[float] = None):
        """
        Prepara la cadena de procesamiento y variables de entrada
        
        Args:
            question: Pregunta del usuario
            context: Contexto opcional para la respuesta
            temperature: Temperatura del modelo (opcional)
            
        Returns:
            Tupla con (chain, input_vars, log_message)
        """
        # Configurar temperatura si se especifica
        if temperature is not None:
            self.llm.temperature = temperature
        
        # Seleccionar prompt según si hay contexto
        if context:
            prompt = self.context_prompt
            input_vars = {"question": question, "context": context}
            log_message = f"con contexto para: {question[:QUESTION_PREVIEW_LENGTH]}..."
        else:
            prompt = self.chat_prompt
            input_vars = {"question": question}
            log_message = f"sin contexto para: {question[:QUESTION_PREVIEW_LENGTH]}..."
        
        # Crear cadena de procesamiento
        chain = prompt | self.llm | self.output_parser
        
        return chain, input_vars, log_message
    
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
            chain, input_vars, log_message = self._prepare_chain(question, context, temperature)
            logger.info(f"Generando respuesta {log_message}")
            
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
            chain, input_vars, log_message = self._prepare_chain(question, context, temperature)
            logger.info(f"Generando respuesta streaming {log_message}")
            
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
            
            # Construir parte del contexto
            context_part = f"Documento {i}:\n{content}"
            
            # Añadir metadatos si existen
            if metadata:
                metadata_str = ", ".join(f"{k}: {v}" for k, v in metadata.items())
                context_part += f"\nMetadatos: {metadata_str}"
            
            context_parts.append(context_part)
        
        return "\n\n".join(context_parts)
    
    async def check_model_availability(self) -> bool:
        """
        Verifica si el modelo está disponible
        
        Returns:
            True si el modelo está disponible, False en caso contrario
        """
        try:
            # Intentar generar una respuesta simple con timeout implícito
            response = await self.generate_response(TEST_QUESTION)
            
            # Verificar que la respuesta no esté vacía
            is_available = bool(response and response.strip())
            
            if is_available:
                logger.info("Modelo disponible y funcionando correctamente")
            else:
                logger.warning("Modelo disponible pero respuesta vacía")
            
            return is_available
            
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
