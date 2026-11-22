"""CLI application for Bambda RAG."""

import uuid
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from ..config.prompts import BAMBDA_TYPE_INFO
from ..config.settings import settings
from ..generation.generator import BambdaGenerator
from ..ingestion.chunker import chunk_documentation
from ..ingestion.loader import load_all_documents
from ..retrieval.retriever import BambdaRetriever
from ..retrieval.vectorstore import SimpleStore

app = typer.Typer(
    name="bambda-gen",
    help="Generate Burp Suite Bambda scripts using AI and RAG",
    add_completion=False,
)
console = Console()


def get_store() -> SimpleStore:
    """Get the store instance."""
    return SimpleStore(data_dir=settings.data_dir)


def get_generator() -> BambdaGenerator:
    """Get the generator instance."""
    store = get_store()
    retriever = BambdaRetriever(store)
    return BambdaGenerator(retriever)


@app.command()
def generate(
    description: str = typer.Argument(..., help="Description of the bambda to generate"),
    bambda_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Bambda type: filter, column, action, scan-active, scan-passive, match-request, match-response"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o",
        help="Output file path (without extension)"
    ),
    copy: bool = typer.Option(
        False, "--copy", "-c",
        help="Copy generated code to clipboard"
    ),
    examples: int = typer.Option(
        3, "--examples", "-e",
        help="Number of examples to use for context"
    ),
):
    """Generate a bambda script from a natural language description."""

    # Map short type names to full names
    type_mapping = {
        "filter": "VIEW_FILTER",
        "column": "CUSTOM_COLUMN",
        "action": "CUSTOM_ACTION",
        "scan-active": "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT",
        "scan-passive": "SCAN_CHECK_PASSIVE",
        "match-request": "MATCH_AND_REPLACE_REQUEST",
        "match-response": "MATCH_AND_REPLACE_RESPONSE",
    }

    if bambda_type:
        bambda_type = type_mapping.get(bambda_type.lower(), bambda_type)

    console.print("\n[bold blue]Generating bambda...[/bold blue]")

    if not settings.anthropic_api_key:
        console.print("[red]ANTHROPIC_API_KEY is not set.[/red]")
        console.print("Add it to .env or export it before running.")
        raise typer.Exit(1)

    try:
        generator = get_generator()
        result = generator.generate(
            description=description,
            bambda_type=bambda_type,
            n_examples=examples,
        )

        # Display the generated code
        console.print(f"\n[bold green]── {result.bambda_type}: {result.suggested_name} ──[/bold green]\n")
        syntax = Syntax(result.code, "java", theme="monokai", line_numbers=False)
        console.print(syntax)

        # Show validation results
        if result.validation.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.validation.warnings:
                console.print(f"  - {warning}")

        if result.validation.errors:
            console.print("\n[red]Errors:[/red]")
            for error in result.validation.errors:
                console.print(f"  - {error}")

        # Show metadata
        console.print(f"\n[dim]Examples used: {', '.join(result.examples_used)}[/dim]")
        console.print(f"[dim]Tokens used: {result.tokens_used}[/dim]")

        # Copy to clipboard if requested
        if copy:
            try:
                import pyperclip
                pyperclip.copy(result.code)
                console.print("\n[green]Copied to clipboard![/green]")
            except ImportError:
                console.print("\n[yellow]Install pyperclip for clipboard support: pip install pyperclip[/yellow]")
            except Exception as e:
                # pyperclip raises PyperclipException when no clipboard backend exists (headless Linux)
                console.print(f"\n[yellow]Clipboard unavailable: {e}[/yellow]")

        # Save to file if requested
        if output:
            save_bambda(result.code, result.suggested_name, result.bambda_type, output)

    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to knowledge base directory"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-ingestion"),
):
    """Ingest documents into the database."""

    kb_path = Path(path)
    if not kb_path.exists():
        console.print(f"[red]Error: Path does not exist: {path}[/red]")
        raise typer.Exit(1)

    console.print(f"\n[bold blue]Ingesting documents from: {path}[/bold blue]\n")

    store = get_store()

    # Check if already ingested
    existing_bambdas = store.get_bambda_count()
    existing_docs = store.get_docs_count()

    if (existing_bambdas > 0 or existing_docs > 0) and not force:
        console.print(f"[yellow]Database already contains {existing_bambdas} bambdas and {existing_docs} doc chunks.[/yellow]")
        if not Confirm.ask("Do you want to re-ingest?"):
            raise typer.Exit(0)
        store.clear()

    # Load documents
    console.print("Loading documents...")
    documents = load_all_documents(kb_path)

    # Chunk documentation
    console.print("Chunking documentation...")
    docs_chunked = chunk_documentation(documents["documentation"])

    # Add to store
    console.print("Adding bambda examples...")
    bambda_count = store.add_bambdas(documents["bambdas"])

    console.print("Adding documentation...")
    docs_count = store.add_documentation(docs_chunked)

    console.print("\n[green]Ingestion complete![/green]")
    console.print(f"  - Bambda examples: {bambda_count}")
    console.print(f"  - Documentation chunks: {docs_count}")


