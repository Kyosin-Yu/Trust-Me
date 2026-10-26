# Final Held-Out Test Evaluation — Review Intelligence Classifier

## 1. Objective

This evaluation assesses the selected Review Intelligence classifier on the reserved test partition after completing model development, validation-based selection and configuration freezing.

The objective is to measure classification performance and probability quality on held-out products without using test results for further model selection.

## 2. Implementation

The evaluation uses the configuration recorded in `experiments/model_selection/frozen_model_config.json`.

| Component | Configuration |
|---|---|
| Dataset | `strategy_a_v1` |
| Training Reviews | 46,564 |
| Test Reviews | 9,926 |
| Feature Extraction | TF-IDF (unigrams and bigrams) |
| Classifier | Logistic Regression |
| Calibration | Sigmoid |
| Calibration CV | 3-fold StratifiedGroupKFold |
| Calibration Seed | 42 |
| Classification Threshold | 0.65 |
| Primary Metric | Macro-F1 |
| Evaluation Script | `ml/evaluate_final_test.py` |

The classifier was trained using the original training partition. The held-out test partition was not used to fit the model or select its decision threshold.

## 3. Final Test Results

### 3.1 Classification Performance

| Metric | Result |
|---|---:|
| Accuracy | 0.785916 |
| Macro-F1 | 0.692986 |
| Candidate-Genuine Precision | 0.5028 |
| Candidate-Genuine Recall | 0.5472 |
| Candidate-Genuine F1 | 0.5241 |
| Candidate-Fake Precision | 0.8726 |
| Candidate-Fake Recall | 0.8514 |
| Candidate-Fake F1 | 0.8619 |

### 3.2 Confusion Matrix

Rows represent actual candidate labels and columns represent predicted candidate labels.

| Actual / Predicted | Candidate Genuine (0) | Candidate Fake (1) |
|---|---:|---:|
| Candidate Genuine (0) | 1,170 | 968 |
| Candidate Fake (1) | 1,157 | 6,631 |

The model identifies candidate-fake reviews more effectively than candidate-genuine reviews.

The classification errors indicate that the model should be used as one supporting evidence source rather than as a definitive review-authenticity detector.

### 3.3 Probability Quality

| Metric | Result |
|---|---:|
| Brier Score | 0.134661 |
| Log Loss | 0.429860 |
| Expected Calibration Error (10 bins) | 0.033945 |

These metrics assess probability quality relative to the research-derived candidate labels.

### 3.4 Validation–Test Comparison

| Metric | Validation | Final Test |
|---|---:|---:|
| Accuracy | 0.797344 | 0.785916 |
| Macro-F1 | 0.707114 | 0.692986 |
| Candidate-Genuine Recall | 0.562354 | 0.5472 |
| Candidate-Fake Recall | 0.861870 | 0.8514 |

The test Macro-F1 was approximately 0.0141 lower than the validation Macro-F1.

This relatively modest performance difference provides limited evidence of generalization to held-out products within the evaluated dataset. It does not establish generalization to other platforms or independently verified fraudulent reviews.

## 4. Dataset Integrity and Limitations

The final evaluation retained the original DEV-03 dataset partitions.

### Dataset Integrity Findings

| Check | Train/Test | Validation/Test |
|---|---:|---:|
| Product Overlap | 0 | 0 |
| Review ID Overlap | 0 | 0 |
| Original Exact-Stripped-Text Overlap | 0 | 0 |
| Casefolded Unique-Text Overlap | 9 | 4 |
| Affected Test Rows | 9 | 4 |

The original DEV-03 deduplication used exact-text comparison after removing leading and trailing whitespace.

A stricter case-insensitive audit identified residual overlaps. These remain a potential text-contamination risk because the selected TF-IDF vectorizer applies lowercase preprocessing.

The overlapping records were retained, and no test records were modified or removed after the issue was identified.

### Additional Limitations

- The dataset labels are research-derived proxies rather than independently verified fake-review ground truth.
- Reviewer overlap remains across dataset partitions.
- The model was selected using repeated evaluations of the same validation partition, which may introduce model-selection bias.
- Class imbalance and lower candidate-genuine recall remain important limitations.
- Performance on other e-commerce platforms and naturally occurring AI-generated reviews has not been established.
- The classifier's calibrated scores should not be presented as verified probabilities of review fraud.

## 5. Conclusion

The frozen sigmoid-calibrated TF-IDF Logistic Regression classifier achieved a final held-out test Macro-F1 of **0.692986** and accuracy of **0.785916**, using a decision threshold of **0.65**.

Test performance was slightly lower than validation performance, with stronger classification performance for candidate-fake reviews than candidate-genuine reviews.

The result supports using this classifier as a component of the Trust Me Review Intelligence Agent, while clearly communicating its limitations.

No threshold adjustment, model selection or test-based tuning was performed following the final evaluation.

**Evaluation Status:** Completed.

**Next Development Stage:** Model persistence, Review Intelligence inference pipeline and structured evidence generation.