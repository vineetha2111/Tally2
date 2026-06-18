"""Terminal entry point for the local AI Analytics application."""

import sys
import textwrap

from app.agents.orchestrator import AgentOrchestrator
from app.config.logging import setup_logging, get_logger
from app.config.settings import get_settings
from app.database.session import check_database_connection
from app.schemas.state import AnalyticsStateModel

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║           Tally AI Analytics — Local Intelligence            ║
║     Natural Language → SQL → Insights → Executive Summary    ║
╚══════════════════════════════════════════════════════════════╝
"""

SECTION_WIDTH = 50


def print_section(title: str, content: str) -> None:
    """Print a formatted section to the terminal."""
    print("=" * SECTION_WIDTH)
    print(title.upper())
    print("=" * SECTION_WIDTH)
    wrapped = textwrap.fill(content, width=78) if content else "(empty)"
    print(wrapped)
    print()


def print_results(result: AnalyticsStateModel) -> None:
    """Render pipeline results in the required format."""
    print_section("QUESTION", result.question)
    print_section("INTENT", result.intent or "N/A")

    schema_preview = result.schema_context[:500]
    if len(result.schema_context) > 500:
        schema_preview += "\n... (truncated)"
    print_section("SCHEMA", schema_preview or "N/A")
    print_section("GENERATED SQL", result.sql_query or "N/A")
    print_section("ROWS RETRIEVED", str(len(result.query_results)))

    if result.error:
        print_section("ERROR", result.error)

    print_section("ANALYSIS", result.analysis or "N/A")
    print_section("EXECUTIVE SUMMARY", result.summary or "N/A")


def run_interactive() -> None:
    """Run the interactive question loop."""
    logger = get_logger("main")
    settings = get_settings()

    print(BANNER)
    print(f"Model: {settings.ollama_model}")
    print(f"Database: {settings.database_url.split('@')[-1]}")
    print("Type your business question, or 'quit' / 'exit' to stop.\n")

    try:
        check_database_connection(settings)
    except Exception as exc:
        print(f"Database connection failed: {exc}")
        print("Ensure PostgreSQL is running and DATABASE_URL is correct in .env")
        sys.exit(1)

    orchestrator = AgentOrchestrator(settings)

    while True:
        try:
            question = input("Ask a business question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        logger.info("Processing question: %s", question)
        try:
            result = orchestrator.invoke(question)
            print_results(result)
        except Exception as exc:
            logger.exception("Unhandled error during workflow")
            print_section("ERROR", str(exc))


def main() -> None:
    """Application entry point."""
    setup_logging()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        settings = get_settings()
        check_database_connection(settings)
        orchestrator = AgentOrchestrator(settings)
        result = orchestrator.invoke(question)
        print_results(result)
    else:
        run_interactive()


if __name__ == "__main__":
    main()
