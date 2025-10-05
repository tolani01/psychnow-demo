"""
Base Screener Class
Foundation for all mental health screening instruments
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ScreenerQuestion(BaseModel):
    """Individual question in a screener"""
    number: int
    text: str
    options: List[Dict[str, Any]]  # [{value: 0, label: "Not at all"}, ...]


class ScreenerResult(BaseModel):
    """Result of a completed screener"""
    name: str
    score: int
    max_score: int
    interpretation: str
    severity: Optional[str] = None
    clinical_significance: Optional[str] = None
    subscales: Optional[Dict[str, Any]] = None
    item_scores: Optional[List[int]] = None


class BaseScreener(ABC):
    """
    Abstract base class for all screeners
    
    Each screener must implement:
    - name: str
    - questions: List[ScreenerQuestion]
    - score(responses: List[int]) -> ScreenerResult
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Screener name (e.g., 'PHQ-9')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what this screener measures"""
        pass
    
    @property
    @abstractmethod
    def questions(self) -> List[ScreenerQuestion]:
        """List of screening questions"""
        pass
    
    @abstractmethod
    def score(self, responses: List[int]) -> ScreenerResult:
        """
        Score the screener based on responses
        
        Args:
            responses: List of integer responses (length must match questions)
            
        Returns:
            ScreenerResult with score, interpretation, and severity
        """
        pass
    
    def validate_responses(self, responses: List[int]) -> bool:
        """
        Validate that responses are correct length and within valid ranges
        
        Args:
            responses: List of responses to validate
            
        Returns:
            True if valid, raises ValueError if invalid
        """
        if len(responses) != len(self.questions):
            raise ValueError(
                f"{self.name} requires {len(self.questions)} responses, got {len(responses)}"
            )
        
        for i, response in enumerate(responses):
            valid_values = [opt['value'] for opt in self.questions[i].options]
            if response not in valid_values:
                raise ValueError(
                    f"Invalid response {response} for question {i+1}. "
                    f"Valid values: {valid_values}"
                )
        
        return True
    
    def get_question_text_for_llm(self, question_num: int) -> str:
        """
        Get formatted question text for LLM to present to patient
        
        Args:
            question_num: Question number (1-indexed)
            
        Returns:
            Formatted question with options
        """
        if question_num < 1 or question_num > len(self.questions):
            raise ValueError(f"Question number must be between 1 and {len(self.questions)}")
        
        question = self.questions[question_num - 1]
        
        # Format question with options
        text = f"{self.name} Question #{question_num}:\n\n{question.text}\n\n"
        for option in question.options:
            text += f"{option['value']}: {option['label']}\n"
        
        text += f"\nPlease enter your choice (0-{len(question.options)-1})."
        
        return text

