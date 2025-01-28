import pandas as pd
import xgboost as xgb
import numpy as np
from active_features import FEATURES
import json
import os

# Ensure output directories exist
os.makedirs('train/model', exist_ok=True)
os.makedirs('train/data', exist_ok=True)

# Load training data
data = pd.read_csv('train/data/training_set.csv')
X = data[FEATURES]
y = data['relevance_grade']
groups = data['query_id']

# Prepare XGBoost training data
dtrain = xgb.DMatrix(X, label=y)
dtrain.set_group(groups.value_counts().sort_index().values)

# Train model
params = {
    'objective': 'rank:ndcg',
    'eval_metric': ['ndcg@5'],
    'eta': 0.1,                # Learning rate
    'max_depth': 6            # Maximum tree depth
}

model = xgb.train(
    params,
    dtrain,
    num_boost_round=100,
    evals=[(dtrain, 'train')],
    verbose_eval=10
)

# Save model in OpenSearch format
model_dump = model.get_dump(with_stats=False, dump_format='json')

# Save raw model dump
with open('train/model/model.json', 'w') as f:
    json.dump(model_dump, f, indent=2)

# Create OpenSearch model format - wrap the dumps in an array
opensearch_model = {
    "model": {
        "name": "xgboost_model",
        "model": {
            "type": "model/xgboost+json",
            "definition": "[" + ",".join(model_dump) + "]"  # Join all trees into array string
        }
    }
}

with open('train/model/os_model.json', 'w') as f:
    json.dump(opensearch_model, f, indent=2)

# Print feature importance
importance = model.get_score(importance_type='weight')
importance_df = pd.DataFrame(
    [(k, importance[k]) for k in importance],
    columns=['Feature', 'Importance']
).sort_values('Importance', ascending=False)

print("\nFeature Importance:")
print(importance_df)

# Optional: Plot feature importance
try:
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 6))
    plt.bar(importance_df['Feature'], importance_df['Importance'])
    plt.xticks(rotation=45, ha='right')
    plt.title('Feature Importance in LTR Model')
    plt.tight_layout()
    plt.savefig('train/data/feature_importance.png')
except ImportError:
    print("Matplotlib not installed - skipping plot generation")
