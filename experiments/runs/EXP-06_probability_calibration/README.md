# EXP-06 — Probability Calibration

## Objective

To evaluate whether sigmoid calibration improves the reliability of predicted candidate-fake probabilities produced by the existing TF-IDF and Logistic Regression baseline model.

## Implementation

- **Base Model:** EXP-01 — TF-IDF + Logistic Regression
- **Calibration Method:** Sigmoid (Platt Scaling)
- **Cross-Validation:** 3-fold StratifiedGroupKFold
- **Grouping Variable:** `asin` (Product ID)
- **Random Seed:** 42
- **Dataset:** `strategy_a_v1`
- **Training Reviews:** 46,564
- **Validation Reviews:** 9,938
- **Comparison Threshold:** 0.60 (referenced from EXP-03)
- **Implementation Script:** `ml/evaluate_probability_calibration.py`
- **Test Dataset:** Not accessed

The calibration model was trained using product-disjoint cross-validation folds within the training partition. All three folds contained both candidate classes and had zero overlapping products between the model-fitting and calibration subsets.

The original uncalibrated baseline was compared with the sigmoid-calibrated model using Brier Score, Log Loss, Expected Calibration Error (ECE), Accuracy, and Macro-F1.

The 0.60 decision threshold was retained for comparison purposes and was not re-optimized for the calibrated model.

## Validation Results

| Metric | Uncalibrated | Sigmoid Calibrated |
|---|---:|---:|
| Brier Score ↓ | 0.133251 | **0.131561** |
| Log Loss ↓ | 0.425433 | **0.421229** |
| ECE (10 bins) ↓ | 0.037274 | **0.028313** |
| Accuracy ↑ | 0.804287 | **0.813946** |
| Macro-F1 ↑ | 0.704920 | **0.705708** |

### Quantitative Findings

- Sigmoid calibration reduced the Brier Score from 0.133251 to 0.131561.
- Log Loss decreased from 0.425433 to 0.421229.
- ECE decreased from 0.037274 to 0.028313, representing approximately 24.0% relative improvement.
- Accuracy increased from 0.804287 to 0.813946 at the fixed threshold of 0.60.
- Macro-F1 increased slightly from 0.704920 to 0.705708.
- Seven of the ten reliability intervals showed smaller absolute calibration gaps, while three showed larger gaps.
- The calibrated model showed its largest bin-level deterioration in the 0.20–0.30 predicted fake-score interval.

### Limitations

- The results are based on research-derived candidate labels rather than independently verified review authenticity.
- ECE depends on the number and boundaries of the probability bins.
- Individual reliability bins contain different numbers of reviews, and the models may assign different reviews to the same bin.
- Product-level separation was maintained during calibration, but reviewer-level independence was not established.
- The calibrated model has not yet been evaluated on the held-out test partition or an independent external dataset.
- Improved calibration against candidate labels does not establish the true probability that a review is fraudulent.

## Conclusion

EXP-06 demonstrated that sigmoid calibration produced modest improvements in validation probability quality compared with the uncalibrated TF-IDF and Logistic Regression baseline.

All three probability-quality metrics—Brier Score, Log Loss, and ECE—improved after calibration. Accuracy also increased at the fixed comparison threshold, while Macro-F1 improved only slightly.

Although the results support retaining sigmoid calibration as a candidate enhancement to the Review Intelligence Agent, the calibrated outputs remain estimates relative to research-derived candidate labels. They should not be interpreted as verified fraud probabilities or as the final Trust Me Confidence Level.

Further evaluation is required before selecting the calibrated model for system integration.

**Status:** Completed — validation calibration analysis.