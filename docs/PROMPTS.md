# LLM Prompts Specification

## Overview

The system makes exactly **3 LLM calls**. All scoring, ranking, and anomaly detection are deterministic (no LLM).

---

## Call #1: Requirement Extraction

**Purpose:** Parse natural language / Excel input into structured procurement items.

**Model:** `gpt-4-turbo` or `claude-3-5-sonnet-20241022`

**Output schema:**
```json
{
  "items": [{
    "product_name": "string",
    "brand": "string|null",
    "model": "string|null",
    "quantity": "integer",
    "max_price": "number|null",
    "currency": "string",
    "max_lead_time_days": "integer|null",
    "moq_acceptable": "integer",
    "specs": {}
  }],
  "missing_info": ["array of missing fields"],
  "confidence": "high|medium|low"
}
```

**Fallback:** Returns empty items + `confidence: low` on any error.

---

## Call #2: Product Matching Judgment

**Purpose:** Determine if two listings are the same product (Layer 3 matching).

**Triggered only when:** Embedding similarity > 0.85 AND GTIN/Brand+Model match failed.

**Output schema:**
```json
{
  "is_same_product": true,
  "confidence": 0.95,
  "reasoning": "brief explanation"
}
```

**Cost control:** Only called for pairs with cosine similarity > 0.85.

---

## Call #3: Recommendation Explanation

**Purpose:** Generate human-readable markdown explaining the top 3 results.

**Constraints:**
- Maximum 300 words
- Must NOT make the purchasing decision
- Must cite specific numbers (prices, days, scores)
- Must flag anomalies if present

**Template variables:**
- `{user_requirement}` — original requirement string
- `{ranked_results_json}` — top 3 scored listings as JSON
- `{anomalies}` — detected anomaly flags

---

## What LLM Does NOT Do

- Calculate or influence scores
- Rank or re-rank listings
- Override anomaly flags
- Make the final purchase recommendation
