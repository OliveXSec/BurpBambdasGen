"""Simple JSON-based store for bambda documents (no vector DB needed)."""

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..ingestion.loader import Document


class SimpleStore:
    """Simple JSON-based store with keyword search."""

    def __init__(self, data_dir: Path):
        """Initialize the store.

        Args:
            data_dir: Directory for data persistence
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.bambda_file = self.data_dir / "bambdas.json"
        self.docs_file = self.data_dir / "documentation.json"

        self.bambdas: List[Dict[str, Any]] = []
        self.documentation: List[Dict[str, Any]] = []

        self._load()

    def _load(self):
        """Load data from JSON files."""
        if self.bambda_file.exists():
            with open(self.bambda_file, 'r', encoding='utf-8') as f:
                self.bambdas = json.load(f)

        if self.docs_file.exists():
            with open(self.docs_file, 'r', encoding='utf-8') as f:
                self.documentation = json.load(f)

    def _save(self):
        """Save data to JSON files."""
        with open(self.bambda_file, 'w', encoding='utf-8') as f:
            json.dump(self.bambdas, f, indent=2, ensure_ascii=False)

        with open(self.docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.documentation, f, indent=2, ensure_ascii=False)

    def add_bambdas(self, documents: List[Document]) -> int:
        """Add bambda examples to the store."""
        for doc in documents:
            # Check if already exists
            existing_ids = {b["id"] for b in self.bambdas}
            if doc.id not in existing_ids:
                self.bambdas.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "keywords": self._extract_keywords(doc.content + " " + doc.metadata.get("description", "")),
                })

        self._save()
        return len(documents)

    def add_documentation(self, documents: List[Document]) -> int:
        """Add documentation to the store."""
        for doc in documents:
            existing_ids = {d["id"] for d in self.documentation}
            if doc.id not in existing_ids:
                self.documentation.append({
                    "id": doc.id,
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "keywords": self._extract_keywords(doc.content),
                })

        self._save()
        return len(documents)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Count frequency
        counter = Counter(words)

        # Filter out common words
        stop_words = {
            "the", "and", "for", "with", "this", "that", "from", "are", "was",
            "were", "been", "being", "have", "has", "had", "will", "would",
            "could", "should", "may", "might", "must", "can", "does", "did",
            "var", "new", "return", "true", "false", "null", "void", "int",
            "string", "boolean", "public", "private", "static", "final",
            "import", "class", "interface", "extends", "implements",
        }

        keywords = [word for word, count in counter.most_common(30)
                   if word not in stop_words]

        return keywords[:20]

    def _score_match(self, item: Dict, query_keywords: List[str], bambda_type: Optional[str] = None) -> float:
        """Score how well an item matches the query."""
        score = 0.0

        item_keywords = set(item.get("keywords", []))
        query_set = set(query_keywords)

        # Keyword overlap
        overlap = item_keywords & query_set
        score += len(overlap) * 2

        # Check if query words appear in content
        content = item.get("content", "").lower()
        for kw in query_keywords:
            if kw in content:
                score += 1

        # Type match bonus
        if bambda_type:
            if item.get("metadata", {}).get("bambda_type") == bambda_type:
                score += 5

        # Description match
        description = item.get("metadata", {}).get("description", "").lower()
        for kw in query_keywords:
            if kw in description:
                score += 1.5

        return score

    def search_bambdas(
        self,
        query: str,
        n_results: int = 3,
        bambda_type: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for bambda examples."""
        query_keywords = self._extract_keywords(query)

        # Filter by type/location first
        candidates = self.bambdas
        if bambda_type:
            candidates = [b for b in candidates
                         if b.get("metadata", {}).get("bambda_type") == bambda_type]
        if location:
            candidates = [b for b in candidates
                         if b.get("metadata", {}).get("location") == location]

        # Score and sort
        scored = [(b, self._score_match(b, query_keywords, bambda_type)) for b in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = []
        for item, score in scored[:n_results]:
            results.append({
                "id": item["id"],
                "content": item["content"],
                "metadata": item["metadata"],
                "score": score,
            })

        return results

    def search_documentation(
        self,
        query: str,
        n_results: int = 5,
        doc_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search documentation."""
        query_keywords = self._extract_keywords(query)

        candidates = self.documentation
        if doc_type:
            candidates = [d for d in candidates
                         if d.get("metadata", {}).get("doc_type") == doc_type]

        scored = [(d, self._score_match(d, query_keywords)) for d in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for item, score in scored[:n_results]:
            results.append({
                "id": item["id"],
                "content": item["content"],
                "metadata": item["metadata"],
                "score": score,
            })

        return results

    def get_bambda_count(self) -> int:
        """Get number of bambdas."""
        return len(self.bambdas)

    def get_docs_count(self) -> int:
        """Get number of documentation chunks."""
        return len(self.documentation)

    def clear(self):
        """Clear all data."""
        self.bambdas = []
        self.documentation = []
        self._save()

    def list_bambda_types(self) -> List[str]:
        """List all bambda types."""
        types = set()
        for b in self.bambdas:
            t = b.get("metadata", {}).get("bambda_type")
            if t:
                types.add(t)
        return sorted(list(types))


# Alias for compatibility
VectorStore = SimpleStore
