# Trust Me — Review Intelligence Dataset

## 1. Dataset Overview


**Dataset:** Amazon Fake Reviews Dataset

**Source:** https://bretthollenbeck.com/fake-reviews-data/

**Dataset version:** March 2026 update

**Collection period:** 2019–2020

**Original format:** Compressed CSV (ZIP)

**Total reviews:** 381,734

**Total columns:** 23


This dataset supports the development and evaluation of the
Trust Me Review Intelligence Agent.

The dataset contains Amazon product reviews alongside
research-derived signals associated with seller-recruited
paid reviews.

These signals should not be interpreted as independently
verified review-level fraud labels.

## 2. Directory Structure

dataset/
├── raw/
│   └── public_reviews_dataset_cleaned.csv_.zip
├── processed/
└── README.md

Raw and processed datasets are excluded from Git tracking.

The original downloaded ZIP must remain unchanged.

## 3. Exploratory Data Analysis

### 3.1 Dataset Completeness

| Metric | Count |
|---|---:|
| Total reviews | 381,734 |
| Missing review text | 0 |
| Missing review IDs | 0 |
| Unique review IDs | 381,734 |
| Unique reviewers | 334,342 |
| Unique products | 3,389 |

### 3.2 Duplicate Analysis

| Metric | Count |
|---|---:|
| Duplicate review ID groups | 0 |
| Duplicate review text groups | 2,064 |
| Extra rows with repeated review text | 9,673 |

Duplicate text is measured after stripping leading and
trailing whitespace.

Repeated text does not automatically indicate a fake review.

### 3.3 Preliminary Label Analysis

Strategy A:

Candidate fake:
- Fake-review product classification = True
- Fake-reviewer classification = True
- Review rating = 5

Candidate genuine:
- Fake-review product classification = False
- Honest-reviewer classification = True

Strategy B:

Candidate fake:
- All Strategy A fake conditions
- reviewer_labeled_fake = 1.0

Candidate genuine:
- All Strategy A genuine conditions
- reviewer_labeled_honest = 1.0

| Category | Strategy A | Strategy B |
|---|---:|---:|
| Candidate fake | 52,209 | 20,378 |
| Candidate genuine | 15,013 | 9,524 |
| Total candidates | 67,222 | 29,902 |

Reviews not satisfying a strategy's conditions are treated
as unknown for that strategy, rather than automatically genuine.

These are provisional proxy-label strategies, not verified
ground truth.

### 3.4 Label Consistency

| Metric | Count |
|---|---:|
| Conflicting duplicate-text groups (Strategy A) | 89 |
| All rows in conflicting groups | 3,312 |
| Candidate fake rows within these groups | 164 |
| Candidate genuine rows within these groups | 537 |
| Unknown rows within these groups | 2,611 |

Identical review text can receive different candidate labels.

Therefore, review text alone may not be sufficient to infer
whether an individual review is fraudulent.

### 3.5 Reviewer and Product Grouping

| Metric | Count |
|---|---:|
| Reviewers with multiple reviews | 28,311 |
| Maximum reviews from one reviewer | 137 |
| Products with multiple reviews | 3,337 |
| Maximum reviews for one product | 2,251 |

Strategy A candidate fake reviews occur across 1,404 products.
Strategy A candidate genuine reviews occur across 1,554 products.

No product contains both candidate labels under these rules.
This separation follows from the label definitions, which
depend on product-level classification.

## 4. Provisional Training Policy

1. Preserve all original reviews and raw files.
2. Use Strategy A for the initial baseline experiment.
3. Use Strategy B for a separate label-sensitivity experiment.
4. Exclude unknown labels from supervised binary training.
5. Investigate conflicting identical-text groups before splitting.
6. Prefer product-grouped evaluation for unseen-product testing.
7. Check reviewer and exact-text overlap across partitions.
8. Fit text vectorizers only on training data.
9. Keep label-construction signals out of model input features.
10. Select the final model using performance, generalization,
    computational cost, and interpretability.

These decisions remain subject to validation during dataset
preparation and model evaluation.

## 5. Planned Models

- TF-IDF + Logistic Regression
- TF-IDF + Linear SVM
- Fine-tuned DistilBERT

Planned evaluation includes precision, recall, F1-score,
PR-AUC, confusion matrices, and inference performance.

Cross-domain evaluation will be investigated using an
independently sourced dataset. Differences in label definitions
must be documented.

## 6. Dataset Limitations

- Labels are derived from research evidence, rules, and classifiers.
- Product-level signals do not prove that every review is fake.
- Missing labels must not automatically be treated as genuine.
- Rule-derived and classifier-derived labels may be dependent.
- Amazon review language may not generalize to other platforms.
- Amazon removal observations after June 15, 2020 require
  caution because of the documented measurement limitation.
- Repeated text can occur in legitimate as well as suspicious reviews.

## 7. Reproducibility

EDA scripts are maintained in the experiments/ directory.

The dataset is stored locally and excluded from Git.
Future preprocessing must record its parameters, random seeds,
split assignments, and data-selection decisions.

## 8. Research References

He, S., Hollenbeck, B., Overgoor, G., Proserpio, D.,
& Tosyali, A. (2022).
Detecting fake review buyers using network structure:
Direct evidence from Amazon.
https://doi.org/10.1073/pnas.2211932119

He, S., Hollenbeck, B., & Proserpio, D. (2022).
The market for fake reviews.
https://doi.org/10.1287/mksc.2022.1353

Feldman, E., Tosyali, A., & Overgoor, G. (2025).
Addressing large-scale reviewer recruitment on Amazon:
A reviewer-centric approach to the fake review problem.
http://dx.doi.org/10.2139/ssrn.5156231

Hou, Y., Li, J., He, Z., Yan, A., Chen, X., & McAuley, J.
Bridging language and items for retrieval and recommendation.
https://doi.org/10.48550/arXiv.2403.03952
