# Trust Me — Review Intelligence Experiment Registry

**Project:** Trust Me — AI-Powered Product Trust Analysis and Decision Support Platform  
**Module:** Review Intelligence Agent  
**Dataset:** Strategy A v1.0  
**Development milestone:** DEV-04  
**Last updated:** 26 October 2026

## 1. Purpose

This registry provides a centralized record of machine learning experiments conducted for the Review Intelligence Agent.

Each experiment has a permanent identifier (EXP-XX) and records its objective, implementation, configuration, validation performance, and findings.

The primary evaluation metric is **Macro-F1**, which gives equal importance to both candidate classes.

All reported results below were obtained from the Validation partition. The held-out Test partition has not been accessed during model development.

## 2. Dataset Information

| Partition | Reviews |
|---|---:|
| Training | 46,564 |
| Validation | 9,938 |
| Testing (reserved) | 9,926 |
| Total | 66,428 |

Dataset characteristics:

- Product-disjoint and exact-text-disjoint partitions.
- Binary proxy labels: 0 = candidate genuine; 1 = candidate fake.
- Reviewer overlap remains across partitions.
- Candidate labels are derived from research dataset heuristics, not independently verified review authenticity.

## 3. Experiment Summary

| ID | Experiment | Accuracy | Macro-F1 | Genuine Recall | Fake Recall |
|---|---|---:|---:|---:|---:|
| EXP-00 | Majority-Class Baseline | 0.7846 | 0.4396 | 0.0000 | 1.0000 |
| EXP-01 | TF-IDF + Standard Logistic Regression | 0.8168 | 0.6800 | 0.3783 | 0.9372 |
| EXP-02 | TF-IDF + Balanced Logistic Regression | 0.7078 | 0.6532 | 0.7221 | 0.7039 |
| EXP-03 | Logistic Regression Threshold Analysis (0.60) | 0.8043 | **0.7049** | 0.5199 | 0.8824 |
| EXP-04 | TF-IDF + Linear SVM | 0.7746 | 0.6641 | 0.4666 | 0.8592 |

**Current leader:** EXP-03, based on Validation Macro-F1.

This is a provisional selection, not a final model deployment decision.

## 4. Individual Experiment Records

### EXP-00 — Majority-Class Baseline

- **Script:** `ml/evaluate_majority_baseline.py`
- **Method:** scikit-learn `DummyClassifier(strategy="most_frequent")`
- **Result:** Macro-F1 = 0.4396
- **Finding:** Always predicts candidate fake and cannot identify candidate-genuine reviews.

### EXP-01 — Standard Logistic Regression

- **Script:** `ml/train_baseline.py`
- **Configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Model:** TF-IDF + Logistic Regression, `class_weight=None`, threshold 0.50
- **Result:** Macro-F1 = 0.6800
- **Finding:** High candidate-fake recall but limited candidate-genuine recall.

### EXP-02 — Balanced Logistic Regression

- **Script:** `ml/train_baseline.py`
- **Configuration:** `experiments/runs/EXP-02_balanced_logistic_regression/review_baseline_config_2.json`
- **Model:** TF-IDF + Logistic Regression, `class_weight="balanced"`, threshold 0.50
- **Result:** Macro-F1 = 0.6532
- **Finding:** Candidate-genuine recall increased, but overall Macro-F1 declined compared with EXP-01.

### EXP-03 — Decision Threshold Analysis

- **Script:** `ml/evaluate_thresholds.py`
- **Base configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Method:** EXP-01 Logistic Regression with classification thresholds from 0.30 to 0.80, in increments of 0.05
- **Results file:** `experiments/reports/review_threshold_analysis_v1.csv`
- **Best tested threshold:** 0.60
- **Result:** Macro-F1 = 0.7049
- **Finding:** Threshold adjustment improved Macro-F1 without changing the learned classifier.

### EXP-04 — Linear SVM

- **Script:** `ml/train_linear_svm.py`
- **Base TF-IDF configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Model:** LinearSVC, C = 1.0, `class_weight=None`
- **Result:** Macro-F1 = 0.6641
- **Finding:** The initial Linear SVM configuration did not outperform EXP-03.

### EXP-05 — Validation Error Analysis

- **Objective:** Investigate classification disagreements from the selected EXP-03 baseline and identify potential model limitations.
- **Implementation:** `ml/analyze_validation_errors.py`
- **Base configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Decision threshold:** 0.60 (selected in EXP-03)
- **Dataset:** `strategy_a_v1` — validation partition (9,938 reviews)
- **Accuracy:** 0.8043
- **Macro-F1:** 0.7049
- **False Positives:** 1,028
- **False Negatives:** 917
- **Total Disagreements:** 1,945
- **Key Findings:** Short reviews exhibited higher disagreement rates, while the 0.40–0.60 fake-score interval recorded the highest score-group disagreement rate (55.04%).
- **Conclusion:** The analysis identified limitations of text-only review classification. Results represent disagreements with research-derived candidate labels, not independently verified authenticity errors.
- **Status:** Completed — quantitative analysis, exploratory qualitative inspection, and excerpt-truncation verification.
- **Experiment Folder:** `experiments/runs/EXP-05_error_analysis/`

