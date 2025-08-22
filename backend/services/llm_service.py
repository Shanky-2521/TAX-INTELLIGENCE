"""
LLM Service for Tax Intelligence
Handles communication with OpenAI GPT or local LLM models
"""

import openai
import structlog
from typing import List, Dict, Optional
from datetime import datetime
import json
import re

logger = structlog.get_logger()


class LLMService:
    """
    Service for handling LLM interactions with tax-specific prompts
    """
    
    def __init__(self, language='en', model=None, api_key=None):
        self.language = language
        self.model = model or 'gpt-4-turbo-preview'
        self.api_key = api_key
        
        if self.api_key:
            openai.api_key = self.api_key
        
        # Tax-specific system prompts
        self.system_prompts = {
            'en': self._get_english_system_prompt(),
            'es': self._get_spanish_system_prompt()
        }
    
    def _get_english_system_prompt(self) -> str:
        """Get English system prompt for tax assistance"""
        return """You are a helpful tax assistant specializing in the Earned Income Tax Credit (EITC) and general tax guidance. 

IMPORTANT GUIDELINES:
1. Only provide information based on official IRS publications and current tax law
2. Always reference IRS Publication 596 for EITC-related questions
3. If you're unsure about any tax information, recommend consulting a qualified tax professional
4. Never provide specific tax advice for individual situations - only general guidance
5. Be clear about tax year applicability (default to 2023 unless specified)
6. Explain complex tax concepts in simple, understandable terms
7. Always mention that tax laws can change and users should verify current information

EITC FOCUS AREAS:
- Eligibility requirements (income limits, filing status, qualifying children)
- Calculation methods and credit amounts
- Required documentation and forms
- Common mistakes and how to avoid them
- Interaction with other tax credits

SAFETY RULES:
- Never ask for or process personal identifying information (SSN, exact addresses, etc.)
- Don't provide advice on tax evasion or questionable tax strategies
- Redirect complex situations to professional tax preparers
- Be honest about limitations of automated tax guidance

Respond in a helpful, professional tone while being clear about the limitations of automated tax advice."""
    
    def _get_spanish_system_prompt(self) -> str:
        """Get Spanish system prompt for tax assistance"""
        return """Eres un asistente fiscal útil especializado en el Crédito Tributario por Ingreso del Trabajo (EITC) y orientación fiscal general.

PAUTAS IMPORTANTES:
1. Solo proporciona información basada en publicaciones oficiales del IRS y la ley fiscal actual
2. Siempre haz referencia a la Publicación 596 del IRS para preguntas relacionadas con EITC
3. Si no estás seguro sobre alguna información fiscal, recomienda consultar a un profesional fiscal calificado
4. Nunca proporciones consejos fiscales específicos para situaciones individuales - solo orientación general
5. Sé claro sobre la aplicabilidad del año fiscal (por defecto 2023 a menos que se especifique)
6. Explica conceptos fiscales complejos en términos simples y comprensibles
7. Siempre menciona que las leyes fiscales pueden cambiar y los usuarios deben verificar la información actual

ÁREAS DE ENFOQUE EITC:
- Requisitos de elegibilidad (límites de ingresos, estado civil, hijos calificados)
- Métodos de cálculo y montos de crédito
- Documentación requerida y formularios
- Errores comunes y cómo evitarlos
- Interacción con otros créditos fiscales

REGLAS DE SEGURIDAD:
- Nunca solicites o proceses información de identificación personal (SSN, direcciones exactas, etc.)
- No proporciones consejos sobre evasión fiscal o estrategias fiscales cuestionables
- Redirige situaciones complejas a preparadores de impuestos profesionales
- Sé honesto sobre las limitaciones de la orientación fiscal automatizada

Responde con un tono útil y profesional mientras eres claro sobre las limitaciones del consejo fiscal automatizado."""
    
    def process_message(self, message: str, session_history: List[Dict] = None, context: Dict = None) -> str:
        """
        Process user message and generate response
        """
        try:
            # Prepare conversation history
            messages = [
                {"role": "system", "content": self.system_prompts.get(self.language, self.system_prompts['en'])}
            ]
            
            # Add session history if available
            if session_history:
                for item in session_history[-10:]:  # Last 10 exchanges
                    messages.append({"role": "user", "content": item.get('user_message', '')})
                    messages.append({"role": "assistant", "content": item.get('assistant_response', '')})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Add context if provided
            if context:
                context_str = self._format_context(context)
                if context_str:
                    messages[-1]["content"] += f"\n\nAdditional context: {context_str}"
            
            logger.info("Sending request to LLM", 
                       model=self.model,
                       language=self.language,
                       message_count=len(messages))
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=2048,
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            assistant_response = response.choices[0].message.content.strip()
            
            # Log token usage
            usage = response.get('usage', {})
            logger.info("LLM response generated",
                       tokens_used=usage.get('total_tokens', 0),
                       prompt_tokens=usage.get('prompt_tokens', 0),
                       completion_tokens=usage.get('completion_tokens', 0))
            
            return assistant_response
            
        except openai.error.RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return self._get_rate_limit_message()
        
        except openai.error.InvalidRequestError as e:
            logger.error("Invalid OpenAI request", error=str(e))
            return self._get_error_message()
        
        except Exception as e:
            logger.error("Error in LLM processing", error=str(e))
            return self._get_error_message()
    
    def _format_context(self, context: Dict) -> str:
        """Format context information for the prompt"""
        if not context:
            return ""
        
        formatted_parts = []
        
        # Format common context fields
        if context.get('filing_status'):
            formatted_parts.append(f"Filing status: {context['filing_status']}")
        
        if context.get('has_children'):
            formatted_parts.append(f"Has qualifying children: {context['has_children']}")
        
        if context.get('income_range'):
            formatted_parts.append(f"Income range: {context['income_range']}")
        
        if context.get('tax_year'):
            formatted_parts.append(f"Tax year: {context['tax_year']}")
        
        return "; ".join(formatted_parts)
    
    def _get_rate_limit_message(self) -> str:
        """Get rate limit exceeded message"""
        if self.language == 'es':
            return "Lo siento, el servicio está temporalmente ocupado. Por favor, inténtalo de nuevo en unos momentos."
        return "I'm sorry, the service is temporarily busy. Please try again in a few moments."
    
    def _get_error_message(self) -> str:
        """Get generic error message"""
        if self.language == 'es':
            return "Lo siento, ocurrió un error al procesar tu consulta. Por favor, inténtalo de nuevo o consulta a un profesional fiscal."
        return "I'm sorry, there was an error processing your question. Please try again or consult a tax professional."
    
    def validate_response(self, response: str) -> bool:
        """
        Validate that the response is appropriate for tax guidance
        """
        # Check for inappropriate content
        inappropriate_patterns = [
            r'social security number',
            r'ssn',
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'exact address',
            r'bank account',
            r'routing number'
        ]
        
        response_lower = response.lower()
        for pattern in inappropriate_patterns:
            if re.search(pattern, response_lower):
                logger.warning("Response contains inappropriate content", pattern=pattern)
                return False
        
        return True
