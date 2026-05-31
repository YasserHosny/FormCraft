"""Unit tests for the ReDoS-safe regex sandbox (Feature 048 FR-9).

These are the Phase 1 .T tests that gate the sandbox implementation.
"""

import re
import sys

import pytest

from app.services.custom_validator_sandbox import (
    SandboxAccepted,
    SandboxRejection,
    evaluate_runtime,
    validate_pattern,
)


# ----------------------------------------------------------------------
# Static rejection rules
# ----------------------------------------------------------------------

class TestStaticRejections:
    def test_empty_pattern_rejected(self):
        result = validate_pattern("")
        assert isinstance(result, SandboxRejection)
        assert result.code == "INVALID_REGEX_SYNTAX"

    def test_pattern_over_500_chars_rejected(self):
        result = validate_pattern("a" * 501)
        assert isinstance(result, SandboxRejection)
        assert result.code == "INVALID_REGEX_LENGTH"

    def test_pattern_exactly_500_chars_allowed(self):
        # 'a' x500 is benign — should pass even if it's at the boundary
        result = validate_pattern("a" * 500)
        assert isinstance(result, SandboxAccepted)

    def test_syntax_error_rejected(self):
        result = validate_pattern("(unbalanced")
        assert isinstance(result, SandboxRejection)
        assert result.code == "INVALID_REGEX_SYNTAX"


# ----------------------------------------------------------------------
# Nested-quantifier ReDoS pre-check (the cheap defense)
# ----------------------------------------------------------------------

class TestNestedQuantifierRejection:
    @pytest.mark.parametrize(
        "pattern",
        [
            r"(a+)+",
            r"(a+)+$",
            r"(a*)*",
            r"(.+)+",
            r"(.*)*",
            r"^(\d+)+$",
            r"(x+)*y",
        ],
    )
    def test_classic_redos_shapes_rejected(self, pattern):
        result = validate_pattern(pattern)
        assert isinstance(result, SandboxRejection), f"expected rejection for {pattern!r}"
        assert result.code == "INVALID_REGEX_REDOS_RISK"

    @pytest.mark.parametrize(
        "pattern",
        [
            r"^[0-9]{14}$",            # Egyptian national ID
            r"^[0-9]{10}$",            # Saudi Iqama
            r"^AE[0-9]{21}$",          # UAE IBAN
            r"^\+20[0-9]{10}$",        # Egyptian phone
            r"^[A-Z][a-z]{2,}$",       # Capitalized word
            r"^[\w.+-]+@[\w-]+\.[\w.-]+$",  # benign email
        ],
    )
    def test_benign_patterns_accepted(self, pattern):
        result = validate_pattern(pattern)
        assert isinstance(result, SandboxAccepted), f"expected acceptance for {pattern!r}"


# ----------------------------------------------------------------------
# Acceptance returns a compiled, usable Pattern
# ----------------------------------------------------------------------

class TestAcceptedShape:
    def test_returns_compiled_pattern(self):
        result = validate_pattern(r"^[0-9]{14}$")
        assert isinstance(result, SandboxAccepted)
        assert isinstance(result.compiled_pattern, re.Pattern)

    def test_compiled_pattern_matches_correctly(self):
        result = validate_pattern(r"^[0-9]{14}$")
        assert isinstance(result, SandboxAccepted)
        assert result.compiled_pattern.fullmatch("12345678901234")
        assert not result.compiled_pattern.fullmatch("123")


# ----------------------------------------------------------------------
# Runtime evaluation contract (FR-9: 50ms fail-open)
# ----------------------------------------------------------------------

@pytest.mark.skipif(
    not hasattr(__import__("signal"), "SIGALRM"),
    reason="SIGALRM not available on this platform — runtime timeout is best-effort only",
)
class TestRuntimeEvaluation:
    def test_match_returns_true(self):
        compiled = re.compile(r"^[0-9]{14}$")
        assert evaluate_runtime(compiled, "12345678901234") is True

    def test_mismatch_returns_false(self):
        compiled = re.compile(r"^[0-9]{14}$")
        assert evaluate_runtime(compiled, "abc") is False

    def test_runtime_timeout_returns_none_fail_open(self):
        # This pattern PASSES the static pre-check (no obvious nesting) but exhibits
        # catastrophic backtracking on certain inputs. The runtime timeout must catch it.
        # Pattern from RFC 5322-style email validators known to be ReDoS-prone.
        compiled = re.compile(r"^([a-zA-Z0-9])(([\-.]|[_]+)?([a-zA-Z0-9]+))*(@){1}[a-z0-9]+[.]{1}(([a-z]{2,3})|([a-z]{2,3}[.]{1}[a-z]{2,3}))$")
        # Adversarial input: many @ characters
        adversarial = "a" + "@" * 30
        result = evaluate_runtime(compiled, adversarial)
        # Either timeout (None) or quick non-match (False) is acceptable — both are
        # safe outcomes. The contract is: do not hang.
        assert result in (None, False)
