import os
import click
from urllib.parse import urlparse

def validate_pdf(ctx, param, value):
    """
    Validate that the input is a local PDF file.
    Must exist and have .pdf extension.
    """
    if os.path.isfile(value) and value.lower().endswith(".pdf"):
        return value
    raise click.BadParameter(f"'{value}' must be an existing local PDF file.")

def validate_url(ctx, param, value):
    """
    Validate that the input is a remote URL.
    Must have both scheme and netloc components.
    """
    parsed = urlparse(value)
    if parsed.scheme and parsed.netloc:
        return value
    raise click.BadParameter(f"'{value}' must be a valid URL.")