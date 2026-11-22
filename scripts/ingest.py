#!/usr/bin/env python3
"""Script to ingest documents into the database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.ingestion.chunker import chunk_documentation
from src.ingestion.loader import load_all_documents
from src.retrieval.vectorstore import SimpleStore


def main():
    """Run the ingestion process."""
    print("Bambda RAG - Document Ingestion")
    print("=" * 40)

    # Get knowledge base path from args or settings
    if len(sys.argv) > 1:
        kb_path = Path(sys.argv[1])
    else:
        kb_path = settings.knowledge_base_path

    if not kb_path.exists():
        print(f"Error: Knowledge base path does not exist: {kb_path}")
        sys.exit(1)

    print(f"\nKnowledge base: {kb_path}")
    print(f"Data directory: {settings.data_dir}")

    # Initialize store
    print("\nInitializing store...")
    store = SimpleStore(data_dir=settings.data_dir)

    # Check existing data
    existing_bambdas = store.get_bambda_count()
    existing_docs = store.get_docs_count()

    if existing_bambdas > 0 or existing_docs > 0:
        print("\nExisting data found:")
        print(f"  - Bambda examples: {existing_bambdas}")
        print(f"  - Documentation chunks: {existing_docs}")

        response = input("\nClear and re-ingest? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

        print("Clearing existing data...")
        store.clear()

    # Load documents
    print("\nLoading documents...")
    documents = load_all_documents(kb_path)

    print(f"  - Loaded {len(documents['bambdas'])} bambda examples")
    print(f"  - Loaded {len(documents['documentation'])} documentation sections")

    # Chunk documentation
    print("\nChunking documentation...")
    docs_chunked = chunk_documentation(documents["documentation"])
    print(f"  - Created {len(docs_chunked)} documentation chunks")

    # Add to store
    print("\nAdding bambda examples...")
    bambda_count = store.add_bambdas(documents["bambdas"])
    print(f"  - Added {bambda_count} bambda examples")

    print("\nAdding documentation...")
    docs_count = store.add_documentation(docs_chunked)
    print(f"  - Added {docs_count} documentation chunks")

    # Summary
    print("\n" + "=" * 40)
    print("Ingestion complete!")
    print(f"  - Total bambdas: {store.get_bambda_count()}")
    print(f"  - Total doc chunks: {store.get_docs_count()}")
    print(f"  - Bambda types: {', '.join(store.list_bambda_types())}")


if __name__ == "__main__":
    main()
