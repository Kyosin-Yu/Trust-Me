# EXP-08 — Calibrated Classification Threshold Evaluation

## Objective

To evaluate the effect of classification thresholds on the sigmoid-calibrated Logistic Regression model and identify a provisional threshold based on validation Macro-F1 and class-specific recall.

## Implementation

- **Base Model:** EXP-01 — TF-IDF + Logistic Regression
- **Calibration Reference:** EXP-06
- **Calibration Method:** Sigmoid
- **Cross-Validation:** 3-fold StratifiedGroupKFold grouped by `asin`
- **Random Seed:** 42
- **Dataset:** `strategy_a_v1`
- **Training Reviews:** 46,564
- **Validation Reviews:** 9,938
- **Threshold Range:** 0.30–0.80, increments of 0.05
- **Primary Selection Metric:** Validation Macro-F1
- **Tie-Breaking Rule:** Lower threshold
- **Implementation Script:** `ml/evaluate_calibrated_thresholds.py`
- **Test Dataset:** Not accessed

The calibrated classifier was fitted once using the training partition. Its validation probabilities were evaluated against 11 predefined classification thresholds without retraining the model for each threshold.

All three calibration folds maintained zero overlapping products between their fitting and calibration subsets.

## Validation Results

| Metric | Calibrated Threshold 0.60 | Calibrated Threshold 0.65 |
|---|---:|---:|
| Accuracy | 0.813946 | 0.797344 |
| Macro-F1 | 0.705708 | **0.707114** |
| Candidate Genuine Recall | 0.481551 | **0.562354** |
| Candidate Fake Recall | **0.905220** | 0.861870 |

### Quantitative Findings

- Threshold 0.65 achieved the highest validation Macro-F1 of 0.707114 among the 11 predefined thresholds.
- Increasing the threshold from 0.60 to 0.65 improved candidate-genuine recall while reducing candidate-fake recall.
- Accuracy decreased from 0.813946 to 0.797344.
- The Macro-F1 improvement was small, with an absolute increase of 0.001406.
- Threshold 0.60 reproduced the classification performance recorded in EXP-06.
- All three calibration folds maintained zero product overlap.

### Limitations

- Threshold selection was performed on the validation partition, which has also been used in previous experiments.
- Repeated validation-based model selection may introduce optimistic performance estimates.
- The experiment evaluated a predefined threshold grid rather than every possible threshold.
- The chosen threshold has not been evaluated on the held-out test partition.
- Research-derived candidate labels are not independently verified review-authenticity ground truth.
- The threshold was selected using Macro-F1 and does not represent an application-specific risk or cost optimization.

## Conclusion

EXP-08 identified 0.65 as the provisional classification threshold for the sigmoid-calibrated Logistic Regression model based on the highest Macro-F1 among the tested thresholds.

Compared with threshold 0.60, the selected threshold improved candidate-genuine recall but reduced candidate-fake recall and overall accuracy. The improvement in Macro-F1 was marginal.

The results highlight the importance of considering class-specific recall alongside aggregate metrics when designing the Review Intelligence Agent.

The selected threshold remains provisional until the model configuration is frozen and final evaluation is conducted on the reserved test partition. All findings remain specific to research-derived candidate labels.

**Status:** Completed — validation threshold analysis.