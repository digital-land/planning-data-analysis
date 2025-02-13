import pandas as pd
import numpy as np

def cil_process(df, df_ref):
        """
    Processes a dataset containing information on Community Infrastructure Levy (CIL) and 
    Infrastructure Funding Statements (IFS), cleaning the data, handling missing values, 
    and mapping local authority codes before saving separate datasets for CIL and IFS.

    Parameters:
    ----------
    df : pandas.DataFrame
        The main dataset containing CIL and IFS documents with associated metadata.
    
    df_ref : pandas.DataFrame
        A reference dataset mapping local authority codes to their official names.

    Processing Steps:
    ----------------
    - Drops rows where 'document-type' or 'document-url' contain NaN or "OTHER".
    - Removes rows where 'adopted-date' is "No CIL".
    - Replaces instances of `None` and "Cannot find a page" with an empty string.
    - Standardises 'adopted-date' by replacing "N/A" and `None` with an empty string.
    - Moves "On hold" or "In Discussion" values from 'adopted-date' to 'notes' and sets 'adopted-date' to an empty string.
    - Extracts relevant columns from `df_ref` for mapping.
    - Extracts organisation codes and maps them using local authority reference data.
    - Updates the 'organisation' column with mapped local authority codes, prefixed with "local-authority:".
    - Drops redundant columns after merging.
    - Saves cleaned CIL and IFS datasets separately as CSV files.

    Outputs:
    -------
    - Saves `cil_dataset.csv` containing rows where 'document-type' is "CIL".
    - Saves `ifs_dataset.csv` containing rows where 'document-type' is "IFS".
    """
        
    # Define values to drop 
    doc_type_values_to_drop = [np.nan, 'OTHER']

    # Drop rows 
    df = df[~df["document-type"].isin(doc_type_values_to_drop) & df["document-type"].notna()]
    df = df[~df["document-url"].isin(doc_type_values_to_drop) & df["document-url"].notna()]
    
    # Drop rows where the value in any column is "No CIL"
    df = df[df["adopted-date"] != "No CIL"]

    # Strip `None` and "Cannot find a page", leaving cells blank
    df = df.replace([None, "Cannot find a page"], "")

    # Set `adopted-date` to blank if it contains "N/A" or is None
    df['adopted-date'] = df['adopted-date'].replace(["N/A", None], "")

    # Copy "On hold" or "In Discussion" to `notes` and set `adopted-date` to blank
    mask = df['adopted-date'].isin(['On hold', 'In Discussion'])
    df.loc[mask, 'notes'] = df.loc[mask, 'adopted-date']
    df.loc[mask, 'adopted-date'] = ""

    # Only select relevant columns from df_ref
    df_ref = df_ref[["local-authority-code", "official-name"]]

    # Extract the codes from both df0 and df1
    df['org_code'] = df['organisation']
    df_ref['org_code'] = df_ref['official-name']

    # Perform a left merge and replace organisation with extracted 3-letter codes
    df = pd.merge(df, df_ref, on='org_code', how='left')
    df['organisation'] = df['local-authority-code']

    # Prepend 'local-authority:' to each entry in the 'organisation' column
    df['organisation'] = "local-authority: " + df['organisation']

    # Drop reduntant columns
    df = df.drop(columns=['local-authority-code', 'official-name', 'org_code'])

    # Create and save CIL dataset
    cil_df = df[df["document-type"]=="CIL"]
    cil_df.to_csv('cil_dataset.csv', index=False)

    # Create and save IFS dataset
    ifs_df = df[df["document-type"]=="IFS"]
    ifs_df.to_csv('ifs_dataset.csv', index=False)


# Load dataset and function invoking
#df = pd.read_csv("CIL_schedule_documents - Sheet1.csv")
# Load the organisation reference data
#df_ref = pd.read_csv("C:/Users/DanielGodden/Documents/planning_data/local_plan_data_collection/documents/uk_local_authorities_future.csv")

#cil_process(df, df_ref)

