"""Document loaders for bambda files and documentation."""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Document:
    """Represents a document chunk for the vector store."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def generate_id(content: str, prefix: str = "") -> str:
    """Generate a unique ID based on content hash."""
    hash_val = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_val}" if prefix else hash_val


class BambdaLoader:
    """Load and parse .bambda files."""

    # Mapping from function names to standardized types
    FUNCTION_MAPPING = {
        "VIEW_FILTER": "VIEW_FILTER",
        "CUSTOM_COLUMN": "CUSTOM_COLUMN",
        "CUSTOM_ACTION": "CUSTOM_ACTION",
        "MATCH_AND_REPLACE_REQUEST": "MATCH_AND_REPLACE_REQUEST",
        "MATCH_AND_REPLACE_RESPONSE": "MATCH_AND_REPLACE_RESPONSE",
        "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT",
        "SCAN_CHECK_ACTIVE_PER_REQUEST": "SCAN_CHECK_ACTIVE_PER_REQUEST",
        "SCAN_CHECK_PASSIVE": "SCAN_CHECK_PASSIVE",
    }

    def load_file(self, file_path: Path) -> Optional[Document]:
        """Load a single .bambda file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Try to parse as YAML
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict) and "source" in data:
                    return self._parse_yaml_bambda(data, file_path)
            except yaml.YAMLError:
                pass

            # Fallback: treat entire content as Java source
            return self._parse_raw_bambda(content, file_path)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def _parse_yaml_bambda(self, data: dict, file_path: Path) -> Document:
        """Parse a YAML-formatted bambda file."""
        source = data.get("source", "")
        name = data.get("name", file_path.stem)
        function = data.get("function", "VIEW_FILTER")
        location = data.get("location", "PROXY_HTTP_HISTORY")

        # Extract metadata from Javadoc
        description, author = self._extract_javadoc(source)

        # Extract keywords from description and source
        keywords = self._extract_keywords(description + " " + name + " " + source)

        # Determine complexity
        complexity = self._estimate_complexity(source)

        metadata = {
            "file_name": file_path.name,
            "bambda_name": name,
            "bambda_type": self.FUNCTION_MAPPING.get(function, function),
            "location": location,
            "description": description,
            "author": author,
            "keywords": keywords,
            "complexity": complexity,
            "uses_ai": "api.ai()" in source or "api().ai()" in source,
            "uses_http_requests": "sendRequest" in source,
            "uses_collaborator": "collaborator" in source.lower(),
            "source_type": "bambda_example",
        }

        return Document(
            id=generate_id(source, "bambda"),
            content=source,
            metadata=metadata,
        )

    def _parse_raw_bambda(self, content: str, file_path: Path) -> Document:
        """Parse a raw Java bambda file."""
        description, author = self._extract_javadoc(content)
        keywords = self._extract_keywords(description + " " + file_path.stem)

        metadata = {
            "file_name": file_path.name,
            "bambda_name": file_path.stem,
            "bambda_type": "VIEW_FILTER",  # Default
            "location": "PROXY_HTTP_HISTORY",
            "description": description,
            "author": author,
            "keywords": keywords,
            "complexity": self._estimate_complexity(content),
            "source_type": "bambda_example",
        }

        return Document(
            id=generate_id(content, "bambda"),
            content=content,
            metadata=metadata,
        )

    def _extract_javadoc(self, source: str) -> tuple[str, str]:
        """Extract description and author from Javadoc comment."""
        description = ""
        author = "Unknown"

        # Match Javadoc block
        javadoc_match = re.search(r'/\*\*(.*?)\*/', source, re.DOTALL)
        if javadoc_match:
            javadoc = javadoc_match.group(1)

            # Extract author
            author_match = re.search(r'@author\s+(.+?)(?:\n|$)', javadoc)
            if author_match:
                author = author_match.group(1).strip()

            # Extract description (everything before first @tag)
            desc_match = re.search(r'^\s*\*?\s*(.+?)(?=\s*@|\s*$)', javadoc, re.DOTALL)
            if desc_match:
                description = re.sub(r'\s*\*\s*', ' ', desc_match.group(1)).strip()

        return description, author

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        # Security-related keywords to look for
        security_keywords = {
            "jwt", "token", "cookie", "csrf", "xss", "sql", "injection",
            "cors", "csp", "header", "auth", "session", "password",
            "ssrf", "lfi", "rfi", "rce", "xxe", "ssti", "idor",
            "redirect", "bypass", "vulnerability", "security",
            "filter", "highlight", "detect", "extract", "parse",
            "json", "xml", "graphql", "websocket", "api",
        }

        text_lower = text.lower()
        found = []

        for keyword in security_keywords:
            if keyword in text_lower:
                found.append(keyword)

        return found[:10]  # Limit to 10 keywords

    def _estimate_complexity(self, source: str) -> str:
        """Estimate script complexity based on code analysis."""
        lines = len(source.split('\n'))
        has_loops = bool(re.search(r'\b(for|while)\b', source))
        has_try_catch = 'try {' in source or 'try{' in source
        has_multiple_methods = source.count('private ') + source.count('public ') > 1

        if lines < 15 and not has_loops and not has_try_catch:
            return "simple"
        elif lines > 50 or has_multiple_methods:
            return "complex"
        else:
            return "medium"

    def load_directory(self, directory: Path) -> List[Document]:
        """Load all .bambda files from a directory recursively."""
        documents = []

        for bambda_file in directory.rglob("*.bambda"):
            doc = self.load_file(bambda_file)
            if doc:
                documents.append(doc)

        return documents


