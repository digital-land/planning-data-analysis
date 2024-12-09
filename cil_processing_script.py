import pandas as pd
import numpy as np

def cil_process(df, df_ref):
    # Define values to drop 
    doc_type_values_to_drop = [np.nan, 'OTHER']

    # Drop rows 
    df = df[~df["document type"].isin(doc_type_values_to_drop) & df["document type"].notna()]

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
    cil_df = df[df["document type"]=="CIL"]
    cil_df.to_csv('cil_dataset.csv', index=False)

    # Create and save IFS dataset
    ifs_df = df[df["document type"]=="IFS"]
    ifs_df.to_csv('ifs_dataset.csv', index=False)