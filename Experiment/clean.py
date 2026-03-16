from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RowKey:
    test: str
    question_id: str
    question_text: str
    prompt_varient: str


def _question_sort_key(question_id: str) -> tuple[int, str]:
    digits = "".join(ch for ch in question_id if ch.isdigit())
    if digits:
        return (int(digits), question_id)
    return (10**9, question_id)


def _load_model_columns(models_path: Path) -> tuple[list[str], dict[str, str]]:
    data = json.loads(models_path.read_text(encoding="utf-8"))
    display_names: list[str] = []
    id_to_display: dict[str, str] = {}
    seen: set[str] = set()

    for item in data:
        model_id = str(item.get("id", "")).strip()
        model_name = str(item.get("name", model_id)).strip() or model_id
        display = model_name
        if display in seen:
            display = f"{model_name} ({model_id})"
        seen.add(display)

        id_to_display[model_id] = display
        display_names.append(display)

    return display_names, id_to_display


def _choose_record(existing: dict[str, Any] | None, new: dict[str, Any]) -> dict[str, Any]:
    """Choose best record for same (prefix, model, test, question) key.

    Preference:
    1) successful response over null response
    2) if same success/null class, latest timestamp wins
    """
    if existing is None:
        return new

    old_ok = existing.get("response") is not None
    new_ok = new.get("response") is not None

    if new_ok and not old_ok:
        return new
    if old_ok and not new_ok:
        return existing

    old_ts = str(existing.get("timestamp", ""))
    new_ts = str(new.get("timestamp", ""))
    if new_ts >= old_ts:
        return new
    return existing


def _load_best_records(jsonl_path: Path) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    best: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                key = (
                    str(obj["instruction_prefix_version"]),
                    str(obj["model_id"]),
                    str(obj["test"]),
                    str(obj["question_id"]),
                )
                best[key] = _choose_record(best.get(key), obj)
            except Exception:
                continue

    return best


def _build_table(
    best_records: dict[tuple[str, str, str, str], dict[str, Any]],
    id_to_display: dict[str, str],
) -> dict[str, dict[RowKey, dict[str, str]]]:
    """Return test -> rowkey -> model_display -> response"""
    tables: dict[str, dict[RowKey, dict[str, str]]] = {}

    for (_, model_id, test, _), rec in best_records.items():
        prefix = str(rec.get("instruction_prefix_version", ""))
        question_id = str(rec.get("question_id", ""))
        question_text = str(rec.get("question_text", ""))
        response = rec.get("response")

        key = RowKey(
            test=test,
            question_id=question_id,
            question_text=question_text,
            prompt_varient=prefix,
        )

        model_col = id_to_display.get(model_id, model_id)
        tables.setdefault(test, {}).setdefault(key, {})[model_col] = "" if response is None else str(response)

    return tables


def _write_test_csv(
    output_path: Path,
    test_name: str,
    rows: dict[RowKey, dict[str, str]],
    model_columns: list[str],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["test", "question_id", "question_text", "prompt_varient", *model_columns]

    def row_sort_key(k: RowKey) -> tuple[str, tuple[int, str]]:
        return (k.prompt_varient, _question_sort_key(k.question_id))

    ordered_keys = sorted(rows.keys(), key=row_sort_key)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for k in ordered_keys:
            base = {
                "test": test_name,
                "question_id": k.question_id,
                "question_text": k.question_text,
                "prompt_varient": k.prompt_varient,
            }
            model_answers = rows[k]
            for m in model_columns:
                base[m] = model_answers.get(m, "")
            writer.writerow(base)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cleaned per-test CSV files from responses.jsonl")
    parser.add_argument(
        "--input",
        default="results/responses.jsonl",
        help="Path to input JSONL results file",
    )
    parser.add_argument(
        "--models",
        default="models.json",
        help="Path to models.json",
    )
    parser.add_argument(
        "--output_dir",
        default="results",
        help="Directory to write pct.csv, sap.csv, 8val.csv",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    input_path = (base_dir / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    models_path = (base_dir / args.models).resolve() if not Path(args.models).is_absolute() else Path(args.models)
    output_dir = (base_dir / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")
    if not models_path.exists():
        raise SystemExit(f"Models file not found: {models_path}")

    model_columns, id_to_display = _load_model_columns(models_path)
    best = _load_best_records(input_path)
    tables = _build_table(best, id_to_display)

    # Requested output names
    if "pct" in tables:
        _write_test_csv(
            output_path=output_dir / "pct.csv",
            test_name="pct",
            rows=tables["pct"],
            model_columns=model_columns,
        )

    sap_rows: dict[RowKey, dict[str, str]] = {}
    for sap_test in ("sap", "saply"):
        for k, v in tables.get(sap_test, {}).items():
            sap_rows[k] = v
    if sap_rows:
        _write_test_csv(
            output_path=output_dir / "sap.csv",
            test_name="saply",
            rows=sap_rows,
            model_columns=model_columns,
        )

    if "8val" in tables:
        _write_test_csv(
            output_path=output_dir / "8val.csv",
            test_name="8val",
            rows=tables["8val"],
            model_columns=model_columns,
        )

    print(f"Wrote cleaned CSV files to: {output_dir}")


if __name__ == "__main__":
    main()
