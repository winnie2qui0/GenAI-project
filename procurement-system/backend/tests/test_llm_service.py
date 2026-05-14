import pytest

from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_extract_offline_mock() -> None:
    svc = LLMService()
    out = await svc.extract_requirements("500 HP toner CF410A")
    assert "items" in out
    assert len(out["items"]) >= 1


@pytest.mark.asyncio
async def test_judge_offline_mock() -> None:
    svc = LLMService()
    a = {"title": "x", "brand": "b", "model": "m"}
    b = {"title": "x", "brand": "b", "model": "m"}
    out = await svc.judge_same_product(a, b)
    assert "is_same_product" in out
