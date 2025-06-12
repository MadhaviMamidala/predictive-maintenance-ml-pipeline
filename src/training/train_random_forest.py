import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from pathlib import Path

# Load processed data
data_path = Path('data/processed/processed_data.csv')
df = pd.read_csv(data_path)

# Feature selection (drop non-numeric/categorical columns not useful for modeling)
features = ['volt', 'rotate', 'pressure', 'vibration', 'age']
# Convert categorical columns to numeric (if needed)
df['machineID'] = df['machineID'].astype('category').cat.codes
df['model'] = df['model'].astype('category').cat.codes
features += ['machineID', 'model']

# Target: Predict if there is a failure (binary classification: 1 if failure, else 0)
df['failure_flag'] = df['failure'].apply(lambda x: 0 if x == 'none' else 1)

y = df['failure_flag']
X = df[features]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train Random Forest
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features='sqrt',
    bootstrap=True,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Save model
output_dir = Path('models')
output_dir.mkdir(exist_ok=True)
model_path = output_dir / 'random_forest_model.joblib'
joblib.dump(model, model_path)
print(f"Model saved to {model_path}") 