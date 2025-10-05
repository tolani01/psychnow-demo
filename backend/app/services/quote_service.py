"""
Quote Extraction Service
Extracts and formats key patient statements for report
"""
from typing import List, Dict, Any
from app.services.llm_service import llm_service


class QuoteExtractionService:
    """Service for extracting and cleaning patient quotes"""
    
    async def extract_key_quotes(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract key patient statements from conversation
        
        Args:
            conversation_history: Full conversation messages
            
        Returns:
            List of key quotes organized by topic (filtered for quality)
        """
        # Filter to just patient messages (minimum 15 characters for meaningful content)
        patient_messages = [
            msg for msg in conversation_history 
            if msg.get("role") == "user" and len(msg.get("content", "").strip()) >= 15
        ]
        
        if not patient_messages:
            return []
        
        # Build extraction prompt
        conversation_text = "\n".join([
            f"Patient: {msg['content']}" 
            for msg in patient_messages
        ])
        
        extraction_prompt = f"""
You are extracting key patient statements from an intake conversation.

**CONVERSATION:**
{conversation_text}

**TASK:**
Extract 5-8 of the most clinically relevant patient statements and organize by topic.

Topics to look for:
- Chief Complaint (why they're seeking help)
- Symptom Description (how they describe their experience)
- Sleep/Appetite (if mentioned)
- Functioning (impact on work/relationships)
- Suicidal Thoughts (if mentioned)
- Treatment History (if mentioned)
- Support System (if mentioned)

**RULES:**
1. Use patient's EXACT words (copy directly from conversation)
2. Fix obvious typos/spelling ONLY if present (set lightly_edited: true)
3. Do NOT add interpretations or clinical language
4. Do NOT combine multiple messages
5. Do NOT include short fragments (minimum 10 words per quote)
6. Do NOT include single-word or very brief responses like "yes", "no", "getting worse"
7. Only include complete, meaningful statements

**FORMAT (JSON):**
{{
  "quotes": [
    {{
      "topic": "Chief Complaint",
      "statement": "exact patient words here",
      "lightly_edited": true/false
    }}
  ]
}}

Return ONLY the JSON, no additional text.
"""
        
        # Get structured response
        result = await llm_service.get_structured_completion(
            messages=[{"role": "user", "content": extraction_prompt}],
            response_format={},
            temperature=0.2  # Low temperature for accuracy
        )
        
        return result.get("quotes", [])


# Global quote service instance
quote_service = QuoteExtractionService()

