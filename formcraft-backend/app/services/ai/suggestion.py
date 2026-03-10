"""AI suggestion orchestrator: cache → deterministic → LLM → validate → respond."""

import logging

from pydantic import ValidationError

from app.models.enums import Direction, ElementType
from app.schemas.ai import (
    FormattingSchema,
    SuggestionRequest,
    SuggestionResponse,
    ValidationSchema,
)
from app.services.ai.cache import get_cache_key, suggestion_cache
from app.services.ai.provider import LLMProvider

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = SuggestionResponse(
    control_type=ElementType.TEXT,
    confidence=0.0,
    validation=ValidationSchema(),
    formatting=FormattingSchema(),
    direction=Direction.AUTO,
    source="fallback",
)


async def get_suggestion(
    request: SuggestionRequest,
    llm_provider: LLMProvider,
    label_matcher=None,
    validator_registry=None,
) -> SuggestionResponse:
    """Main suggestion pipeline."""

    # 1. Check cache
    cache_key = get_cache_key(request.label, request.language.value, request.country.value)
    cached = suggestion_cache.get(cache_key)
    if cached is not None:
        return cached

    # 2. Check deterministic validators (if available)
    if label_matcher and validator_registry:
        match = label_matcher.match(request.label, request.country.value)
        if match:
            country, field_type = match
            validator = validator_registry.get(country, field_type)
            if validator:
                response = SuggestionResponse(
                    control_type=ElementType.TEXT,  # Will be overridden by field_type mapping
                    confidence=1.0,
                    validation=ValidationSchema(
                        required=True,
                        regex=validator.regex_pattern,
                    ),
                    direction=Direction.RTL if request.language.value == "ar" else Direction.LTR,
                    source="deterministic",
                )
                suggestion_cache[cache_key] = response
                return response

    # 3. Call LLM
    try:
        raw = await llm_provider.classify_field(request)
    except Exception as e:
        logger.warning("LLM call failed: %s", e)
        return FALLBACK_RESPONSE

    # 4. Validate response with Pydantic
    try:
        response = SuggestionResponse(
            control_type=raw.get("controlType", "text"),
            confidence=raw.get("confidence", 0.5),
            validation=ValidationSchema(**raw.get("validation", {})),
            formatting=FormattingSchema(**raw.get("formatting", {})),
            direction=raw.get("direction", "auto"),
            source="llm",
        )
    except (ValidationError, TypeError, KeyError) as e:
        logger.warning("LLM response validation failed: %s", e)
        return SuggestionResponse(
            control_type=ElementType.TEXT,
            confidence=0.5,
            source="fallback",
        )

    # 5. Cache and return
    suggestion_cache[cache_key] = response
    return response
