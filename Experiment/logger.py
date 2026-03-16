from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import threading
import time


class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"


@dataclass
class Stats:
    total: int
    completed: int = 0
    failed: int = 0
    retried: int = 0
    running: int = 0


class ExperimentLogger:
    def __init__(self, total_tasks: int) -> None:
        self._stats = Stats(total=total_tasks)
        self._lock = threading.Lock()
        self._start = time.perf_counter()
        self._stop_event = threading.Event()
        self._ticker = threading.Thread(target=self._ticker_loop, daemon=True)

    def start(self) -> None:
        self.info("Starting experiment")
        self._ticker.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._ticker.is_alive():
            self._ticker.join(timeout=1.0)
        self._print_progress_line(force_newline=True)
        self.info("Experiment finished")

    def info(self, message: str) -> None:
        self._line("INFO", message, _C.CYAN)

    def model(self, model_id: str) -> None:
        self._line("MODEL", model_id, _C.MAGENTA)

    def test(self, test_name: str) -> None:
        self._line("TEST", test_name, _C.MAGENTA)

    def retry(self, model_id: str, question_id: str, attempt: int) -> None:
        self._line(
            "RETRY",
            f"model={model_id} question={question_id} attempt={attempt}",
            _C.YELLOW,
        )

    def increment_running(self) -> None:
        with self._lock:
            self._stats.running += 1

    def complete_success(self, had_retry: bool) -> None:
        with self._lock:
            self._stats.running = max(0, self._stats.running - 1)
            self._stats.completed += 1
            if had_retry:
                self._stats.retried += 1

    def complete_failure(self, had_retry: bool) -> None:
        with self._lock:
            self._stats.running = max(0, self._stats.running - 1)
            self._stats.completed += 1
            self._stats.failed += 1
            if had_retry:
                self._stats.retried += 1

    def snapshot(self) -> Stats:
        with self._lock:
            return Stats(**self._stats.__dict__)

    def _ticker_loop(self) -> None:
        while not self._stop_event.is_set():
            self._print_progress_line(force_newline=False)
            time.sleep(1.0)

    def _print_progress_line(self, force_newline: bool) -> None:
        s = self.snapshot()
        elapsed = max(1e-9, time.perf_counter() - self._start)
        rps = s.completed / elapsed
        msg = (
            f"{_C.BOLD}{_C.GREEN}[PROGRESS]{_C.RESET} "
            f"{s.completed}/{s.total} completed | running={s.running} | "
            f"failed={s.failed} | retried={s.retried} | rps={rps:.2f}"
        )
        end = "\n" if force_newline else "\r"
        print(msg, end=end, flush=True)

    @staticmethod
    def _line(tag: str, message: str, color: str) -> None:
        ts = datetime.utcnow().strftime("%H:%M:%S")
        print(f"{color}[{tag}] {_C.RESET}{ts} {message}", flush=True)
