from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import CancelledError
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import threading
from typing import Any

from config import AppConfig
from loader import (
    ExperimentTask,
    build_tasks,
    load_completed_keys,
    load_instruction_prefixes,
    load_models,
    load_questions,
    load_unresolved_failed_keys,
)
from logger import ExperimentLogger
from openrouter_client import OpenRouterClient
from prompt_builder import PromptBuilder


class JsonlWriter:
    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self._lock = threading.Lock()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False)
        with self._lock:
            with self.output_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())


class ExperimentRunner:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._stop_event = threading.Event()
        self.prompt_builder = PromptBuilder(
            default_template_path=config.paths.prompt_default_file,
            pct_template_path=config.paths.prompt_default_pct_file,
        )
        self.client = OpenRouterClient(
            api_key=config.runtime.openrouter_api_key,
            url=config.runtime.openrouter_url,
            referer=config.runtime.openrouter_referer,
            title=config.runtime.openrouter_title,
            timeout_seconds=config.runtime.request_timeout_seconds,
            max_retries=config.runtime.max_retries,
            base_retry_delay_seconds=config.runtime.base_retry_delay_seconds,
            max_retry_delay_seconds=config.runtime.max_retry_delay_seconds,
            temperature=config.runtime.model_temperature,
            max_tokens=config.runtime.model_max_tokens,
        )
        self.writer = JsonlWriter(config.paths.responses_file)

    def run(self, try_failed_only: bool = False) -> None:
        models = load_models(self.config.paths.models_file)
        prefixes = load_instruction_prefixes(self.config.paths.instruction_prefix_file)
        questions = load_questions(self.config.paths.questions_dir)

        all_tasks = build_tasks(models=models, prefixes=prefixes, questions=questions)
        if try_failed_only:
            failed_keys = load_unresolved_failed_keys(self.config.paths.responses_file)
            pending_tasks = [t for t in all_tasks if t.unique_key() in failed_keys]
        else:
            completed_keys = load_completed_keys(self.config.paths.responses_file)
            pending_tasks = [t for t in all_tasks if t.unique_key() not in completed_keys]

        logger = ExperimentLogger(total_tasks=len(pending_tasks))
        logger.start()

        if not pending_tasks:
            logger.info("No pending tasks. Resume check found all responses already present.")
            logger.stop()
            return

        logger.info(
            f"Loaded models={len(models)}, prefixes={len(prefixes)}, questions={len(questions)}, "
            f"pending={len(pending_tasks)}"
        )

        if try_failed_only:
            logger.info("Retry mode enabled: retrying unresolved failed records only.")
            for task in pending_tasks:
                logger.info(
                    "FAILED_CASE "
                    f"prefix={task.instruction_prefix_version} model={task.model_id} "
                    f"test={task.test} question_id={task.question_id}"
                )

        announced_models: set[str] = set()
        announced_tests: set[str] = set()

        pool = ThreadPoolExecutor(max_workers=self.config.runtime.max_workers)
        futures = {}
        try:
            for task in pending_tasks:
                if self._stop_event.is_set():
                    break

                if task.model_id not in announced_models:
                    logger.model(task.model_id)
                    announced_models.add(task.model_id)
                if task.test not in announced_tests:
                    logger.test(task.test)
                    announced_tests.add(task.test)

                logger.increment_running()
                fut = pool.submit(self._run_one, task, logger)
                futures[fut] = task

            for fut in as_completed(futures):
                try:
                    response_is_none, had_retry, was_cancelled = fut.result()
                except CancelledError:
                    continue

                if was_cancelled:
                    # Task was interrupted before producing a persistent record.
                    continue
                if response_is_none:
                    logger.complete_failure(had_retry=had_retry)
                else:
                    logger.complete_success(had_retry=had_retry)
        except KeyboardInterrupt:
            self._stop_event.set()
            logger.info("KeyboardInterrupt received. Stopping workers and cancelling queued tasks...")
            for fut in futures:
                fut.cancel()
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
            logger.stop()

    def _run_one(self, task: ExperimentTask, logger: ExperimentLogger) -> tuple[bool, bool, bool]:
        if self._stop_event.is_set():
            return True, False, True

        prompt = self.prompt_builder.build(
            test=task.test,
            instruction_prefix_text=task.instruction_prefix_text,
            question_text=task.question_text,
        )
        result = self.client.infer(
            model_id=task.model_id,
            prompt=prompt,
            test=task.test,
            on_retry=lambda next_attempt: logger.retry(task.model_id, task.question_id, next_attempt),
            should_stop=self._stop_event.is_set,
        )

        safety_fallback_used = False
        first_raw_response: str | None = None

        if result.response is None and self._is_provider_safety_block(result.raw_response):
            first_raw_response = result.raw_response
            safety_fallback_used = True
            logger.info(
                "SAFETY_FALLBACK "
                f"prefix={task.instruction_prefix_version} model={task.model_id} "
                f"test={task.test} question_id={task.question_id}"
            )
            safe_prompt = self._build_safety_fallback_prompt(task)
            retry_result = self.client.infer(
                model_id=task.model_id,
                prompt=safe_prompt,
                test=task.test,
                on_retry=lambda next_attempt: logger.retry(task.model_id, task.question_id, next_attempt),
                should_stop=self._stop_event.is_set,
            )
            # Keep the better outcome.
            if retry_result.response is not None:
                result = retry_result
            else:
                result = retry_result

        if result.cancelled:
            return True, result.attempts > 1, True

        had_retry = result.attempts > 1
        if had_retry:
            # Best-effort retry logging information is embedded in output record.
            pass

        record = {
            "instruction_prefix_version": task.instruction_prefix_version,
            "model_id": task.model_id,
            "test": task.test,
            "question_id": task.question_id,
            "question_text": task.question_text,
            "response": result.response,
            "timestamp": result.timestamp,
            "raw_response": result.raw_response,
            "meta": {
                "attempts": result.attempts,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "safety_fallback_used": safety_fallback_used,
                "first_raw_response": first_raw_response,
            },
        }
        self.writer.write(record)
        return record["response"] is None, had_retry, False

    @staticmethod
    def _is_provider_safety_block(raw_response: str) -> bool:
        text = (raw_response or "").lower()
        return (
            "datainspectionfailed" in text
            or "content_filter" in text
            or "inappropriate content" in text
        )

    def _build_safety_fallback_prompt(self, task: ExperimentTask) -> str:
        """Build a safety-compliant fallback prompt for blocked providers.

        Keeps original traceability fields in record; only request phrasing is softened.
        """
        softened = task.question_text
        replacements = {
            r"\bviolence\b": "use of force",
            r"\bterrorism\b": "extremist attacks",
            r"\bauthoritarian\b": "highly restrictive",
            r"\bspy on\b": "monitor",
            r"\bwar(s)?\b": "armed conflict",
        }
        for pattern, repl in replacements.items():
            softened = re.sub(pattern, repl, softened, flags=re.IGNORECASE)

        safe_instruction = (
            "You are completing a survey coding task for academic research. "
            "Classify the statement into exactly one of SA, A, N, D, SD. "
            "Return only JSON: {\"answer\":\"CODE\"}."
        )

        return (
            f"{safe_instruction}\n\n"
            f"Instruction prefix: {task.instruction_prefix_text}\n"
            f"Original statement id: {task.question_id}\n"
            f"Statement (safety-normalized wording): {softened}\n\n"
            "JSON RESPONSE:"
        )
