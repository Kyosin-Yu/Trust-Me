# EXP-05 — Validation Error Analysis

## Objective

To analyze classification disagreements produced by the best-performing baseline model from EXP-03 and identify potential limitations associated with review length, predicted fake scores, and classification outcomes.

## Implementation

- **Base Model:** EXP-01 — TF-IDF + Logistic Regression
- **Threshold Reference:** EXP-03
- **Decision Threshold:** 0.60
- **Dataset:** `strategy_a_v1`
- **Training Reviews:** 46,564
- **Validation Reviews:** 9,938
- **Implementation Script:** `ml/analyze_validation_errors.py`
- **Test Dataset:** Not accessed

The experiment reused the existing Logistic Regression configuration and applied the previously selected decision threshold of 0.60.

The analysis examined:
- False Positive (FP) and False Negative (FN) classifications.
- Review length and its relationship with classification disagreements.
- Predicted fake-score intervals and their disagreement rates.
- Average review length and predicted fake score for each classification outcome.

The experiment generated `metrics.json`, `length_analysis.csv`, `score_analysis.csv`, and `outcome_analysis.csv`. A separate private file containing sampled review excerpts was excluded from Git tracking.

## Validation Results

| Metric | Result |
|---|---:|
| Accuracy | 0.8043 |
| Macro-F1 | 0.7049 |
| True Positive (TP) | 6,880 |
| True Negative (TN) | 1,113 |
| False Positive (FP) | 1,028 |
| False Negative (FN) | 917 |
| Total Disagreements | 1,945 |

### Quantitative Findings

- Reviews containing 1–10 words recorded the highest length-group disagreement rate of 34.80%.
- Reviews containing 61–120 words recorded the lowest length-group disagreement rate of 13.05%.
- The predicted fake-score interval of 0.40–0.60 recorded the highest score-group disagreement rate of 55.04%.
- False positives had an average fake score of 0.7781, indicating that some candidate genuine reviews received relatively high fake-class scores.
- False negatives averaged 35.10 words, compared with 59.69 words for true positives.
- The validation results successfully reproduced EXP-03's Accuracy of 0.8043 and Macro-F1 of 0.7049.

### Qualitative Findings

A qualitative inspection was conducted on 20 randomly sampled validation disagreements, consisting of 10 false positives (FP) and 10 false negatives (FN). The samples were selected using a fixed random seed of 42 to support reproducibility.

| Observed Characteristic | FP | FN |
|---|---|---|
| Generic or repetitive praise | Observed | Observed |
| Specific product details | Observed | Not observed |
| Mixed positive and negative sentiment | Observed | Not observed |
| Short or vague statements | Observed | Observed |
| Unusual or promotional language | Not observed | Observed |
| No additional identifiable pattern | — | Noted in inspection |

**Key Observations:**

- Generic or repetitive praise and short or vague statements were observed in both FP and FN samples.
- Specific product details and mixed sentiment were observed in FP samples, while unusual or promotional language was observed in FN samples.
- The observed characteristics varied between reviews, without establishing a single dominant error pattern.
- Source-text verification confirmed that 8 of the 20 sampled review excerpts (40%) were truncated by the 240-character export limit, including 4 false-positive and 4 false-negative samples. Therefore, some apparently incomplete excerpts resulted from the sampling procedure rather than incomplete original reviews. The completeness of the remaining source reviews was not independently assessed.

**Limitation:** These findings are exploratory and based on only 20 sampled disagreements. "Not observed" means the characteristic was not identified in the inspected samples, not that it never occurs in the full validation dataset. The recorded observations indicate presence rather than frequency.

## Conclusion

EXP-05 successfully reproduced the EXP-03 validation results, achieving an Accuracy of 0.8043 and a Macro-F1 score of 0.7049 using the selected decision threshold of 0.60.

The quantitative analysis identified higher disagreement rates among shorter reviews and predictions in the 0.40–0.60 fake-score interval. The qualitative inspection further indicated that classification disagreements occurred across multiple language characteristics, including generic praise, product-specific descriptions, mixed sentiment, and vague statements.

These findings highlight limitations of the text-only TF-IDF and Logistic Regression baseline. They support the need to interpret review classification outputs cautiously and to consider additional evidence when integrating results into the Review Intelligence Agent and Trust Reasoning Agent.

As the dataset relies on research-derived candidate labels rather than independently verified review authenticity, the findings represent disagreements with proxy labels and do not establish real-world fake-review detection accuracy.

**Status:** Completed — quantitative analysis, exploratory qualitative inspection, and excerpt-truncation verification.