"""Prompt injection prevention module.

Security implementation based on OWASP LLM Prompt Injection Prevention Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

Implements detection patterns and validation strategies for preventing prompt injection attacks in LLM applications.
"""

import re


class PromptInjectionFilter:
    """Filter for detecting and preventing prompt injection attacks."""

    def __init__(self):
        """Initialize the prompt injection filter with detection patterns."""
        self.dangerous_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions?",
            r"you\s+are\s+now\s+(in\s+)?developer\s+mode",
            r"system\s+override",
            r"reveal\s+prompt",
        ]

        # Fuzzy matching for typoglycemia attacks
        self.fuzzy_patterns = [
            "ignore",
            "bypass",
            "override",
            "reveal",
            "delete",
            "system",
        ]

        # HTML/Markdown injection patterns
        self.html_injection_patterns = [
            r"<script",
            r"<img[^>]+src=",
            r"<iframe",
            r"javascript:",
            r"onerror=",
            r"onclick=",
        ]

    def detect_injection(self, text: str) -> bool:
        """
        Detect potential prompt injection attacks in text.

        Args:
            text: The input text to check

        Returns:
            True if injection detected, False otherwise
        """
        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.dangerous_patterns
        ):
            return True

        if any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in self.html_injection_patterns
        ):
            return True

        # Fuzzy matching for misspelled words (typoglycemia defense)
        words = re.findall(r"\b\w+\b", text.lower())
        for word in words:
            for pattern in self.fuzzy_patterns:
                if self._is_similar_word(word, pattern):
                    return True
        return False

    def _is_similar_word(self, word: str, target: str) -> bool:
        """Check if word is a typoglycemia variant of target"""
        if len(word) != len(target) or len(word) < 3:
            return False
        # Same first and last letter, scrambled middle
        return (
            word[0] == target[0]
            and word[-1] == target[-1]
            and sorted(word[1:-1]) == sorted(target[1:-1])
        )

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input text to remove potential injection attempts.

        Args:
            text: The input text to sanitize

        Returns:
            Sanitized text
        """
        # Normalize common obfuscations
        text = re.sub(r"\s+", " ", text)  # Collapse whitespace
        text = re.sub(r"(.)\1{3,}", r"\1", text)  # Remove char repetition

        for pattern in self.dangerous_patterns:
            text = re.sub(pattern, "[FILTERED]", text, flags=re.IGNORECASE)
        return text[:10000]  # Limit length
