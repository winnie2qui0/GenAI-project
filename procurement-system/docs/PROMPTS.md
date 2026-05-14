# LLM Prompts（MVP）

三個呼叫定義於 `backend/app/services/llm_service.py`：

1. **需求抽取**：`EXTRACT_PROMPT` → `extract_requirements()`
2. **同品裁決**：`MATCHING_PROMPT` → `judge_same_product()`
3. **結果說明**：`EXPLANATION_PROMPT` → `explain_recommendation()`

若未設定 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`，系統會進入**離線示範模式**（規則式抽取/裁決/摘要），以利本機 demo。
