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


