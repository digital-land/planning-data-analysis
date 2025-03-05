# Data analysis tools for planning data

## Getting started

Create a python virtual environment and install the dependencies:

```
make init
```

## Installation

To install and run locally, run:

```
pip install -e .
```

## Usage

To run the CLI, run:

```
pda [command] [options]
```

### Commands

#### Extract tables from a PDF file

index parameter is optional, if not provided, all tables will be extracted.

```
pda extract-from-file --pdf <path-to-pdf-file> --index <table-index>
```

#### Extract tables from a web page

index parameter is optional, if not provided, all tables will be extracted.

```
pda extract-from-web --url <url> --index <table-index>
```

#### Collect plan data from URLs

Collects plan data from URLs and saves it to a CSV file. Requires input CSV with 'reference' and 'documentation-url' columns.

```
pda collect-plan-data --input <input-csv> --reference <reference-csv> --output <output-csv> [--failed-urls <failed-urls-csv>]
```

#### Process Community Infrastructure Levy (CIL) data

Processes CIL and Infrastructure Funding Statements (IFS) data, cleaning and mapping local authority codes.

```
pda process-cil --input <input-csv> --reference <reference-csv> [--output <output-dir>]
```

#### Analyze clusters in invalid application reasons

Analyzes clusters in invalid application reasons and generates visualizations and reports.

```
pda analyze-clusters --input <input-csv> [--output <output-dir>]
```

#### Generate EDA report for geospatial data

Generates an exploratory data analysis report for geospatial data, including visualizations and metadata.

```
pda generate-eda-report --dataset <dataset-name> --input <input-dir> [--output <output-dir>]
```

#### Collect WFS data

Collects data from WFS layers and saves as GeoPackage files. Defaults to CASI and LiDAR habitat map service.

```
pda collect-wfs [--capabilities-url <url>] [--wfs-url <url>] [--output <output-dir>]
```
