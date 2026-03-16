from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
from typing import Iterable


@dataclass(frozen=True)
class ModelConfig:
    id: str
    name: str
    description: str = ""


@dataclass(frozen=True)
class InstructionPrefix:
    id: str
    text: str


@dataclass(frozen=True)
class QuestionRecord:
    test: str
    question_id: str
    question_text: str


@dataclass(frozen=True)
class ExperimentTask:
    instruction_prefix_version: str
    instruction_prefix_text: str
    model_id: str
    test: str
    question_id: str
    question_text: str

    def unique_key(self) -> tuple[str, str, str, str]:
        return (
            self.instruction_prefix_version,
            self.model_id,
            self.test,
            self.question_id,
        )



def load_models(path: Path) -> list[ModelConfig]:
    data = json.loads(path.read_text(encoding="utf-8"))
    models: list[ModelConfig] = []
    for item in data:
        models.append(
            ModelConfig(
                id=str(item["id"]).strip(),
                name=str(item.get("name", item["id"])).strip(),
                description=str(item.get("description", "")).strip(),
            )
        )
    return models



def load_instruction_prefixes(path: Path) -> list[InstructionPrefix]:
    data = json.loads(path.read_text(encoding="utf-8"))
    prefixes = data.get("instruction_prefixes", [])
    records: list[InstructionPrefix] = []
    for item in prefixes:
        records.append(InstructionPrefix(id=str(item["id"]).strip(), text=str(item["text"]).strip()))
    return records



def _test_name_from_file(file_path: Path) -> str:
    stem = file_path.stem
    if stem.endswith("_ques"):
        return stem[: -len("_ques")]
    return stem



def load_questions(questions_dir: Path) -> list[QuestionRecord]:
    records: list[QuestionRecord] = []
    for csv_path in sorted(questions_dir.glob("*.csv")):
        test = _test_name_from_file(csv_path)
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                qid = str(row["question_id"]).strip()
                qtext = str(row["question_text"]).strip()
                records.append(QuestionRecord(test=test, question_id=qid, question_text=qtext))
    return records



def build_tasks(
    models: Iterable[ModelConfig],
    prefixes: Iterable[InstructionPrefix],
    questions: Iterable[QuestionRecord],
) -> list[ExperimentTask]:
    tasks: list[ExperimentTask] = []
    for prefix in prefixes:
        for model in models:
            for question in questions:
                tasks.append(
                    ExperimentTask(
                        instruction_prefix_version=prefix.id,
                        instruction_prefix_text=prefix.text,
                        model_id=model.id,
                        test=question.test,
                        question_id=question.question_id,
                        question_text=question.question_text,
                    )
                )
    return tasks



def load_completed_keys(responses_file: Path) -> set[tuple[str, str, str, str]]:
    completed: set[tuple[str, str, str, str]] = set()
    if not responses_file.exists():
        return completed

    with responses_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if obj.get("response") is None:
                    continue
                key = (
                    str(obj["instruction_prefix_version"]),
                    str(obj["model_id"]),
                    str(obj["test"]),
                    str(obj["question_id"]),
                )
                completed.add(key)
            except Exception:
                # Keep scanning even if one line is malformed.
                continue
    return completed


def load_unresolved_failed_keys(responses_file: Path) -> set[tuple[str, str, str, str]]:
    """Return task keys that currently have failures and no successful completion.

    This scans JSONL in order. Any later success for a key clears prior failure state.
    """
    unresolved_failed: set[tuple[str, str, str, str]] = set()
    if not responses_file.exists():
        return unresolved_failed

    with responses_file.open("r", encoding="utf-8") as f:
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
                if obj.get("response") is None:
                    unresolved_failed.add(key)
                else:
                    unresolved_failed.discard(key)
            except Exception:
                continue

    return unresolved_failed