@app.command("list")
def list_examples(
    bambda_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search query"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
):
    """List bambda examples in the knowledge base."""

    store = get_store()

    if store.get_bambda_count() == 0:
        console.print("[yellow]No bambdas in database. Run 'bambda-gen ingest' first.[/yellow]")
        raise typer.Exit(1)

    retriever = BambdaRetriever(store)

    # Map short type names
    type_mapping = {
        "filter": "VIEW_FILTER",
        "column": "CUSTOM_COLUMN",
        "action": "CUSTOM_ACTION",
    }
    if bambda_type:
        bambda_type = type_mapping.get(bambda_type.lower(), bambda_type)

    # Search or list
    if search:
        results = retriever.search_examples(search, n_results=limit)
    elif bambda_type:
        results = retriever.get_example_by_type(bambda_type, n_results=limit)
    else:
        results = store.search_bambdas("bambda", n_results=limit)

    # Display results
    table = Table(title="Bambda Examples")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Description", style="white", max_width=50)

    for result in results:
        meta = result.get("metadata", {})
        desc = meta.get("description", "")
        table.add_row(
            meta.get("bambda_name", "Unknown"),
            meta.get("bambda_type", "Unknown"),
            desc[:50] + "..." if len(desc) > 50 else desc,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(results)} results[/dim]")


@app.command()
def types():
    """List available bambda types."""

    table = Table(title="Bambda Types")
    table.add_column("Type", style="cyan")
    table.add_column("Short Name", style="yellow")
    table.add_column("Return Type", style="green")
    table.add_column("Description", style="white")

    short_names = {
        "VIEW_FILTER": "filter",
        "CUSTOM_COLUMN": "column",
        "CUSTOM_ACTION": "action",
        "MATCH_AND_REPLACE_REQUEST": "match-request",
        "MATCH_AND_REPLACE_RESPONSE": "match-response",
        "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": "scan-active",
        "SCAN_CHECK_PASSIVE": "scan-passive",
    }

    for type_name, info in BAMBDA_TYPE_INFO.items():
        table.add_row(
            type_name,
            short_names.get(type_name, "-"),
            info["return_type"],
            info["description"],
        )

    console.print(table)


