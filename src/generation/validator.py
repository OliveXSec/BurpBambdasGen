"""Validation for generated bambda scripts."""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    """Result of bambda validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class BambdaValidator:
    """Validate generated bambda scripts."""

    # Required patterns for each bambda type
    REQUIRED_PATTERNS = {
        "VIEW_FILTER": [
            (r'return\s+(true|false|[a-zA-Z_][a-zA-Z0-9_]*)\s*;', "Must return a boolean value"),
        ],
        "CUSTOM_COLUMN": [
            (r'return\s+("[^"]*"|[a-zA-Z_][a-zA-Z0-9_]*)\s*;', "Must return a String value"),
        ],
        "CUSTOM_ACTION": [],  # No specific return required
        "MATCH_AND_REPLACE_REQUEST": [
            (r'return\s+\w+\s*;', "Must return an HttpRequest"),
        ],
        "MATCH_AND_REPLACE_RESPONSE": [
            (r'return\s+\w+\s*;', "Must return an HttpResponse"),
        ],
        "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": [
            (r'AuditResult', "Must use AuditResult"),
        ],
        "SCAN_CHECK_ACTIVE_PER_REQUEST": [
            (r'AuditResult', "Must use AuditResult"),
        ],
        "SCAN_CHECK_PASSIVE": [
            (r'AuditResult', "Must use AuditResult"),
        ],
    }

    # Common code issues to check
    COMMON_ISSUES = [
        # Accessing response without checking hasResponse
        {
            "pattern": r'\.response\(\)',
            "negative_pattern": r'hasResponse\(\)',
            "warning": "Accessing response() without checking hasResponse() first",
        },
        # Accessing header value without checking hasHeader
        {
            "pattern": r'\.headerValue\(["\'][^"\']+["\']\)',
            "negative_pattern": r'hasHeader\(',
            "warning": "Consider checking hasHeader() before accessing headerValue()",
        },
    ]

    def validate(self, code: str, bambda_type: str) -> ValidationResult:
        """Validate a bambda script.

        Args:
            code: Java code to validate
            bambda_type: Type of bambda script

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Check for required patterns
        required = self.REQUIRED_PATTERNS.get(bambda_type, [])
        for pattern, error_msg in required:
            if not re.search(pattern, code):
                errors.append(error_msg)

        # Check for Javadoc
        if not code.strip().startswith("/**"):
            warnings.append("Missing Javadoc documentation block")

        # Check common issues
        for issue in self.COMMON_ISSUES:
            if re.search(issue["pattern"], code):
                if not re.search(issue["negative_pattern"], code):
                    warnings.append(issue["warning"])

        # Check for potential null pointer issues
        self._check_null_safety(code, warnings)

        # Check for syntax basics
        self._check_syntax_basics(code, errors)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def _check_null_safety(self, code: str, warnings: List[str]):
        """Check for potential null pointer issues."""

        # Check if using .get() results directly without null check
        if re.search(r'\.parameters\(\)\.get\([^)]+\)\.[^n]', code):
            if "!= null" not in code and "Optional" not in code:
                warnings.append("Parameter access may return null - consider null check")

        # Check string operations on potentially null values
        if re.search(r'\.bodyToString\(\)\.(contains|indexOf|split|replace)', code):
            if "hasBody()" not in code and "!= null" not in code:
                warnings.append("Body may be null or empty - consider checking first")

    def _check_syntax_basics(self, code: str, errors: List[str]):
        """Check basic Java syntax."""

        # Check for balanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")

        # Check for balanced parentheses
        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            errors.append(f"Unbalanced parentheses: {open_parens} opening, {close_parens} closing")

        # Check for common typos.
        # These are case-sensitive on purpose: `\bstring\b` must only match the
        # lowercase (invalid) spelling. Matching case-insensitively would flag the
        # correct `String` as well and mark every valid CUSTOM_COLUMN as invalid.
        typos = [
            (r'\bstring\b', "Use 'String' (capitalized) for the type"),
            (r'\bboolean\s+\w+\s*=\s*"', "Boolean variable assigned string value"),
        ]
        for pattern, msg in typos:
            if re.search(pattern, code):
                errors.append(msg)

    def validate_and_fix(self, code: str, bambda_type: str) -> tuple[str, ValidationResult]:
        """Validate and attempt to fix common issues.

        Args:
            code: Java code to validate
            bambda_type: Type of bambda script

        Returns:
            Tuple of (potentially fixed code, validation result)
        """
        # First validate
        result = self.validate(code, bambda_type)

        if result.is_valid:
            return code, result

        fixed_code = code

        # Attempt to fix missing Javadoc
        if "Missing Javadoc" in str(result.warnings):
            if not fixed_code.strip().startswith("/**"):
                fixed_code = f"/**\n * Generated Bambda script\n * @author BambdaRAG\n */\n{fixed_code}"

        # Re-validate
        new_result = self.validate(fixed_code, bambda_type)

        return fixed_code, new_result
