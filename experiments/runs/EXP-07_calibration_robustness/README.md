# EXP-07 — Calibration Robustness Evaluation

## Objective

To evaluate whether the probability-quality improvements observed in EXP-06 remain consistent across different product-grouped calibration fold assignments.

## Implementation

- **Base Model:** EXP-01 — TF-IDF + Logistic Regression
- **Reference Experiment:** EXP-06 — Probability Calibration
- **Calibration Method:** Sigmoid
- **Cross-Validation:** 3-fold StratifiedGroupKFold
- **Grouping Variable:** `asin` (Product ID)
- **Random Seeds:** 42, 123, 2026
- **Dataset:** `strategy_a_v1`
- **Training Reviews:** 46,564
- **Validation Reviews:** 9,938
- **Comparison Threshold:** 0.60
- **Implementation Script:** `ml/evaluate_calibration_robustness.py`
- **Test Dataset:** Not accessed

The uncalibrated baseline was fitted once using the training partition. Three sigmoid-calibrated models were then fitted using different product-grouped cross-validation assignments.

All nine calibration folds contained both candidate classes and maintained zero product overlap between their fitting and calibration subsets.

Each calibrated model was evaluated on the same validation partition using Brier Score, Log Loss, Expected Calibration Error (ECE), Accuracy, and Macro-F1.

## Validation Results

| Metric | Uncalibrated Baseline | Calibrated Mean | Standard Deviation | Improved Seeds |
|---|---:|---:|---:|---:|
| Brier Score ↓ | 0.133251 | 0.131652 | 0.000082 | 3/3 |
| Log Loss ↓ | 0.425433 | 0.421453 | 0.000195 | 3/3 |
| ECE (10 bins) ↓ | 0.037274 | 0.028947 | 0.001428 | 3/3 |
| Accuracy ↑ | 0.804287 | 0.814718 | 0.000868 | 3/3 |
| Macro-F1 ↑ | 0.704920 | 0.703945 | 0.002146 | 1/3 |

### Quantitative Findings

- Brier Score improved for all three calibration seeds, with a mean reduction of 0.001599.
- Log Loss improved for all three seeds, with a mean reduction of 0.003980.
- ECE improved for all three seeds, with a mean reduction of 0.008327.
- Accuracy increased across all three seeds at the fixed comparison threshold of 0.60.
- Macro-F1 improved only for seed 42 and decreased for seeds 123 and 2026.
- Seed 42 reproduced the EXP-06 calibrated results.
- All nine calibration folds passed product-overlap verification.

### Limitations

- Only three random seeds were evaluated.
- The same training and validation partitions were used in all runs.
- The experiment measures sensitivity to calibration-fold assignments, not performance across independent datasets.
- ECE depends on the selected binning procedure.
- The decision threshold of 0.60 was not re-optimized for each calibrated model.
- Dataset labels are research-derived authenticity candidates rather than independently verified fraud labels.
- Reviewer-level independence was not established, and the held-out test partition remains unused.

## Conclusion

EXP-07 demonstrated that sigmoid calibration consistently improved Brier Score, Log Loss, and Expected Calibration Error across the three evaluated product-grouped cross-validation assignments.

However, classification Macro-F1 did not consistently improve. Its mean value was slightly lower than that of the uncalibrated baseline at the fixed decision threshold of 0.60.

These findings suggest that sigmoid calibration provides modest, comparatively stable improvements in probability quality under the tested fold assignments, but additional evaluation is required before selecting the final classifier and decision threshold.

The calibrated scores remain estimates relative to research-derived candidate labels and should not be treated as independently verified probabilities of fraudulent reviews.

**Status:** Completed — calibration-fold sensitivity analysis.