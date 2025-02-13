# Imports
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from fuzzywuzzy import process
import warnings
from slugify import slugify

def clean_text(text):
    """
    Cleans the provided text by replacing or removing unwanted characters.
    """
    text = re.sub(r'[^\x00-\x7F]+', "'", text)  # Replace all non-ASCII characters with an apostrophe
    text = re.sub(r'\[\s*pdf\s*\]', '', text, flags=re.IGNORECASE)  # Remove [pdf] tags
    text = re.sub(r'\s+', ' ', text)  # Normalise any excessive spaces
    text = re.sub(r'\(\d+(,\d{3})?KB\)|\d+(,\d{3})?KB|\d+MB', '', text)  # Remove file sizes like (63KB), 63KB, or 12MB

    # Split the text into words and remove apostrophes at the end of each word
    words = text.split()
    cleaned_words = [word.rstrip("'") for word in words]  # Remove apostrophe at the end of each word

    cleaned_text = ' '.join(cleaned_words)

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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

    response = requests.get(url, verify=False)
    #response = requests.get(url, verify=certifi.where())
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> tags that contain href attributes
    links = soup.find_all('a', href=True)
    
    link_data = []
    counter = 1
    
    # Process href links and check if they contain 'pdf', 'doc', 'document', or 'file'
    for link in links:
        href = link['href']
        full_url = urljoin(url, href)  # Handle relative URLs
        
        # Check if 'pdf', 'doc', 'document', or 'file' is in the URL
        if any(x in href.lower() for x in ['pdf', 'doc', 'document', 'file']):
            text = link.get_text(strip=True)  # Get the link text
            text = clean_text(text)  # Clean the text
            reference = f"{plan_prefix}-{counter}"  # Create the reference using the plan prefix and counter
            
            # Fuzzy match the text to the "name" column in reference_data
            match = process.extractOne(text, reference_data['name'])
            matched_reference = reference_data.loc[reference_data['name'] == match[0], 'reference'].values[0] if match else None

            link_data.append([reference, plan_prefix, text, full_url, url, matched_reference])  # Add the matched reference
            counter += 1  # Increment the counter for each link

    return link_data

# Main script logic
if __name__ == "__main__":
    # Load your main DataFrame (df) containing 'reference' and 'documentation-url'
    df = pd.read_csv('')  

    # Load the reference data from the CSV file (assumed to be the same for all rows)
    reference_data = pd.read_csv('documents/development-plan-document-type.csv')

    # Create an empty list to hold all extracted link data across all iterations
    all_link_data = []

    # List to hold tuples of failed URLs and their associated plan_prefix
    failed_urls = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        ref = row['reference']  # Reference from the current row
        url = row['documentation-url']  # Documentation URL from the current row

        try:
            # Attempt to extract links from the current page
            link_data = extract_links_from_page(url, ref, reference_data)
            
            # Append the extracted data to the all_link_data list
            all_link_data.extend(link_data)
        except Exception as e:
            # If an error occurs, print the error and add the URL and plan_prefix to the failed list
            print(f"Error processing {url} with plan {ref}: {e}")
            failed_urls.append((ref, url))
            continue  # Move on to the next URL

    # Create a DataFrame from the combined list of link data
    final_df = pd.DataFrame(all_link_data, columns=['reference', 'plan', 'text', 'url', 'input_url', 'matched_reference'])
    
    # Populate blank rows with 'supplementary-planning-documents'
    final_df['matched_reference'].fillna('supplementary-planning-documents', inplace=True)
    
    # Rename columns to specification
    final_df.rename(columns={'text':'name', 
                             'url':'document-url', 
                             'input_url':'documentation-url', 
                             'matched_reference':'document-types'}, 
                   inplace=True
                   )

    # Save the final DataFrame as a CSV file
    output_path = ''
    final_df.to_csv(output_path, index=False)

    print(f"Data saved as {output_path}")

    # Save failed URLs along with their plan_prefix to a CSV file
    if failed_urls:
        # Create a DataFrame for failed URLs with columns 'reference' and 'documentation-url'
        failed_df = pd.DataFrame(failed_urls, columns=['reference', 'documentation-url'])
        failed_urls_path = 'data/failed_urls.csv' 
        failed_df.to_csv(failed_urls_path, index=False)

        print(f"Failed URLs saved to {failed_urls_path}")

        # Print out the list of failed URLs
        print("\nThe following URLs failed during processing:")
        for ref, failed_url in failed_urls:
            print(f"Reference: {ref}, URL: {failed_url}")
