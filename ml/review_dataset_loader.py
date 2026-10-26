import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = (
    PROJECT_ROOT
    / "experiments"
    / "runs"
    / "EXP-01_logistic_regression"
    / "review_baseline_config.json"
)

def load_config(config_path=None):
    """Load baseline experiment configuration."""

    path = Path(config_path) if config_path else CONFIG_PATH

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = [
        "experiment_id",
        "dataset_version",
        "input_column",
        "target_column",
    ]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing config key: {key}")

    return config

def load_partition(name, config, *, allow_test=False):
    """Load and validate one ML dataset partition."""

    allowed_partitions = {"train", "validation"}

    if allow_test:
        allowed_partitions.add("test")

    if name not in allowed_partitions:
        raise ValueError(
            f"Partition '{name}' is not permitted. "
            "Test access must be explicitly enabled "
            "for final evaluation."
        )

    dataset_dir = (
        PROJECT_ROOT
        / "dataset"
        / "processed"
        / config["dataset_version"]
    )

    path = dataset_dir / f"{name}.csv"

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(
        path,
        dtype={
            "review_id": "string",
            "asin": "string",
            "reviewer_id": "string",
            "review_text": "string",
        },
        keep_default_na=False,
    )

    input_column = config["input_column"]
    target_column = config["target_column"]

    required_columns = {
        "review_id",
        "asin",
        input_column,
        target_column,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{name} missing columns: {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(f"{name} dataset is empty")

    if df[input_column].isna().any():
        raise ValueError(f"{name} contains missing review text")

    if df[input_column].str.strip().eq("").any():
        raise ValueError(f"{name} contains blank review text")

    labels = pd.to_numeric(
        df[target_column],
        errors="raise",
    )

    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError(
            f"{name} must contain only binary labels 0 and 1"
        )

    if df["review_id"].duplicated().any():
        raise ValueError(f"{name} contains duplicate review IDs")

    X = df[input_column].astype(str)
    y = labels.astype(int)

    return X, y, df


def main():
    config = load_config()

    print("=== REVIEW DATASET LOADER ===")
    print(f"Experiment: {config['experiment_id']}")

    for name in ("train", "validation"):
        X, y, df = load_partition(name, config)

        print(f"\n{name.upper()}")
        print(f"Reviews: {len(df):,}")
        print(f"Candidate fake (1): {(y == 1).sum():,}")
        print(f"Candidate genuine (0): {(y == 0).sum():,}")
        print(f"Blank inputs: {X.str.strip().eq('').sum():,}")
        print("Dataset validation: PASSED")

    print("\nReview dataset loader: PASSED")


if __name__ == "__main__":
    main()
