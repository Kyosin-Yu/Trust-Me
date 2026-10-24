# EXP-02 — Balanced Logistic Regression

## Objective
Evaluate the effect of class weighting on minority-class recognition.

## Implementation
- Script: `ml/train_baseline.py`
- Configuration: `config.json`
- Model: TF-IDF + Logistic Regression
- Class weighting: balanced
- Decision threshold: 0.50
- Dataset: strategy_a_v1
- Test: Not accessed

## Validation Results
- Accuracy: 0.7078
- Macro-F1: 0.6532
- Genuine recall: 0.7221
- Fake recall: 0.7039

## Conclusion
Balanced class weighting improves genuine recall but lowers overall Macro-F1 compared with EXP-01.
