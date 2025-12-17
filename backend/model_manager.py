"""
Enhanced Model Manager for ProfileGPT
Handles multiple AI providers and smart model routing
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import openai
from openai import OpenAI
import anthropic
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"

class TaskType(Enum):
    SIMPLE_QA = "simple_qa"
    COMPLEX_REASONING = "complex_reasoning"
    SKILL_EXTRACTION = "skill_extraction"
    DOCUMENT_ANALYSIS = "document_analysis"

@dataclass
class ModelConfig:
    provider: ModelProvider
    model_name: str
    cost_per_input_token: float  # in USD per 1M tokens
    cost_per_output_token: float
    max_tokens: int
    temperature: float = 0.1

class EnhancedModelManager:
    """
    Intelligent model manager that routes queries to optimal models
    based on task complexity and cost optimization
    """

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.current_month_cost = 0.0
        self.monthly_budget = float(os.getenv("MONTHLY_AI_BUDGET", "50"))

        # Initialize clients
        self._initialize_clients()

        # Model configurations with costs (as of Dec 2024)
        self.model_configs = {
            # OpenAI Models
            "gpt-4o": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o",
                cost_per_input_token=2.50,
                cost_per_output_token=10.00,
                max_tokens=4096,
                temperature=0.1
            ),
            "gpt-4o-mini": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-4o-mini",
                cost_per_input_token=0.15,
                cost_per_output_token=0.60,
                max_tokens=4096,
                temperature=0.1
            ),
            "gpt-3.5-turbo": ModelConfig(
                provider=ModelProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                cost_per_input_token=0.50,
                cost_per_output_token=1.50,
                max_tokens=4096,
                temperature=0.1
            ),

            # Anthropic Models
            "claude-3-5-sonnet": ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-sonnet-20241022",
                cost_per_input_token=3.00,
                cost_per_output_token=15.00,
                max_tokens=4096,
                temperature=0.1
            ),
            "claude-3-5-haiku": ModelConfig(
                provider=ModelProvider.ANTHROPIC,
                model_name="claude-3-5-haiku-20241022",
                cost_per_input_token=0.25,
                cost_per_output_token=1.25,
                max_tokens=4096,
                temperature=0.1
            )
        }

        # Task to model routing
        self.task_routing = {
            TaskType.SIMPLE_QA: ["gpt-4o-mini", "claude-3-5-haiku", "gpt-3.5-turbo"],
            TaskType.COMPLEX_REASONING: ["gpt-4o", "claude-3-5-sonnet"],
            TaskType.SKILL_EXTRACTION: ["gpt-4o-mini", "claude-3-5-haiku"],
            TaskType.DOCUMENT_ANALYSIS: ["claude-3-5-sonnet", "gpt-4o"]
        }

        # Default model preference
        self.preferred_model = os.getenv("PREFERRED_AI_MODEL", "gpt-4o-mini")

    def _initialize_clients(self):
        """Initialize AI provider clients"""
        try:
            # OpenAI
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and not openai_key.startswith("sk-demo"):
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI client initialized")

            # Anthropic
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if anthropic_key:
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("Anthropic client initialized")

        except Exception as e:
            logger.warning(f"Error initializing AI clients: {e}")

    def select_optimal_model(self,
                           task_type: TaskType,
                           query_complexity: str = "medium",
                           budget_conscious: bool = True) -> str:
        """
        Select the optimal model based on task type and constraints
        """
        available_models = self.task_routing.get(task_type, ["gpt-4o-mini"])

        # Filter by available clients
        viable_models = []
        for model in available_models:
            config = self.model_configs[model]
            if config.provider == ModelProvider.OPENAI and self.openai_client:
                viable_models.append(model)
            elif config.provider == ModelProvider.ANTHROPIC and self.anthropic_client:
                viable_models.append(model)

        if not viable_models:
            return "gpt-4o-mini"  # Fallback

        # Budget-conscious selection
        if budget_conscious and self.current_month_cost > self.monthly_budget * 0.8:
            # Choose cheapest model when near budget limit
            cheapest = min(viable_models,
                         key=lambda x: self.model_configs[x].cost_per_input_token)
            return cheapest

        # Quality-first selection
        if query_complexity == "high":
            return viable_models[0]  # Best model for task
        else:
            return viable_models[-1] if len(viable_models) > 1 else viable_models[0]

    async def generate_response(self,
                              prompt: str,
                              context: str = "",
                              task_type: TaskType = TaskType.SIMPLE_QA,
                              max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate response using optimal model selection
        """
        model_name = self.select_optimal_model(task_type)
        config = self.model_configs[model_name]

        # Prepare messages
        messages = [
            {"role": "system", "content": self._get_system_prompt(task_type)},
        ]

        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})

        messages.append({"role": "user", "content": prompt})

        try:
            if config.provider == ModelProvider.OPENAI:
                response = await self._openai_completion(
                    model=config.model_name,
                    messages=messages,
                    max_tokens=min(max_tokens, config.max_tokens),
                    temperature=config.temperature
                )
            elif config.provider == ModelProvider.ANTHROPIC:
                response = await self._anthropic_completion(
                    model=config.model_name,
                    messages=messages,
                    max_tokens=min(max_tokens, config.max_tokens),
                    temperature=config.temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")

            # Track costs
            self._update_usage_costs(config, response.get("usage", {}))

            return {
                "response": response["content"],
                "model_used": model_name,
                "provider": config.provider.value,
                "usage": response.get("usage", {}),
                "estimated_cost": response.get("estimated_cost", 0)
            }

        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {e}")
            # Fallback to default model
            if model_name != "gpt-4o-mini":
                return await self.generate_response(
                    prompt, context, TaskType.SIMPLE_QA, max_tokens
                )
            raise e

    async def _openai_completion(self, model: str, messages: List[Dict],
                               max_tokens: int, temperature: float) -> Dict[str, Any]:
        """OpenAI API completion"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )

            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e

    async def _anthropic_completion(self, model: str, messages: List[Dict],
                                  max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Anthropic API completion"""
        try:
            # Convert messages format for Anthropic
            system_msg = None
            user_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append(msg)

            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_msg,
                messages=user_messages
            )

            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise e

    def _get_system_prompt(self, task_type: TaskType) -> str:
        """Get optimized system prompt for task type"""
        base_prompt = """You are an AI assistant for ProfileGPT, a professional portfolio system.
        Provide accurate, helpful responses based on the provided context."""

        task_specific = {
            TaskType.SIMPLE_QA: "Answer the question directly and concisely.",
            TaskType.COMPLEX_REASONING: "Think through this step-by-step and provide detailed analysis.",
            TaskType.SKILL_EXTRACTION: "Extract and categorize skills mentioned in the context.",
            TaskType.DOCUMENT_ANALYSIS: "Analyze the document content thoroughly and provide insights."
        }

        return f"{base_prompt}\n\nTask: {task_specific.get(task_type, '')}"

    def _update_usage_costs(self, config: ModelConfig, usage: Dict[str, Any]):
        """Track API costs"""
        if not usage:
            return

        input_cost = (usage.get("input_tokens", 0) / 1_000_000) * config.cost_per_input_token
        output_cost = (usage.get("output_tokens", 0) / 1_000_000) * config.cost_per_output_token
        total_cost = input_cost + output_cost

        self.current_month_cost += total_cost
        logger.info(f"API Cost: ${total_cost:.4f} (Monthly total: ${self.current_month_cost:.2f})")

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage and cost statistics"""
        return {
            "monthly_cost": self.current_month_cost,
            "monthly_budget": self.monthly_budget,
            "budget_remaining": max(0, self.monthly_budget - self.current_month_cost),
            "budget_used_percentage": (self.current_month_cost / self.monthly_budget) * 100,
            "available_providers": {
                "openai": bool(self.openai_client),
                "anthropic": bool(self.anthropic_client)
            }
        }

# Global instance
model_manager = EnhancedModelManager()