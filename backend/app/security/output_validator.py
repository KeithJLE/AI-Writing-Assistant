"""Output validation module for LLM responses.

Security implementation based on OWASP LLM Prompt Injection Prevention Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

Validates LLM outputs to detect potential security issues such as prompt leakage, API key exposure, and instruction injection in responses.
"""

import re


class OutputValidator:
    """Validator for LLM outputs to detect security issues."""

    def __init__(self):
        """Initialize the output validator with detection patterns."""
        self.suspicious_patterns = [
            r"SYSTEM\s*[:]\s*You\s+are",  # System prompt leakage
            r"API[_\s]KEY[:=]\s*\w+",  # API key exposure
            r"instructions?[:]\s*\d+\.",  # Numbered instructions
        ]

    def validate_output(self, output: str) -> bool:
        """
        Validate LLM output for security issues.

        Args:
            output: The LLM output to validate

        Returns:
            True if valid, False if suspicious
        """
        return not any(
            re.search(pattern, output, re.IGNORECASE)
            for pattern in self.suspicious_patterns
        )

    def filter_response(self, response: str) -> str:
        """
        Filter LLM response to remove potential security issues.

        Args:
            response: The LLM response to filter

        Returns:
            Filtered response
        """
        if not self.validate_output(response) or len(response) > 5000:
            return "I cannot provide that information for security reasons."
        return response
