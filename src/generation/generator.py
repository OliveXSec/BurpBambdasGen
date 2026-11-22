"""Bambda generation using Claude API."""

import re
from dataclasses import dataclass
from typing import AsyncIterator, Optional

import anthropic

from ..config.prompts import (
    SYSTEM_PROMPT,
    build_generation_prompt,
    detect_bambda_type,
)
from ..config.settings import settings
from ..retrieval.retriever import BambdaRetriever
from .validator import BambdaValidator, ValidationResult


@dataclass
class GenerationResult:
    """Result of bambda generation."""
    code: str
    bambda_type: str
    suggested_name: str
    validation: ValidationResult
    examples_used: list
    tokens_used: int


class BambdaGenerator:
    """Generate bambda scripts using Claude and RAG."""

    def __init__(
        self,
        retriever: BambdaRetriever,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize the generator.

        Args:
            retriever: BambdaRetriever for context retrieval
            api_key: Anthropic API key (defaults to settings)
            model: Model name (defaults to settings)
        """
        self.retriever = retriever
        self.client = anthropic.Anthropic(
            api_key=api_key or settings.anthropic_api_key
        )
        self.model = model or settings.model_name
        self.validator = BambdaValidator()

    def generate(
        self,
        description: str,
        bambda_type: Optional[str] = None,
        n_examples: int = 3,
        n_docs: int = 5,
    ) -> GenerationResult:
        """Generate a bambda script from a description.

        Args:
            description: Natural language description of the desired bambda
            bambda_type: Type of bambda (auto-detected if not provided)
            n_examples: Number of examples to retrieve
            n_docs: Number of documentation chunks to retrieve

        Returns:
            GenerationResult with the generated code and metadata
        """
        # Auto-detect bambda type if not provided
        if not bambda_type:
            bambda_type = detect_bambda_type(description)

        # Retrieve relevant context
        context = self.retriever.retrieve_as_context(
            query=description,
            bambda_type=bambda_type,
            n_examples=n_examples,
            n_docs=n_docs,
        )

        # Build the prompt
        user_prompt = build_generation_prompt(
            user_request=description,
            bambda_type=bambda_type,
            context=context,
        )

        # Generate with Claude
        response = self.client.messages.create(
            model=self.model,
            max_tokens=settings.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Extract code from response
        raw_response = response.content[0].text
        code = self._extract_code(raw_response)

        # Determine final bambda type
        final_type = bambda_type or self._infer_type_from_code(code) or "VIEW_FILTER"

        # Validate the generated code
        validation = self.validator.validate(code, final_type)

        # Generate suggested name
        suggested_name = self._generate_name(description)

        return GenerationResult(
            code=code,
            bambda_type=final_type,
            suggested_name=suggested_name,
            validation=validation,
            examples_used=[ex.get("name", "Unknown") for ex in context.examples],
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
        )

    async def generate_stream(
        self,
        description: str,
        bambda_type: Optional[str] = None,
        n_examples: int = 3,
        n_docs: int = 5,
    ) -> AsyncIterator[str]:
        """Generate a bambda script with streaming output.

        Args:
            description: Natural language description
            bambda_type: Type of bambda
            n_examples: Number of examples to retrieve
            n_docs: Number of documentation chunks to retrieve

        Yields:
            Chunks of generated text
        """
        # Auto-detect bambda type if not provided
        if not bambda_type:
            bambda_type = detect_bambda_type(description)

        # Retrieve relevant context
        context = self.retriever.retrieve_as_context(
            query=description,
            bambda_type=bambda_type,
            n_examples=n_examples,
            n_docs=n_docs,
        )

        # Build the prompt
        user_prompt = build_generation_prompt(
            user_request=description,
            bambda_type=bambda_type,
            context=context,
        )

        # Stream with Claude
        async_client = anthropic.AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )

        async with async_client.messages.stream(
            model=self.model,
            max_tokens=settings.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    def _extract_code(self, response: str) -> str:
        """Extract Java code from the response.

        Args:
            response: Raw response from Claude

        Returns:
            Extracted Java code
        """
        # Try to extract from code block
        code_match = re.search(r'```(?:java)?\n?(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()

        # If no code block, check if response looks like Java code
        if response.strip().startswith(("/**", "//", "var ", "if ", "return ")):
            return response.strip()

        # Return as-is if nothing else works
        return response.strip()

    def _infer_type_from_code(self, code: str) -> Optional[str]:
        """Infer bambda type from the generated code.

        Args:
            code: Generated Java code

        Returns:
            Inferred bambda type or None
        """
        # Check return statements
        if re.search(r'return\s+(true|false)\s*;', code):
            return "VIEW_FILTER"
        if re.search(r'return\s+"[^"]*"\s*;', code) or re.search(r'return\s+\w+\s*;.*String', code):
            return "CUSTOM_COLUMN"
        if "AuditResult" in code or "AuditIssue" in code:
            if "sendRequest" in code:
                return "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT"
            return "SCAN_CHECK_PASSIVE"
        if "httpEditor" in code or "selection" in code:
            return "CUSTOM_ACTION"
        if "HttpRequest" in code and "return" in code:
            return "MATCH_AND_REPLACE_REQUEST"
        if "HttpResponse" in code and "return" in code:
            return "MATCH_AND_REPLACE_RESPONSE"

        return None

    def _generate_name(self, description: str) -> str:
        """Generate a suggested name for the bambda.

        Args:
            description: User's description

        Returns:
            Suggested bambda name
        """
        # Extract key words and create a name
        words = description.lower().split()

        # Remove common words
        stop_words = {"a", "an", "the", "to", "for", "with", "that", "this", "in", "on", "of", "and", "or"}
        key_words = [w for w in words if w not in stop_words and len(w) > 2]

        # Take first 3-4 key words and capitalize
        name_words = key_words[:4]
        name = "".join(word.capitalize() for word in name_words)

        return name or "CustomBambda"
