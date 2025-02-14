import os
import pdfplumber
import pandas as pd
import requests
from bs4 import BeautifulSoup

def extract_table(input, table_index=None, key_words=None, from_file=False, from_web=False):
    extracted_tables = []
    
    if from_file:
        extracted_tables = _extract_from_pdf(input)
    elif from_web:
        extracted_tables = _extract_from_web(input)
    else:
        print("Invalid input. Provide a valid file path or URL.")
        return []
    
    if not extracted_tables:
        print("No tables extracted from the document.")
        return []
    
    # Normalise column names and print extracted columns for debugging
    for i, df in enumerate(extracted_tables):
        df.columns = [col.strip().replace("\n", " ").lower() if isinstance(col, str) else col for col in df.columns]
        print(f"Table {i+1} Columns: {df.columns.tolist()}")
    
    # Filter by keyword if provided
    if key_words:
        key_words_lower = key_words.lower()
        extracted_tables = [df for df in extracted_tables if 
                            any(key_words_lower in col for col in df.columns)]
    
    if not extracted_tables:
        print(f"No tables matched the keyword: {key_words}")
        return []
    
    # Apply table index filtering
    if table_index is not None and len(extracted_tables) > table_index:
        extracted_tables = [extracted_tables[table_index]]
    
    return extracted_tables

def _extract_from_pdf(pdf_path):
    """Extracts tables from a PDF file."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            extracted = page.extract_table()
            if extracted:
                df = pd.DataFrame(extracted[1:], columns=extracted[0])
                tables.append(df)
    return tables

def _extract_from_web(url):
    """Extracts tables from a webpage."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = []
        
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            data = [[cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])] for row in rows]
            if data:
                df = pd.DataFrame(data[1:], columns=data[0])
                tables.append(df)
        
        return tables
    
    except Exception as e:
        print(f"Error fetching webpage: {e}")
        return []

