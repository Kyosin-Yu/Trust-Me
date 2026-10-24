# EXP-03 — Logistic Regression Threshold Analysis

## Objective
Find a decision threshold that improves validation Macro-F1.

## Implementation
- Script: `ml/evaluate_thresholds.py`
- Base configuration: EXP-01
- Threshold search: 0.30 to 0.80, step 0.05
- Results: `threshold_results.csv`
- Dataset: strategy_a_v1
- Test: Not accessed

## Validation Results
- Best tested threshold: 0.60
- Accuracy: 0.8043
- Macro-F1: 0.7049
- Genuine recall: 0.5199
- Fake recall: 0.8824

## Conclusion
Threshold 0.60 achieved the highest Macro-F1 among the evaluated thresholds. This is the current provisional leading configuration.
