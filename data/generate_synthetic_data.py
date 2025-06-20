import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

n_rows = 200
np.random.seed(42)

# Generate columns
start_date = datetime(2023, 1, 1)
datetimes = [start_date + timedelta(hours=i) for i in range(n_rows)]
machineIDs = np.random.randint(1, 11, size=n_rows)
volt = np.random.normal(220, 20, n_rows).round(2)
rotate = np.random.normal(1500, 100, n_rows).round(2)
pressure = np.random.normal(100, 10, n_rows).round(2)
vibration = np.random.normal(40, 5, n_rows).round(2)
errorIDs = np.random.choice(['none', 'E1', 'E2', 'E3', 'E4'], size=n_rows, p=[0.7, 0.1, 0.1, 0.05, 0.05])
failures = np.random.choice(['none', 'comp1', 'comp2', 'comp3', 'comp4'], size=n_rows, p=[0.85, 0.05, 0.04, 0.03, 0.03])
comp_maint = np.random.choice(['none', 'comp1', 'comp2', 'comp3', 'comp4'], size=n_rows, p=[0.8, 0.07, 0.05, 0.04, 0.04])
age = np.random.randint(1, 20, n_rows)
models = np.random.choice(['A', 'B', 'C', 'D'], size=n_rows)

data = pd.DataFrame({
    'datetime': datetimes,
    'machineID': machineIDs,
    'volt': volt,
    'rotate': rotate,
    'pressure': pressure,
    'vibration': vibration,
    'errorID': errorIDs,
    'failure': failures,
    'comp_maint': comp_maint,
    'age': age,
    'model': models
})

# Save to CSV
output_path = 'data/predictive_maintenance_full.csv'
data.to_csv(output_path, index=False)
print(f"Synthetic dataset with {n_rows} rows saved to {output_path}") 