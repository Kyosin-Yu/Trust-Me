# EXP-00 — Majority-Class Baseline

## Objective
Establish a non-learning reference for candidate-review classification.

## Implementation
- Script: `ml/evaluate_majority_baseline.py`
- Model: DummyClassifier(strategy="most_frequent")
- Dataset: strategy_a_v1
- Training: 46,564 reviews
- Validation: 9,938 reviews
- Test: Not accessed

## Validation Results
- Accuracy: 0.7846
- Macro-F1: 0.4396
- Candidate-genuine recall: 0.0000
- Candidate-fake recall: 1.0000

## Conclusion
The classifier always predicts candidate fake. Accuracy alone is insufficient for model selection.