@app.command()
def interactive():
    """Start interactive mode for bambda generation."""

    if not settings.anthropic_api_key:
        console.print("[red]ANTHROPIC_API_KEY is not set.[/red]")
        console.print("Add it to .env or export it before running.")
        raise typer.Exit(1)

    console.print(Panel.fit(
        "[bold green]Bambda Generator - Interactive Mode[/bold green]\n\n"
        "Commands:\n"
        "  /type <type>  - Set bambda type (filter, column, action, etc.)\n"
        "  /save         - Save last generated bambda\n"
        "  /copy         - Copy last generated code to clipboard\n"
        "  /help         - Show help\n"
        "  /quit         - Exit\n\n"
        "Or just type a description to generate a bambda.",
        title="Welcome"
    ))

    generator = get_generator()
    current_type = None
    last_result = None

    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]>[/bold blue]")

            if not user_input.strip():
                continue

            # Handle commands
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()

                if cmd == "/quit" or cmd == "/exit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                elif cmd == "/help":
                    console.print("""
[bold]Available commands:[/bold]
  /type <type>  - Set bambda type (filter, column, action, scan-active, scan-passive)
  /save [name]  - Save last generated bambda to file
  /copy         - Copy last generated code to clipboard
  /clear        - Clear current type setting
  /quit         - Exit interactive mode

[bold]Type a description to generate a bambda.[/bold]
                    """)

                elif cmd == "/type":
                    if len(parts) > 1:
                        type_mapping = {
                            "filter": "VIEW_FILTER",
                            "column": "CUSTOM_COLUMN",
                            "action": "CUSTOM_ACTION",
                            "scan-active": "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT",
                            "scan-passive": "SCAN_CHECK_PASSIVE",
                        }
                        current_type = type_mapping.get(parts[1].lower(), parts[1])
                        console.print(f"[green]Type set to: {current_type}[/green]")
                    else:
                        console.print(f"[yellow]Current type: {current_type or 'auto-detect'}[/yellow]")

                elif cmd == "/clear":
                    current_type = None
                    console.print("[green]Type cleared (auto-detect enabled)[/green]")

                elif cmd == "/copy":
                    if last_result:
                        try:
                            import pyperclip
                            pyperclip.copy(last_result.code)
                            console.print("[green]Copied to clipboard![/green]")
                        except ImportError:
                            console.print("[yellow]Install pyperclip for clipboard support[/yellow]")
                        except Exception as e:
                            console.print(f"[yellow]Clipboard unavailable: {e}[/yellow]")
                    else:
                        console.print("[yellow]No generated code to copy[/yellow]")

                elif cmd == "/save":
                    if last_result:
                        name = parts[1] if len(parts) > 1 else last_result.suggested_name
                        save_bambda(last_result.code, name, last_result.bambda_type)
                    else:
                        console.print("[yellow]No generated code to save[/yellow]")

                else:
                    console.print(f"[yellow]Unknown command: {cmd}[/yellow]")

            else:
                # Generate bambda
                console.print("[dim]Generating...[/dim]")

                result = generator.generate(
                    description=user_input,
                    bambda_type=current_type,
                )
                last_result = result

                # Display result
                console.print(f"\n[bold green]── {result.bambda_type}: {result.suggested_name} ──[/bold green]\n")
                syntax = Syntax(result.code, "java", theme="monokai", line_numbers=False)
                console.print(syntax)

                if result.validation.warnings:
                    for warning in result.validation.warnings:
                        console.print(f"[yellow]Warning: {warning}[/yellow]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use /quit to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def status():
    """Show database status."""

    store = get_store()

    bambda_count = store.get_bambda_count()
    docs_count = store.get_docs_count()
    types = store.list_bambda_types()

    console.print(Panel.fit(
        f"[bold]Database Status[/bold]\n\n"
        f"Bambda examples: {bambda_count}\n"
        f"Documentation chunks: {docs_count}\n"
        f"Bambda types: {', '.join(types) if types else 'None'}",
        title="Bambda RAG"
    ))


def save_bambda(code: str, name: str, bambda_type: str, output_path: Optional[str] = None):
    """Save bambda to a file."""

    if output_path is None:
        output_path = Prompt.ask("Enter filename", default=name)

    filename = f"{output_path}.bambda" if not output_path.endswith('.bambda') else output_path

    # Determine location based on type
    location_mapping = {
        "VIEW_FILTER": "PROXY_HTTP_HISTORY",
        "CUSTOM_COLUMN": "PROXY_HTTP_HISTORY",
        "CUSTOM_ACTION": "REPEATER",
        "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": "SCANNER",
        "SCAN_CHECK_PASSIVE": "SCANNER",
        "MATCH_AND_REPLACE_REQUEST": "PROXY",
        "MATCH_AND_REPLACE_RESPONSE": "PROXY",
    }

    bambda_data = {
        "id": str(uuid.uuid4()),
        "name": name,
        "function": bambda_type,
        "location": location_mapping.get(bambda_type, "PROXY_HTTP_HISTORY"),
        "source": code,
    }

    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(bambda_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    console.print(f"[green]Saved to: {filename}[/green]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
