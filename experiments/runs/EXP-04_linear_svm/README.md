# EXP-04 — Linear Support Vector Machine

## Objective
Compare Linear SVM against the Logistic Regression baselines.

## Implementation
- Script: `ml/train_linear_svm.py`
- Model: TF-IDF + LinearSVC
- C: 1.0
- Class weighting: None
- Decision boundary: 0
- Dataset: strategy_a_v1
- Test: Not accessed

## Validation Results
- Accuracy: 0.7746
- Macro-F1: 0.6641
- Genuine recall: 0.4666
- Fake recall: 0.8592

## Conclusion
The initial Linear SVM configuration did not outperform EXP-03. Unlike EXP-03, this model was not threshold-tuned.
