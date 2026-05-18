import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_service import LLMService


@pytest.fixture
def service():
    return LLMService()


@pytest.mark.asyncio
async def test_extract_requirements_returns_extraction_result(service):
    mock_response = '{"items": [{"product_name": "HP Toner CF410A", "brand": "HP", "model": "CF410A", "quantity": 500, "max_price": 40, "currency": "USD", "max_lead_time_days": 2, "moq_acceptable": 1}], "missing_info": [], "confidence": "high"}'

    with patch.object(service, "_call_llm", new=AsyncMock(return_value=mock_response)):
        result = await service.extract_requirements("I need 500 HP toner CF410A at $40 max, 2 day delivery")

    assert len(result.items) == 1
    assert result.items[0].product_name == "HP Toner CF410A"
    assert result.items[0].brand == "HP"
    assert result.items[0].quantity == 500
    assert result.confidence == "high"


@pytest.mark.asyncio
async def test_extract_requirements_handles_llm_error(service):
    with patch.object(service, "_call_llm", new=AsyncMock(side_effect=Exception("LLM down"))):
        result = await service.extract_requirements("some input")

    assert result.items == []
    assert result.confidence == "low"
    assert "Failed to parse input" in result.missing_info


@pytest.mark.asyncio
async def test_judge_same_product_returns_judgment(service):
    mock_response = '{"is_same_product": true, "confidence": 0.95, "reasoning": "Same brand, model, and specs"}'

    with patch.object(service, "_call_llm", new=AsyncMock(return_value=mock_response)):
        result = await service.judge_same_product(
            {"title": "HP CF410A", "brand": "HP", "model": "CF410A"},
            {"title": "HP CF410A Toner", "brand": "HP", "model": "CF410A"},
        )

    assert result.is_same_product is True
    assert result.confidence == 0.95


@pytest.mark.asyncio
async def test_judge_different_product(service):
    mock_response = '{"is_same_product": false, "confidence": 0.98, "reasoning": "Different brand and model"}'

    with patch.object(service, "_call_llm", new=AsyncMock(return_value=mock_response)):
        result = await service.judge_same_product(
            {"title": "HP toner", "brand": "HP", "model": "CF410A"},
            {"title": "Canon ink", "brand": "Canon", "model": "PG-245"},
        )

    assert result.is_same_product is False
