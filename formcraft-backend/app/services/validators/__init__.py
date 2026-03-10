from app.services.validators.registry import ValidatorRegistry
from app.services.validators.label_matcher import LabelMatcher
from app.services.validators.egypt import (
    EgyptNationalIdValidator,
    EgyptIbanValidator,
    EgyptPhoneValidator,
)
from app.services.validators.saudi import (
    SaudiNationalIdValidator,
    SaudiIbanValidator,
    SaudiVatValidator,
)
from app.services.validators.uae import UaeIbanValidator, UaeTrnValidator

# Initialize the global registry
validator_registry = ValidatorRegistry()
validator_registry.register(EgyptNationalIdValidator())
validator_registry.register(EgyptIbanValidator())
validator_registry.register(EgyptPhoneValidator())
validator_registry.register(SaudiNationalIdValidator())
validator_registry.register(SaudiIbanValidator())
validator_registry.register(SaudiVatValidator())
validator_registry.register(UaeIbanValidator())
validator_registry.register(UaeTrnValidator())

# Initialize the global label matcher
label_matcher = LabelMatcher()