class DocumentationLoader:
    """Load and parse documentation files."""

    def load_file(self, file_path: Path, doc_type: str = "guide") -> List[Document]:
        """Load a documentation file and split into chunks."""
        try:
            content = file_path.read_text(encoding="utf-8")
            return self._split_into_sections(content, file_path, doc_type)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return []

    def _split_into_sections(
        self, content: str, file_path: Path, doc_type: str
    ) -> List[Document]:
        """Split documentation into sections based on headers."""
        documents = []

        # For the main docs file - split by major sections
        if doc_type == "guide":
            # Split by lines starting with uppercase or numbered sections
            sections = re.split(r'\n(?=[A-Z][A-Z\s]+\n|^\d+\.)', content)

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                # Get section title from first line
                lines = section.split('\n')
                title = lines[0].strip()[:100]

                if len(section) > 100:  # Only keep meaningful sections
                    doc = Document(
                        id=generate_id(section, "doc"),
                        content=section,
                        metadata={
                            "source": file_path.name,
                            "section": title,
                            "doc_type": doc_type,
                            "source_type": "documentation",
                        }
                    )
                    documents.append(doc)

        # For API reference - split by interface/class definitions
        elif doc_type == "api":
            # Split by interface definitions
            interfaces = re.split(r'\n(?=public interface|Interface:|package )', content)

            for interface in interfaces:
                interface = interface.strip()
                if not interface or len(interface) < 100:
                    continue

                # Extract interface name
                name_match = re.search(r'interface\s+(\w+)', interface)
                name = name_match.group(1) if name_match else "Unknown"

                doc = Document(
                    id=generate_id(interface, "api"),
                    content=interface[:5000],  # Limit size
                    metadata={
                        "source": file_path.name,
                        "section": name,
                        "doc_type": doc_type,
                        "source_type": "api_reference",
                    }
                )
                documents.append(doc)

        return documents


def load_all_documents(knowledge_base_path: Path) -> Dict[str, List[Document]]:
    """Load all documents from the knowledge base directory.

    Args:
        knowledge_base_path: Path to the knowledge base directory containing:
            - docs: Main documentation file
            - API: API reference file
            - bambdas/: Directory with .bambda examples

    Returns:
        Dictionary with 'bambdas' and 'documentation' lists of Documents.
    """
    bambda_loader = BambdaLoader()
    docs_loader = DocumentationLoader()

    result = {
        "bambdas": [],
        "documentation": [],
    }

    # Load bambda examples
    bambdas_dir = knowledge_base_path / "bambdas"
    if bambdas_dir.exists():
        result["bambdas"] = bambda_loader.load_directory(bambdas_dir)
        print(f"Loaded {len(result['bambdas'])} bambda examples")

    # Load main documentation
    docs_file = knowledge_base_path / "docs"
    if docs_file.exists():
        docs = docs_loader.load_file(docs_file, doc_type="guide")
        result["documentation"].extend(docs)
        print(f"Loaded {len(docs)} documentation sections")

    # Load API reference
    api_file = knowledge_base_path / "API"
    if api_file.exists():
        api_docs = docs_loader.load_file(api_file, doc_type="api")
        result["documentation"].extend(api_docs)
        print(f"Loaded {len(api_docs)} API reference sections")

    return result
