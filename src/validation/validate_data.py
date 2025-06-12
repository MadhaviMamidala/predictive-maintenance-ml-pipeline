import great_expectations as ge
import pandas as pd
from pathlib import Path
from great_expectations.validator.validator import Validator
from great_expectations.core.batch import Batch

# Path to processed data
data_path = Path('data/processed/processed_data.csv')

# Load data
print(f"Loading data from {data_path}...")
df = pd.read_csv(data_path)

# Create a Validator
validator = Validator(
    execution_engine=ge.execution_engine.PandasExecutionEngine(),
    batches=[Batch(data=df, batch_request=None, batch_definition=None, batch_spec=None, batch_markers=None)]
)

# Define expectations
print("Running data validation checks...")

# Check columns
expected_columns = [
    'datetime', 'machineID', 'volt', 'rotate', 'pressure', 'vibration',
    'errorID', 'failure', 'comp_maint', 'age', 'model'
]
validator.expect_table_columns_to_match_ordered_list(expected_columns)

# Check types
for col in ['volt', 'rotate', 'pressure', 'vibration', 'age']:
    validator.expect_column_values_to_be_of_type(col, 'float64')

validator.expect_column_values_to_not_be_null('datetime')
validator.expect_column_values_to_not_be_null('machineID')

# Check value ranges for sensors
sensor_ranges = {
    'volt': (100, 300),
    'rotate': (300, 500),
    'pressure': (50, 150),
    'vibration': (20, 80)
}
for col, (min_val, max_val) in sensor_ranges.items():
    validator.expect_column_values_to_be_between(col, min_value=min_val, max_value=max_val)

# Print validation results
results = validator.validate()
print("\nValidation Results:")
for res in results['results']:
    print(f"{res['expectation_config']['expectation_type']}: {res['success']}")

if results['success']:
    print("\nAll checks passed! Data is valid.")
else:
    print("\nSome checks failed. Please review the results above.") 