import json
import logging
from typing import Any

from app.config import get_settings
from app.schemas.llm import ExtractionResult, MatchingJudgment

logger = logging.getLogger(__name__)
settings = get_settings()

EXTRACT_PROMPT = """You are a procurement requirements parser. Extract structured information from the user's procurement request.

Output ONLY valid JSON matching this schema:
{
  "items": [
    {
      "product_name": "string (required)",
      "brand": "string or null",
      "model": "string or null",
      "quantity": "integer (required, default 1)",
      "max_price": "number or null (per unit)",
      "currency": "string (default USD)",
      "max_lead_time_days": "integer or null",
      "moq_acceptable": "integer (default 1)",
      "specs": {"additional_specs": "as JSON object"}
    }
  ],
  "missing_info": ["array of fields user didn't specify"],
  "confidence": "high | medium | low"
}

User input: {user_input}

JSON output:"""

MATCHING_PROMPT = """You are a product matching expert. Determine if two product listings refer to the SAME product.

Listing A:
- Title: {title_a}
- Brand: {brand_a}
- Model: {model_a}
- Specs: {specs_a}

Listing B:
- Title: {title_b}
- Brand: {brand_b}
- Model: {model_b}
- Specs: {specs_b}

Output ONLY valid JSON:
{{
  "is_same_product": true | false,
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation (max 50 words)"
}}

JSON output:"""

EXPLANATION_PROMPT = """You are a procurement advisor. Generate a recommendation explanation for the buyer.

User requirement: {user_requirement}

Top 3 ranked products:
{ranked_results_json}

Anomaly flags: {anomalies}

Generate a clear, professional recommendation explaining:
1. Why #1 is recommended (specific reasons based on scores)
2. Trade-offs of #2 and #3 (when they might be better)
3. Risk alerts (any anomalies the buyer should know)
4. Action items (what to verify before purchase)

Format as markdown. Maximum 300 words.
Be specific with numbers (prices, days, ratings).
Do NOT make the decision — present information for the buyer to decide."""


class LLMService:
    def __init__(self):
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai(self):
        if self._openai_client is None:
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._openai_client

    def _get_anthropic(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    async def _call_llm(self, prompt: str) -> str:
        if settings.llm_provider == "anthropic":
            client = self._get_anthropic()
            message = await client.messages.create(
                model=settings.llm_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        else:
            client = self._get_openai()
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content

    async def extract_requirements(self, user_input: str) -> ExtractionResult:
        prompt = EXTRACT_PROMPT.format(user_input=user_input)
        try:
            raw = await self._call_llm(prompt)
            data = json.loads(raw)
            return ExtractionResult(**data)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return ExtractionResult(
                items=[],
                missing_info=["Failed to parse input"],
                confidence="low",
            )

    async def judge_same_product(self, listing_a: dict, listing_b: dict) -> MatchingJudgment:
        prompt = MATCHING_PROMPT.format(
            title_a=listing_a.get("title", ""),
            brand_a=listing_a.get("brand", "N/A"),
            model_a=listing_a.get("model", "N/A"),
            specs_a=json.dumps(listing_a.get("specs", {})),
            title_b=listing_b.get("title", ""),
            brand_b=listing_b.get("brand", "N/A"),
            model_b=listing_b.get("model", "N/A"),
            specs_b=json.dumps(listing_b.get("specs", {})),
        )
        try:
            raw = await self._call_llm(prompt)
            data = json.loads(raw)
            return MatchingJudgment(**data)
        except Exception as e:
            logger.error(f"LLM matching failed: {e}")
            return MatchingJudgment(is_same_product=False, confidence=0.0, reasoning="LLM error")

    async def generate_explanation(
        self,
        user_requirement: str,
        ranked_results: list[dict[str, Any]],
        anomalies: list[dict[str, Any]],
    ) -> str:
        top3 = ranked_results[:3]
        prompt = EXPLANATION_PROMPT.format(
            user_requirement=user_requirement,
            ranked_results_json=json.dumps(top3, indent=2, default=str),
            anomalies=json.dumps(anomalies, indent=2, default=str),
        )
        try:
            if settings.llm_provider == "anthropic":
                client = self._get_anthropic()
                message = await client.messages.create(
                    model=settings.llm_model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text
            else:
                client = self._get_openai()
                response = await client.chat.completions.create(
                    model=settings.llm_model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM explanation failed: {e}")
            return "Unable to generate explanation. Please review the scores above."
