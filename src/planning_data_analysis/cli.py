import click

from planning_data_analysis.cil_process import process_and_save
from planning_data_analysis.cluster_analysis import analyze_clusters
from planning_data_analysis.collect_plan_data import collect_plan_data
from planning_data_analysis.eda_report import generate_eda_report
from planning_data_analysis.extract import extract_table
from planning_data_analysis.utils import save_to_csv
from planning_data_analysis.validators import validate_pdf, validate_url
from planning_data_analysis.wfs_collect import collect_wfs_layers


@click.group()
def cli():
    """A command-line interface with multiple commands."""
    pass


@cli.command(name="extract-from-file")
@click.option(
    "--pdf",
    "pdf_path",
    required=True,
    callback=validate_pdf,
    help="Path to input PDF file.",
)
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option(
    "--output", "output_folder", default="output_tables", help="Output folder."
)
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_file_command(pdf_path, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from pdf file
    """
    tables = extract_table(pdf_path, table_index, from_file=True, key_words=key_words)
    if tables:
        save_to_csv(tables, output_folder)


@cli.command(name="extract-from-web")
@click.option(
    "--url", "url", required=True, callback=validate_url, help="URL to input file."
)
@click.option("--index", "table_index", default=None, help="Table index.")
@click.option(
    "--output", "output_folder", default="output_tables", help="Output folder."
)
@click.option("--key-words", "key_words", default=None, help="Key words.")
def extract_from_web_command(url, table_index, output_folder, key_words):
    """
    CLI wrapper around planning_data_analysis.extract_pdf_tables.extract from web page
    """
    tables = extract_table(url, table_index, from_web=True, key_words=key_words)
    if tables:
        save_to_csv(tables, output_folder)


@cli.command(name="collect-plan-data")
@click.option(
    "--input",
    "input_csv",
    required=True,
    help="Path to input CSV containing 'reference' and 'documentation-url' columns",
)
@click.option(
    "--reference",
    "reference_csv",
    required=True,
    help="Path to reference CSV containing document type mappings",
)
@click.option(
    "--output", "output_path", required=True, help="Path to save the output CSV"
)
@click.option(
    "--failed-urls",
    "failed_urls_path",
    default=None,
    help="Path to save failed URLs (optional)",
)
def collect_plan_data_command(input_csv, reference_csv, output_path, failed_urls_path):
    """
    Collect plan data from URLs and save to CSV.
    """
    collect_plan_data(input_csv, reference_csv, output_path, failed_urls_path)


@cli.command(name="process-cil")
@click.option(
    "--input",
    "input_csv",
    required=True,
    help="Path to input CSV file containing CIL and IFS documents",
)
@click.option(
    "--reference",
    "reference_csv",
    required=True,
    help="Path to reference CSV file containing local authority mappings",
)
@click.option(
    "--output",
    "output_dir",
    default="output_cil",
    help="Directory to save the output CSV files",
)
def process_cil_command(input_csv, reference_csv, output_dir):
    """
    Process Community Infrastructure Levy (CIL) data and save separate datasets for CIL and IFS.
    """
    process_and_save(input_csv, reference_csv, output_dir)


@cli.command(name="analyze-clusters")
@click.option(
    "--input",
    "input_csv",
    required=True,
    help="Path to input CSV file containing invalid application reasons",
)
@click.option(
    "--output",
    "output_dir",
    default="output_clusters",
    help="Directory to save output files",
)
def analyze_clusters_command(input_csv, output_dir):
    """
    Analyze clusters in invalid application reasons and generate visualizations and reports.
    """
    analyze_clusters(input_csv, output_dir)


@cli.command(name="generate-eda-report")
@click.option(
    "--dataset",
    "dataset",
    required=True,
    help="Name of the dataset",
)
@click.option(
    "--input",
    "input_dir",
    required=True,
    help="Path to input directory containing geospatial files",
)
@click.option(
    "--output",
    "output_dir",
    default="output_eda",
    help="Directory to save reports and visualizations",
)
def generate_eda_report_command(dataset, input_dir, output_dir):
    """
    Generate an exploratory data analysis report for geospatial data.
    """
    generate_eda_report(dataset, input_dir, output_dir)


@cli.command(name="collect-wfs")
@click.option(
    "--capabilities-url",
    "capabilities_url",
    default="https://environment.data.gov.uk/spatialdata/casi-and-lidar-habitat-map/wfs?service=WFS&request=GetCapabilities&version=2.0.0",  # noqa: E501
    help="URL for the WFS GetCapabilities request. Defaults to CASI and LiDAR habitat map service.",
)
@click.option(
    "--wfs-url",
    "wfs_url",
    default="https://environment.data.gov.uk/spatialdata/casi-and-lidar-habitat-map/wfs",  # noqa: E501
    help="Base URL for the WFS service. Defaults to CASI and LiDAR habitat map service.",
)
@click.option(
    "--output",
    "output_dir",
    default="output_wfs",
    help="Directory to save the output GeoPackage files",
)
def collect_wfs_command(capabilities_url, wfs_url, output_dir):
    """
    Collect data from all available WFS layers and save as GeoPackage files.
    The default URLs point to the CASI and LiDAR habitat map service, but these can be overridden
    to collect data from other WFS services.
    """
    collect_wfs_layers(capabilities_url, wfs_url, output_dir)


if __name__ == "__main__":
    cli()
