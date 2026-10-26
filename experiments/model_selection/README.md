# Review Intelligence — Final Model Selection

## 1. Objective

This document records the selection of the Review Intelligence Agent's classification model before evaluating it on the held-out test dataset.

The purpose is to ensure that model selection is based on training and validation evidence rather than test performance.

## 2. Selected Model Configuration

| Component | Selected Configuration |
|---|---|
| Dataset | `strategy_a_v1` |
| Feature Extraction | TF-IDF (unigrams and bigrams, maximum 20,000 features) |
| Classification Algorithm | Logistic Regression |
| Regularization Parameter | C = 1.0 |
| Class Weighting | None |
| Probability Calibration | Sigmoid |
| Calibration Cross-Validation | 3-fold StratifiedGroupKFold |
| Calibration Grouping | Product identifier (`asin`) |
| Calibration Random Seed | 42 |
| Classification Threshold | 0.65 |
| Primary Selection Metric | Validation Macro-F1 |

The complete configuration is recorded in `frozen_model_config.json`.

## 3. Model Selection Rationale

EXP-00 through EXP-04 established and compared several baseline classification approaches.

EXP-03 identified threshold 0.60 as the best tested threshold for the uncalibrated Logistic Regression model, achieving a validation Macro-F1 of 0.704920.

EXP-05 investigated classification disagreements and identified challenges involving short reviews, ambiguous review language, and overlapping linguistic patterns.

EXP-06 introduced product-grouped sigmoid probability calibration. Calibration improved the Brier Score, Log Loss, and Expected Calibration Error compared with the uncalibrated baseline.

EXP-07 evaluated calibration sensitivity using three random seeds: 42, 123, and 2026. Probability-quality metrics improved under all three tested fold assignments, although Macro-F1 improvements were inconsistent.

EXP-08 evaluated 11 predefined thresholds for the calibrated classifier. Threshold 0.65 achieved the highest tested validation Macro-F1 of 0.707114.

The final configuration therefore retains the established TF-IDF and Logistic Regression architecture, applies sigmoid probability calibration, and selects threshold 0.65 under the predefined validation Macro-F1 criterion.

## 4. Validation Performance

| Metric | Selected Model |
|---|---:|
| Accuracy | 0.797344 |
| Macro-F1 | 0.707114 |
| Candidate-Genuine Recall | 0.562354 |
| Candidate-Fake Recall | 0.861870 |

The improvement over the uncalibrated EXP-03 Macro-F1 of 0.704920 is small. Accordingly, the selected configuration should not be described as substantially outperforming the uncalibrated model.

## 5. Evaluation Protocol

The following rules apply to the final held-out test evaluation:

1. The model architecture, calibration configuration, random seed, and classification threshold must be fixed before evaluating the test dataset.
2. The test dataset must not be used for model selection or threshold adjustment.
3. The test evaluation must reproduce the selected training and calibration procedure.
4. Accuracy, Macro-F1, class-specific precision, recall, F1-score, confusion matrix, and relevant probability-quality metrics should be reported.
5. Unexpected test results must be reported transparently rather than used to justify additional tuning.
6. Any later model revisions must be explicitly separated from this frozen evaluation.

## 6. Limitations

The model was trained and validated using research-derived candidate-authenticity labels rather than independently verified fake-review ground truth.

Products were separated across dataset partitions, but reviewer overlap remains a potential limitation.

Repeated use of the validation partition during experimentation may introduce model-selection bias.

Consequently, the model's predicted candidate-fake probabilities should not be interpreted as verified probabilities of actual review fraud.

## 7. Model Selection Status

**Selected configuration:** Sigmoid-calibrated TF-IDF Logistic