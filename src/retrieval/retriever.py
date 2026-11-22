"""Retrieval logic for bambda generation."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..config.prompts import RetrievedContext
from .vectorstore import VectorStore


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""
    examples: List[Dict[str, Any]]
    documentation: List[Dict[str, Any]]
    bambda_type: Optional[str]


class BambdaRetriever:
    """Retrieve relevant bambda examples and documentation."""

    def __init__(self, vectorstore: VectorStore):
        """Initialize the retriever.

        Args:
            vectorstore: VectorStore instance to search
        """
        self.vectorstore = vectorstore

    def retrieve(
        self,
        query: str,
        bambda_type: Optional[str] = None,
        n_examples: int = 3,
        n_docs: int = 5,
    ) -> RetrievalResult:
        """Retrieve relevant examples and documentation.

        Args:
            query: User's query/description
            bambda_type: Optional bambda type filter
            n_examples: Number of bambda examples to retrieve
            n_docs: Number of documentation chunks to retrieve

        Returns:
            RetrievalResult with examples and documentation
        """
        # Search for similar bambda examples
        examples = self.vectorstore.search_bambdas(
            query=query,
            n_results=n_examples,
            bambda_type=bambda_type,
        )

        # Search for relevant documentation
        documentation = self.vectorstore.search_documentation(
            query=query,
            n_results=n_docs,
        )

        return RetrievalResult(
            examples=examples,
            documentation=documentation,
            bambda_type=bambda_type,
        )

    def retrieve_as_context(
        self,
        query: str,
        bambda_type: Optional[str] = None,
        n_examples: int = 3,
        n_docs: int = 5,
    ) -> RetrievedContext:
        """Retrieve and format as context for prompt building.

        Args:
            query: User's query/description
            bambda_type: Optional bambda type filter
            n_examples: Number of bambda examples to retrieve
            n_docs: Number of documentation chunks to retrieve

        Returns:
            RetrievedContext ready for prompt building
        """
        result = self.retrieve(query, bambda_type, n_examples, n_docs)

        # Format examples for the context
        formatted_examples = []
        for ex in result.examples:
            formatted_examples.append({
                "name": ex["metadata"].get("bambda_name", "Unknown"),
                "bambda_type": ex["metadata"].get("bambda_type", "Unknown"),
                "location": ex["metadata"].get("location", "Unknown"),
                "description": ex["metadata"].get("description", "No description"),
                "source": ex["content"],
            })

        # Format documentation for the context
        formatted_docs = []
        for doc in result.documentation:
            formatted_docs.append({
                "section": doc["metadata"].get("section", "Unknown"),
                "content": doc["content"],
            })

        return RetrievedContext(
            examples=formatted_examples,
            documentation=formatted_docs,
        )

    def get_example_by_type(
        self,
        bambda_type: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """Get bambda examples filtered by type.

        Args:
            bambda_type: Type of bambda to retrieve
            n_results: Number of results

        Returns:
            List of bambda examples
        """
        return self.vectorstore.search_bambdas(
            query="",  # Empty query to get all
            n_results=n_results,
            bambda_type=bambda_type,
        )

    def search_examples(
        self,
        query: str,
        n_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search bambda examples by query.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            List of matching bambda examples
        """
        return self.vectorstore.search_bambdas(
            query=query,
            n_results=n_results,
        )
