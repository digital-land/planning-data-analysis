
import click
from planning_data_analysis.extract import extract_table
from planning_data_analysis.validators import validate_pdf, validate_url
from planning_data_analysis.utils import save_to_csv

@click.group()
def cli():
    """A command-line interface with multiple commands."""
    pass

@cli.command(name="extract-from-file")
@click.option("--pdf", "pdf_path", required=True, callback=validate_pdf, help="Path to input PDF file.")
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option("--output", "output_folder", default="output_tables", help="Output folder.")
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_file_command(pdf_path, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from pdf file
    """
    tables = extract_table(pdf_path, table_index, from_file=True, key_words=key_words)
    if tables:
        save_to_csv(tables, output_folder)

@cli.command(name="extract-from-web")
@click.option("--url", "url", required=True, callback=validate_url, help="URL to input file.")
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option("--output", "output_folder", default="output_tables", help="Output folder.")
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_web_command(url, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from web page
    """
    tables = extract_table(url, table_index, from_web=True, key_words=key_words)
    if tables:
        save_to_csv(tables, output_folder)


if __name__ == "__main__":
    cli()