### EXP-06 — Probability Calibration

- **Objective:** Evaluate whether sigmoid calibration improves the probability quality of the existing TF-IDF and Logistic Regression baseline.
- **Implementation:** `ml/evaluate_probability_calibration.py`
- **Base Configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Calibration Method:** Sigmoid
- **Cross-Validation:** 3-fold StratifiedGroupKFold, grouped by `asin`
- **Dataset:** `strategy_a_v1` — 46,564 training and 9,938 validation reviews
- **Brier Score:** 0.133251 → 0.131561
- **Log Loss:** 0.425433 → 0.421229
- **ECE (10 bins):** 0.037274 → 0.028313
- **Accuracy:** 0.804287 → 0.813946
- **Macro-F1:** 0.704920 → 0.705708
- **Conclusion:** Sigmoid calibration modestly improved validation probability quality, although some reliability intervals deteriorated.
- **Status:** Completed
- **Experiment Folder:** `experiments/runs/EXP-06_probability_calibration/`

### EXP-07 — Calibration Robustness Evaluation

- **Objective:** Evaluate calibration sensitivity across different product-grouped fold assignments.
- **Implementation:** `ml/evaluate_calibration_robustness.py`
- **Base Configuration:** `experiments/runs/EXP-01_logistic_regression/review_baseline_config.json`
- **Calibration Reference:** EXP-06
- **Calibration Method:** Sigmoid
- **Cross-Validation:** 3-fold StratifiedGroupKFold grouped by `asin`
- **Random Seeds:** 42, 123, 2026
- **Dataset:** `strategy_a_v1` — 46,564 training and 9,938 validation reviews
- **Mean Brier Score:** 0.131652
- **Mean Log Loss:** 0.421453
- **Mean ECE (10 bins):** 0.028947
- **Mean Accuracy:** 0.814718
- **Mean Macro-F1:** 0.703945
- **Key Finding:** Probability-quality metrics improved across all three seeds, whereas Macro-F1 improved in only one.
- **Conclusion:** Sigmoid calibration showed modest improvements in probability quality under the tested fold assignments, without consistent classification gains.
- **Status:** Completed
- **Experiment Folder:** `experiments/runs/EXP-07_calibration_robustness/`

## 5. Experiment Status

| Experiment | Status |
|---|---|
| EXP-00 — Majority-Class Baseline | Completed |
| EXP-01 — Standard Logistic Regression | Completed |
| EXP-02 — Balanced Logistic Regression | Completed |
| EXP-03 — Decision Threshold Analysis | Completed |
| EXP-04 — Linear SVM | Completed |
| EXP-05 — Validation Error Analysis | Completed |
| EXP-06 — Probability Calibration | Completed |
| EXP-07 — Calibration Robustness Evaluation | Completed |

## 6. Experimental Controls and Limitations

All experiments used the same Strategy A v1.0 Training and Validation datasets.

The principal model experiments used text-only TF-IDF features. No product ID, reviewer ID, or label-derived metadata was included in the classifier input.

EXP-03 used the same underlying model configuration as EXP-01, changing only the classification threshold. EXP-04 used its default SVM decision boundary and was not threshold-tuned, so the comparison does not establish which algorithm is inherently superior.

Repeated selection using Validation results may introduce model-selection bias. Therefore, the held-out Test dataset must only be used after finalizing the model and operating threshold.

## 7. Future Experiment Record Requirements

For every new experiment, record:

- Experiment ID and objective.
- Dataset version.
- Script path and configuration.
- Parameters changed compared with previous experiments.
- Validation metrics and confusion matrix.
- Results or artifact locations.
- Findings, limitations, and follow-up decision.
- Git commit reference when available.

## 8. Current Engineering Decision

EXP-03 remains the provisional classification baseline based on Validation Macro-F1 of 0.7049 at the selected threshold of 0.60.

EXP-06 demonstrated modest improvements in probability-quality metrics following sigmoid calibration. EXP-07 further showed that improvements in Brier Score, Log Loss, and Expected Calibration Error were consistent across three product-grouped calibration-fold assignments.

However, Macro-F1 did not consistently improve after calibration. Therefore, the calibrated model has not yet been selected as the final review classifier.

The next priority is to evaluate classification-threshold behavior for the calibrated model and establish a defensible model-selection decision before conducting final held-out test evaluation.

All reported findings remain specific to research-derived candidate labels and do not establish verified fake-review detection accuracy.