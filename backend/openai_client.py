"""
Simplified OpenAI Client for ProfileGPT
Cost-optimized implementation with local embeddings + OpenAI chat
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from openai import OpenAI
import tiktoken

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Simple OpenAI client for ProfileGPT with cost tracking"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        self.monthly_budget = float(os.getenv("MONTHLY_AI_BUDGET", "15.0"))
        self.current_cost = 0.0

        # Cost per 1M tokens (as of Dec 2024)
        self.costs = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
        }

        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client if API key is available"""
        if self.api_key and not self.api_key.startswith("sk-demo"):
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("OpenAI API key not found or is demo key")

    def is_available(self) -> bool:
        """Check if OpenAI client is available"""
        return self.client is not None

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except:
            # Fallback estimation: ~4 characters per token
            return len(text) // 4

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""
        if self.model not in self.costs:
            return 0.0

        costs = self.costs[self.model]
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        return input_cost + output_cost

    async def chat_completion(self,
                            messages: List[Dict[str, str]],
                            max_tokens: int = 1000,
                            temperature: float = 0.1) -> Dict[str, Any]:
        """
        Get chat completion from OpenAI with cost tracking
        """
        if not self.is_available():
            raise ValueError("OpenAI client not available. Check API key.")

        # Check budget
        if self.current_cost >= self.monthly_budget:
            raise ValueError(f"Monthly budget of ${self.monthly_budget} exceeded")

        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )

            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = self.calculate_cost(input_tokens, output_tokens)

            # Track cost
            self.current_cost += cost

            logger.info(f"OpenAI API call: {input_tokens}+{output_tokens} tokens, ${cost:.4f}")

            return {
                "response": response.choices[0].message.content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "cost": cost,
                "model": self.model
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e

    def get_system_prompt(self, mode: str = "detailed") -> str:
        """Get system prompt based on response mode"""
        base_prompt = """You are ProfileGPT, an AI assistant representing a professional's portfolio.
        Provide accurate, helpful responses based ONLY on the provided context about this person's background, skills, and experience.

        IMPORTANT RULES:
        1. Only answer based on the provided context
        2. If information isn't in the context, say "I don't have that information in my knowledge base"
        3. Always include relevant citations from the source documents
        4. Be professional and engaging
        5. Highlight specific achievements and quantifiable results when available
        """

        mode_instructions = {
            "short": "Provide concise, direct answers in 1-2 sentences.",
            "detailed": "Provide comprehensive answers with examples and context.",
            "star": "Structure your response using the STAR method (Situation, Task, Action, Result) when discussing experiences."
        }

        return f"{base_prompt}\n\nResponse style: {mode_instructions.get(mode, mode_instructions['detailed'])}"

    async def generate_profile_response(self,
                                      question: str,
                                      context: str,
                                      mode: str = "detailed") -> Dict[str, Any]:
        """
        Generate a response for ProfileGPT using OpenAI
        """
        system_prompt = self.get_system_prompt(mode)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context from portfolio:\n{context}\n\nQuestion: {question}"}
        ]

        # Adjust max_tokens based on mode
        max_tokens = {
            "short": 200,
            "detailed": 800,
            "star": 600
        }.get(mode, 500)

        try:
            result = await self.chat_completion(messages, max_tokens=max_tokens)

            return {
                "answer": result["response"],
                "usage": result["usage"],
                "cost": result["cost"],
                "model_used": result["model"],
                "success": True
            }

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return {
                "answer": f"I'm sorry, I encountered an error processing your question: {str(e)}",
                "error": str(e),
                "success": False
            }

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "monthly_cost": self.current_cost,
            "monthly_budget": self.monthly_budget,
            "budget_remaining": max(0, self.monthly_budget - self.current_cost),
            "budget_used_percent": (self.current_cost / self.monthly_budget) * 100,
            "model": self.model,
            "api_available": self.is_available()
        }

# Global instance
openai_client = OpenAIClient()

# Fallback function for when OpenAI is not available
def get_fallback_response(question: str, context: str, mode: str = "detailed") -> str:
    """Simple fallback when OpenAI API is not available"""
    if not context:
        return "I don't have enough information in my knowledge base to answer that question. Please upload some documents about yourself first."

    # Simple keyword matching fallback
    question_lower = question.lower()

    if any(word in question_lower for word in ["skill", "technology", "tool", "language", "framework"]):
        return f"Based on my knowledge base, here are the relevant skills I found:\n\n{context[:500]}...\n\nFor more detailed information about specific skills, please ask about them individually."

    elif any(word in question_lower for word in ["experience", "work", "job", "role", "position"]):
        return f"Here's information about the professional experience I have on file:\n\n{context[:500]}...\n\nWould you like to know more about any specific role or project?"

    elif any(word in question_lower for word in ["project", "build", "created", "developed"]):
        return f"Based on the available information, here are relevant projects and achievements:\n\n{context[:500]}...\n\nFeel free to ask about specific projects for more details."

    else:
        return f"Based on the available information:\n\n{context[:400]}...\n\n*Note: For more detailed and accurate responses, please configure your OpenAI API key.*"