"""
LLM Service
Wrapper for OpenAI API with streaming support
"""
from typing import AsyncIterator, List, Dict, Any
import openai
from openai import AsyncOpenAI
import json

from app.core.config import settings


class LLMService:
    """Service for interacting with OpenAI LLM"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream chat completion responses
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0-2)
            
        Yields:
            Chunks of response text
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    # Handle Unicode encoding issues
                    content = chunk.choices[0].delta.content
                    try:
                        # Ensure content is properly encoded
                        if isinstance(content, bytes):
                            content = content.decode('utf-8', errors='replace')
                        elif not isinstance(content, str):
                            content = str(content)
                        
                        # Clean any problematic characters
                        content = content.encode('utf-8', errors='replace').decode('utf-8')
                        yield content
                    except UnicodeError:
                        # Fallback for severe Unicode issues
                        yield " "
        
        except openai.APIError as e:
            yield f"⚠️ API Error: {str(e)}"
        except Exception as e:
            yield f"⚠️ Error: {str(e)}"
    
    async def get_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """
        Get a complete (non-streaming) chat completion
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            
        Returns:
            Complete response text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        
        except openai.APIError as e:
            return f"⚠️ API Error: {str(e)}"
        except Exception as e:
            return f"⚠️ Error: {str(e)}"
    
    async def get_structured_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Get a structured JSON response
        
        Args:
            messages: List of conversation messages
            response_format: JSON schema for response
            temperature: Sampling temperature (lower for structured output)
            
        Returns:
            Parsed JSON response
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        
        except openai.APIError as e:
            return {"error": f"API Error: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error: {str(e)}"}


# Global LLM service instance
llm_service = LLMService()

