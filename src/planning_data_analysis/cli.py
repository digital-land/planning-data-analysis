import os
import click
from src.planning_data_analysis.extract import extract_table
from urllib.parse import urlparse


def validate_pdf_local_or_remote_url(ctx, param, value):
    """
    Validation rules:
      - If it has a URL scheme/netloc -> accept it as a remote URL (no extension check).
      - Otherwise, must be a local PDF file (check existence & ".pdf" extension).
    """
    parsed = urlparse(value)

    # If it's a remote URL (has scheme + netloc), just return it
    if parsed.scheme and parsed.netloc:
        return value

    # Otherwise, treat it as a local file path
    if os.path.isfile(value) and value.lower().endswith(".pdf"):
        return value

    # Fails both checks
    raise click.BadParameter(
        f"'{value}' must either be a valid URL or an existing local PDF file."
    )

@click.group()
def cli():
    """A command-line interface with multiple commands."""
    pass

@cli.command(name="extract-from-file")
@click.option("--pdf", "input_path_or_url", required=True, callback=validate_pdf_local_or_remote_url, help="Path or URL to input file.")
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option("--output", "output_folder", default="output_tables", help="Output folder.")
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_file_command(input_path_or_url, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from pdf file
    """
    extract_table(input_path_or_url, table_index, from_file=True, output_folder=output_folder, key_words=key_words)


@cli.command(name="extract-from-web")
@click.option("--pdf", "input_path_or_url", required=True, callback=validate_pdf_local_or_remote_url, help="Path or URL to input file.")
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option("--output", "output_folder", default="output_tables", help="Output folder.")
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_web_command(input_path_or_url, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from web page
    """
    extract_table(input_path_or_url, table_index, from_web=True, output_folder=output_folder, key_words=key_words)


if __name__ == "__main__":
    cli()
