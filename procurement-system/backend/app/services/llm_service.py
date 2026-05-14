"""LLM integration: extraction, matching judgment, recommendation copy."""

from __future__ import annotations

import json
import re
from typing import Any

from app.config import get_settings
from app.schemas.llm import ExtractedRequirements, MatchingJudgment

EXTRACT_PROMPT = """You are a procurement requirements parser. Extract structured information from the user's procurement request.

Output ONLY valid JSON matching this schema:
{{
  "items": [
    {{
      "product_name": "string (required)",
      "brand": "string or null",
      "model": "string or null",
      "quantity": "integer (required, default 1)",
      "max_price": "number or null (per unit)",
      "currency": "string (default USD)",
      "max_lead_time_days": "integer or null",
      "moq_acceptable": "integer (default 1)",
      "specs": {{}}
    }}
  ],
  "missing_info": ["array of fields user didn't specify"],
  "confidence": "high | medium | low"
}}

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
  "is_same_product": true or false,
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
    def __init__(self) -> None:
        self.settings = get_settings()

    def _mock_extract(self, user_input: str) -> dict[str, Any]:
        qty = 1
        m = re.search(r"(\d+)\s*(pcs|units|ea|each|cartridges|toner|boxes)?", user_input, re.I)
        if m and m.group(1).isdigit():
            qty = int(m.group(1))
        brand = None
        for b in ("HP", "Canon", "Epson", "Dell"):
            if b.lower() in user_input.lower():
                brand = b
                break
        model_m = re.search(r"\b([A-Z]{1,3}\d{2,6}[A-Z]?)\b", user_input)
        model = model_m.group(1) if model_m else None
        return {
            "items": [
                {
                    "product_name": user_input.strip()[:200] or "Office supply item",
                    "brand": brand,
                    "model": model,
                    "quantity": qty,
                    "max_price": None,
                    "currency": "USD",
                    "max_lead_time_days": None,
                    "moq_acceptable": 1,
                    "specs": {},
                }
            ],
            "missing_info": ["max_price", "max_lead_time_days"],
            "confidence": "low",
        }

    async def extract_requirements(self, user_input: str) -> dict[str, Any]:
        if not self.settings.openai_api_key and not self.settings.anthropic_api_key:
            return self._mock_extract(user_input)

        content = EXTRACT_PROMPT.format(user_input=user_input)
        raw = await self._complete_json(content)
        data = json.loads(raw)
        ExtractedRequirements.model_validate(data)
        return data

    async def judge_same_product(self, a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
        if not self.settings.openai_api_key and not self.settings.anthropic_api_key:
            same = a.get("title") == b.get("title") and a.get("source_id") == b.get("source_id")
            return {"is_same_product": same, "confidence": 1.0 if same else 0.0, "reasoning": "mock"}

        prompt = MATCHING_PROMPT.format(
            title_a=a.get("title", ""),
            brand_a=a.get("brand"),
            model_a=a.get("model"),
            specs_a=json.dumps(a.get("specs") or {}),
            title_b=b.get("title", ""),
            brand_b=b.get("brand"),
            model_b=b.get("model"),
            specs_b=json.dumps(b.get("specs") or {}),
        )
        raw = await self._complete_json(prompt)
        data = json.loads(raw)
        MatchingJudgment.model_validate(data)
        return data

    async def explain_recommendation(
        self,
        user_requirement: str,
        ranked_results: list[dict[str, Any]],
        anomalies_summary: list[dict[str, Any]],
    ) -> str:
        if not self.settings.openai_api_key and not self.settings.anthropic_api_key:
            lines = ["### 系統摘要（離線示範模式）", ""]
            for row in ranked_results[:3]:
                lines.append(
                    f"- 第 {row.get('rank')} 名：{row.get('source')} 價格 {row.get('price')} {row.get('currency')}，"
                    f"總分 {row.get('final_score')}"
                )
            if anomalies_summary:
                lines.append("")
                lines.append("**注意事項**：偵測到異常旗標，請於採購前人工覆核。")
            return "\n".join(lines)

        prompt = EXPLANATION_PROMPT.format(
            user_requirement=user_requirement,
            ranked_results_json=json.dumps(ranked_results, ensure_ascii=False, indent=2),
            anomalies=json.dumps(anomalies_summary, ensure_ascii=False, indent=2),
        )
        return await self._complete_text(prompt)

    async def _complete_json(self, user_prompt: str) -> str:
        text = await self._complete_raw(user_prompt, json_mode=True)
        return text

    async def _complete_text(self, user_prompt: str) -> str:
        return await self._complete_raw(user_prompt, json_mode=False)

    async def _complete_raw(self, user_prompt: str, *, json_mode: bool) -> str:
        provider = self.settings.llm_provider.lower()
        model = self.settings.llm_model

        if provider == "anthropic" and self.settings.anthropic_api_key:
            import anthropic

            client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)
            msg = await client.messages.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": user_prompt}],
            )
            block = msg.content[0]
            if block.type != "text":
                raise RuntimeError("Unexpected Anthropic response block")
            text = block.text.strip()
            if json_mode:
                start = text.find("{")
                end = text.rfind("}")
                if start >= 0 and end >= start:
                    text = text[start : end + 1]
            return text

        from openai import AsyncOpenAI

        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if json_mode and model.startswith("gpt"):
            kwargs["response_format"] = {"type": "json_object"}
        resp = await client.chat.completions.create(**kwargs)
        return (resp.choices[0].message.content or "").strip()
