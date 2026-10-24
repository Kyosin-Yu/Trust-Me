# EXP-01 — Standard Logistic Regression

## Objective
Establish the first text-based machine learning baseline.

## Implementation
- Script: `ml/train_baseline.py`
- Configuration: `config.json`
- Model: TF-IDF + Logistic Regression
- Class weighting: None
- Decision threshold: 0.50
- Dataset: strategy_a_v1
- Test: Not accessed

## Validation Results
- Accuracy: 0.8168
- Macro-F1: 0.6800
- Genuine recall: 0.3783
- Fake recall: 0.9372

## Conclusion
The classifier improves Macro-F1 over the majority baseline but has limited candidate-genuine recall.
