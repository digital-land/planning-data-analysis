import re
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process


def clean_text(text):
    """
    Cleans the provided text by replacing or removing unwanted characters.
    """
    text = re.sub(
        r"[^\x00-\x7F]+", "'", text
    )  # Replace all non-ASCII characters with an apostrophe
    text = re.sub(r"\[\s*pdf\s*\]", "", text, flags=re.IGNORECASE)  # Remove [pdf] tags
    text = re.sub(r"\s+", " ", text)  # Normalise any excessive spaces
    text = re.sub(
        r"\(\d+(,\d{3})?KB\)|\d+(,\d{3})?KB|\d+MB", "", text
    )  # Remove file sizes like (63KB), 63KB, or 12MB

    # Split the text into words and remove apostrophes at the end of each word
    words = text.split()
    cleaned_words = [
        word.rstrip("'") for word in words
    ]  # Remove apostrophe at the end of each word

    cleaned_text = " ".join(cleaned_words)

    return cleaned_text.strip()


def extract_links_from_page(url, plan_prefix, reference_data):
    """
    Extracts all document links from a webpage, cleans the text associated with each link,
    and matches the text with a reference from an external CSV file.

    Parameters:
    url (str): The URL of the webpage to scrape.
    plan_prefix (str): The prefix to use for naming references.
    reference_data (pd.DataFrame): The dataframe containing the reference data to match with.

    Returns:
    list: A list of lists, where each sublist contains the reference, plan prefix, cleaned text,
          full URL of the document, the input URL, and the matched reference from the CSV.
    """

    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all <a> tags that contain href attributes
    links = soup.find_all("a", href=True)

    link_data = []
    counter = 1

    # Process href links and check if they contain 'pdf', 'doc', 'document', or 'file'
    for link in links:
        href = link["href"]
        full_url = urljoin(url, href)  # Handle relative URLs

        # Check if 'pdf', 'doc', 'document', or 'file' is in the URL
        if any(x in href.lower() for x in ["pdf", "doc", "document", "file"]):
            text = link.get_text(strip=True)  # Get the link text
            text = clean_text(text)  # Clean the text
            reference = f"{plan_prefix}-{counter}"  # Create the reference using the plan prefix and counter

            # Fuzzy match the text to the "name" column in reference_data
            match = process.extractOne(text, reference_data["name"])
            matched_reference = (
                reference_data.loc[
                    reference_data["name"] == match[0], "reference"
                ].values[0]
                if match
                else None
            )

            link_data.append(
                [reference, plan_prefix, text, full_url, url, matched_reference]
            )
            counter += 1

    return link_data


def collect_plan_data(input_csv, reference_csv, output_path, failed_urls_path=None):
    """
    Main function to collect plan data from URLs and save to CSV.

    Parameters:
    input_csv (str): Path to input CSV containing 'reference' and 'documentation-url' columns
    reference_csv (str): Path to reference CSV containing document type mappings
    output_path (str): Path to save the output CSV
    failed_urls_path (str, optional): Path to save failed URLs
    """
    # Load the main DataFrame containing 'reference' and 'documentation-url'
    df = pd.read_csv(input_csv)

    # Load the reference data from the CSV file
    reference_data = pd.read_csv(reference_csv)

    # Create an empty list to hold all extracted link data
    all_link_data = []
    failed_urls = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        ref = row["reference"]
        url = row["documentation-url"]

        try:
            link_data = extract_links_from_page(url, ref, reference_data)
            all_link_data.extend(link_data)
        except Exception as e:
            print(f"Error processing {url} with plan {ref}: {e}")
            failed_urls.append((ref, url))
            continue

    # Create a DataFrame from the combined list of link data
    final_df = pd.DataFrame(
        all_link_data,
        columns=["reference", "plan", "text", "url", "input_url", "matched_reference"],
    )

    # Populate blank rows with 'supplementary-planning-documents'
    final_df["matched_reference"].fillna(
        "supplementary-planning-documents", inplace=True
    )

    # Rename columns to specification
    final_df.rename(
        columns={
            "text": "name",
            "url": "document-url",
            "input_url": "documentation-url",
            "matched_reference": "document-types",
        },
        inplace=True,
    )

    # Save the final DataFrame
    final_df.to_csv(output_path, index=False)
    print(f"Data saved as {output_path}")

    # Save failed URLs if any and path provided
    if failed_urls and failed_urls_path:
        failed_df = pd.DataFrame(
            failed_urls, columns=["reference", "documentation-url"]
        )
        failed_df.to_csv(failed_urls_path, index=False)
        print(f"Failed URLs saved to {failed_urls_path}")
        print("\nThe following URLs failed during processing:")
        for ref, failed_url in failed_urls:
            print(f"Reference: {ref}, URL: {failed_url}")

    return final_df
