import pandas as pd
import numpy as np
import os

def create_sample_csv():
    np.random.seed(42) # For reproducibility
    
    # Scenario: Continuous variable (e.g., Average Margin)
    # Control: Mean 100, StdDev 15
    # Treatment: Mean 106, StdDev 15 (A 6% lift)
    
    n = 200 # Sample size per group
    
    control = np.random.normal(100, 15, n)
    treatment = np.random.normal(106, 15, n)
    
    data = pd.DataFrame({
        'unit_id': range(1, (n*2) + 1),
        'group': ['control'] * n + ['treatment'] * n,
        'margin': np.concatenate([control, treatment])
    })
    
    os.makedirs('docs/raw', exist_ok=True)
    data.to_csv('docs/raw/sample_test_data.csv', index=False)
    print("Created docs/raw/sample_test_data.csv")

if __name__ == "__main__":
    create_sample_csv()