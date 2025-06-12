import pandas as pd
from pathlib import Path

# Paths
input_path = Path('data/predictive_maintenance_full.csv')
output_dir = Path('data/processed')
output_dir.mkdir(exist_ok=True)
output_path = output_dir / 'processed_data.csv'

def clean_data(df):
    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    # Convert numeric columns
    for col in ['volt', 'rotate', 'pressure', 'vibration', 'age']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Fill missing values
    df['errorID'] = df['errorID'].fillna('none')
    df['failure'] = df['failure'].fillna('none')
    df['comp_maint'] = df['comp_maint'].fillna('none')
    df['model'] = df['model'].fillna('unknown')
    df['age'] = df['age'].fillna(df['age'].median())
    # Optionally, drop rows with critical missing values
    df = df.dropna(subset=['datetime', 'machineID'])
    return df

def main():
    print(f'Reading {input_path}...')
    df = pd.read_csv(input_path)
    print('Cleaning data...')
    df_clean = clean_data(df)
    print(f'Saving cleaned data to {output_path}...')
    df_clean.to_csv(output_path, index=False)
    print('Done!')

if __name__ == '__main__':
    main() 