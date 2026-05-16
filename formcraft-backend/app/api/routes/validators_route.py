from fastapi import APIRouter

from app.services.validators.registry import ValidatorRegistry
from app.services.validators.egypt import EgyptValidator
from app.services.validators.saudi import SaudiValidator
from app.services.validators.ufae import UAEValidator
from app.schemas.submission import ValidatorCountryResponse, ValidatorFieldResponse

router = APIRouter(prefix="/validators", tags=["Validators"])

_registry = ValidatorRegistry()
_registry.register(EgyptValidator())
_registry.register(SaudiValidator())
_registry.register(UAEValidator())


@router.get("/{country}", response_model=ValidatorCountryResponse)
async def get_validators(country: str):
    """Return all registered validator patterns for a given country."""
    validators = _registry.list_all_for_country(country)
    fields = [
        ValidatorFieldResponse(
            field_type=vt,
            pattern=validators[vt].pattern if hasattr(validators[vt], 'pattern') else None,
            message_ar=validators[vt].message_ar if hasattr(validators[vt], 'message_ar') else None,
            message_en=validators[vt].message_en if hasattr(validators[vt], 'message_en') else None,
        )
        for vt in validators
    ]
    return ValidatorCountryResponse(country=country, validators=fields)