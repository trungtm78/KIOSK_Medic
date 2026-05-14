"""
Train syndrome classifier using sentence-transformer embeddings + logistic regression, and export to ONNX.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import List

import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def read_dataset(path: Path) -> List[dict]:
    samples: List[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            samples.append(json.loads(line))
    return samples


def train(
    data_path: Path,
    output_dir: Path,
    model_name: str = "AITeamVN/Vietnamese_Embedding",
    test_size: float = 0.2,
    random_state: int = 42,
) -> None:
    samples = read_dataset(data_path)
    if not samples:
        raise ValueError(f"No samples found in {data_path}")

    texts = [item["text"] for item in samples]
    syndromes = [item["syndrome_id"] for item in samples]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(syndromes)

    model = SentenceTransformer(model_name)
    X = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    clf = LogisticRegression(
        max_iter=2000,
        multi_class="multinomial",
        class_weight="balanced",
        solver="lbfgs",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(
        y_test,
        y_pred,
        target_names=label_encoder.classes_,
        digits=3,
    )
    print("=== Classification report ===")
    print(report)

    output_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(clf, output_dir / "syndrome_classifier.joblib")
    (output_dir / "label_encoder.json").write_text(
        json.dumps({"classes": label_encoder.classes_.tolist()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "config.json").write_text(
        json.dumps(
            {
                "model_name": model_name,
                "data_path": str(data_path),
                "trained_at": datetime.utcnow().isoformat(),
                "n_samples": len(samples),
                "classes": label_encoder.classes_.tolist(),
                "test_size": test_size,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    initial_type = [("input", FloatTensorType([None, X.shape[1]]))]
    onnx_model = convert_sklearn(clf, initial_types=initial_type)
    with (output_dir / "syndrome_classifier.onnx").open("wb") as f:
        f.write(onnx_model.SerializeToString())

    print(f"Model and artifacts saved to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train syndrome classifier and export to ONNX")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("chat-service/data/syndrome_training_examples.jsonl"),
        help="Path to JSONL training data",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("chat-service/models/syndrome_classifier"),
        help="Directory to store trained artifacts",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="AITeamVN/Vietnamese_Embedding",
        help="SentenceTransformer model name",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)

    args = parser.parse_args()
    train(
        data_path=args.data,
        output_dir=args.output_dir,
        model_name=args.model_name,
        test_size=args.test_size,
        random_state=args.random_state,
    )


if __name__ == "__main__":
    main()
