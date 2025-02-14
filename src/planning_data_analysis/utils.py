import os

def save_to_csv(tables, output_folder):
    """Saves extracted tables to CSV files."""
    os.makedirs(output_folder, exist_ok=True)
    for idx, df in enumerate(tables):
        csv_filename = os.path.join(output_folder, f"filtered_table_{idx+1}.csv")
        df.to_csv(csv_filename, index=False)
        print(f"Table saved to {csv_filename}")