"""ReDoS-safe regex sandbox for Feature 048 custom validators.

Implements FR-9 from spec:
- 500-char max pattern length (also enforced at schema + DB)
- Static pre-check: reject nested unbounded quantifiers like (.+)+ or (.*)*
- 100ms compile-time probe against adversarial inputs
- 50ms runtime evaluation timeout with fail-open + VALIDATOR_TIMEOUT audit event

Why subprocess instead of threading: Python's `re` is implemented in C and does NOT
release the GIL inside a match, so we cannot interrupt it from another thread. The
sandbox runs the probe in a child process and kills it on timeout.
"""

from __future__ import annotations

import multiprocessing
import re
import signal
from dataclasses import dataclass


# Adversarial probe corpus — strings empirically known to trigger catastrophic
# backtracking against vulnerable patterns. Kept small so probe stays under 100ms total.
_REDOS_PROBE_INPUTS = (
    "",
    "a" * 30,
    "a" * 30 + "!",
    "1" * 30,
    "x" * 30 + "y",
    "ab" * 15,
    " " * 30,
)

# Compile probe budget (ms) — applies once at create/update time
_COMPILE_PROBE_TIMEOUT_MS = 100

# Runtime evaluation budget (ms) — applies on every form-fill validation
_RUNTIME_EVAL_TIMEOUT_MS = 50

# Nested unbounded quantifier patterns — flagged by static AST scan.
# Conservative on purpose: matches (...+)+ , (...*)*, (...+)*, (...*)+
_NESTED_QUANT_RE = re.compile(r"\([^()]*[+*]\)[+*]")


@dataclass(frozen=True)
class SandboxRejection:
    code: str   # e.g. "INVALID_REGEX_SYNTAX", "INVALID_REGEX_REDOS_RISK", "INVALID_REGEX_TIMEOUT"
    message: str


@dataclass(frozen=True)
class SandboxAccepted:
    compiled_pattern: re.Pattern[str]


SandboxResult = SandboxRejection | SandboxAccepted


def _probe_worker(pattern: str, queue: multiprocessing.Queue) -> None:
    """Run compile + adversarial probes inside a child process."""
    try:
        compiled = re.compile(pattern)
        for probe in _REDOS_PROBE_INPUTS:
            compiled.search(probe)
        queue.put(("ok", None))
    except re.error as exc:
        queue.put(("syntax_error", str(exc)))
    except Exception as exc:  # noqa: BLE001 — sandbox must never propagate
        queue.put(("internal_error", str(exc)))


def validate_pattern(pattern: str) -> SandboxResult:
    """Validate a regex pattern under the ReDoS sandbox.

    Returns either SandboxAccepted (with compiled pattern usable in-process) or
    SandboxRejection with a stable error code for the API to surface.
    """
    if not pattern:
        return SandboxRejection("INVALID_REGEX_SYNTAX", "Pattern is empty")

    if len(pattern) > 500:
        return SandboxRejection(
            "INVALID_REGEX_LENGTH",
            "Pattern length exceeds 500 characters",
        )

    # Static pre-check for known catastrophic-backtracking shapes
    if _NESTED_QUANT_RE.search(pattern):
        return SandboxRejection(
            "INVALID_REGEX_REDOS_RISK",
            "Pattern contains nested unbounded quantifiers like (...+)+ or (...*)*",
        )

    # Cheap syntactic check up-front (avoids spawning a process for obviously-broken regex)
    try:
        re.compile(pattern)
    except re.error as exc:
        return SandboxRejection("INVALID_REGEX_SYNTAX", str(exc))

    # Adversarial probe in a child process (the only safe way to kill a slow regex)
    ctx = multiprocessing.get_context("fork") if hasattr(multiprocessing, "get_start_method") else multiprocessing
    queue: multiprocessing.Queue = ctx.Queue()  # type: ignore[attr-defined]
    proc = ctx.Process(target=_probe_worker, args=(pattern, queue))  # type: ignore[attr-defined]
    proc.start()
    proc.join(_COMPILE_PROBE_TIMEOUT_MS / 1000.0)

    if proc.is_alive():
        proc.terminate()
        proc.join(0.5)
        if proc.is_alive():
            proc.kill()
        return SandboxRejection(
            "INVALID_REGEX_REDOS_RISK",
            f"Pattern exceeded {_COMPILE_PROBE_TIMEOUT_MS}ms evaluation budget on adversarial input (possible ReDoS)",
        )

    if not queue.empty():
        status_code, detail = queue.get_nowait()
        if status_code == "syntax_error":
            return SandboxRejection("INVALID_REGEX_SYNTAX", detail or "Invalid regex")
        if status_code == "internal_error":
            return SandboxRejection("INVALID_REGEX_INTERNAL", detail or "Sandbox internal error")

    # Probe passed — return a compiled-in-this-process pattern for reuse by the service
    return SandboxAccepted(compiled_pattern=re.compile(pattern))


class _AlarmTimeout(Exception):
    pass


def _alarm_handler(signum, frame):  # noqa: ARG001
    raise _AlarmTimeout()


def evaluate_runtime(compiled_pattern: re.Pattern[str], value: str) -> bool | None:
    """Evaluate a pre-validated pattern against a user-supplied value at form-fill time.

    Returns:
        True if the pattern matches the entire input (validator passes),
        False if it does not (validator fails),
        None if evaluation exceeded the 50ms runtime timeout (fail-open per FR-9).

    Callers are expected to log VALIDATOR_TIMEOUT to the audit trail when None is
    returned. This function does NOT log directly — keeping it pure-functional makes
    it trivial to unit test.

    Note: Uses signal.SIGALRM which is only available on Unix. On environments without
    SIGALRM the timeout is best-effort (we still evaluate but cannot interrupt).
    """
    if not hasattr(signal, "SIGALRM"):
        try:
            return bool(compiled_pattern.fullmatch(value))
        except Exception:  # noqa: BLE001
            return None

    old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
    # signal.setitimer takes seconds as float; converts to itimer real
    signal.setitimer(signal.ITIMER_REAL, _RUNTIME_EVAL_TIMEOUT_MS / 1000.0)
    try:
        return bool(compiled_pattern.fullmatch(value))
    except _AlarmTimeout:
        return None
    except Exception:  # noqa: BLE001
        return None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
