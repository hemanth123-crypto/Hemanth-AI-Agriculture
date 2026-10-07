"""
app/guardrails/prompt_injection.py
Defense against adversarial prompt injection, system prompt extraction,
credential exfiltration, and jailbreak attempts.
Conforms to Section 14 of project specification.
"""

import re
from typing import Tuple, Optional

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior|system)\s+rules?",
    r"reveal\s+(your\s+)?(system\s+prompt|instructions?|api\s*key|secrets?)",
    r"show\s+(me\s+)?(your\s+)?(system\s+prompt|api\s*key|environment|env\b)",
    r"what\s+is\s+your\s+(api\s*key|system\s*prompt)",
    r"you\s+are\s+now\s+(an\s+unrestricted|a\s+different|in\s+dan\s+mode|jailbroken)",
    r"bypass\s+(all\s+)?(safety|guardrails?|filters?)",
    r"override\s+system\s+(prompt|settings?)",
    r"print\s+env(ironment)?(\s+variables)?",
    r"execute\s+command",
    r"<system>",
    r"\[system\s+instruction\]",
    r"drop\s+table",
    r"union\s+select"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

class PromptInjectionGuardrail:
    @staticmethod
    def inspect(query: str) -> Tuple[bool, Optional[str]]:
        """
        Scans user text for malicious adversarial directives.
        Returns: (is_safe, violation_reason)
        """
        if not query:
            return True, None

        normalized = " ".join(query.strip().split())

        for pattern in COMPILED_PATTERNS:
            match = pattern.search(normalized)
            if match:
                detected_fragment = match.group(0)
                reason = f"Security Violation: Adversarial prompt injection detected ('{detected_fragment}'). Directive rejected."
                return False, reason

        return True, None

prompt_injection_guardrail = PromptInjectionGuardrail()
