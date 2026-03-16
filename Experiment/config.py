from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _load_dotenv(dotenv_path: Path) -> None:
    """Minimal .env loader (KEY=VALUE) that does not override existing env vars."""
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Paths:
    project_root: Path
    experiment_root: Path
    questions_dir: Path
    models_file: Path
    instruction_prefix_file: Path
    prompt_default_file: Path
    prompt_default_pct_file: Path
    output_dir: Path
    responses_file: Path


@dataclass(frozen=True)
class RuntimeConfig:
    openrouter_api_key: str
    openrouter_url: str
    openrouter_referer: str
    openrouter_title: str
    max_workers: int
    request_timeout_seconds: float
    max_retries: int
    base_retry_delay_seconds: float
    max_retry_delay_seconds: float
    model_temperature: float
    model_max_tokens: int


@dataclass(frozen=True)
class AppConfig:
    paths: Paths
    runtime: RuntimeConfig



def build_config() -> AppConfig:
    experiment_root = Path(__file__).resolve().parent
    project_root = experiment_root.parent
    dotenv_path = experiment_root / ".env"
    _load_dotenv(dotenv_path)

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip() or os.getenv("OPENROUTER_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing. Add it to Experiment/.env or your environment."
        )

    max_workers = int(os.getenv("EXPERIMENT_MAX_WORKERS", "24"))
    timeout = float(os.getenv("EXPERIMENT_REQUEST_TIMEOUT", "60"))
    max_retries = int(os.getenv("EXPERIMENT_MAX_RETRIES", "4"))
    retry_base = float(os.getenv("EXPERIMENT_RETRY_BASE_DELAY", "0.8"))
    retry_max = float(os.getenv("EXPERIMENT_RETRY_MAX_DELAY", "12.0"))
    temperature = float(os.getenv("EXPERIMENT_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("EXPERIMENT_MAX_TOKENS", "24"))

    paths = Paths(
        project_root=project_root,
        experiment_root=experiment_root,
        questions_dir=experiment_root / "Questions",
        models_file=experiment_root / "models.json",
        instruction_prefix_file=experiment_root / "instruction_prefix.json",
        prompt_default_file=experiment_root / "prompt_default.txt",
        prompt_default_pct_file=experiment_root / "prompt_default_pct.txt",
        output_dir=experiment_root / "results",
        responses_file=experiment_root / "results" / "responses.jsonl",
    )

    runtime = RuntimeConfig(
        openrouter_api_key=api_key,
        openrouter_url=os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions"),
        openrouter_referer=os.getenv("OPENROUTER_REFERER", "https://github.com/sakhadib/Political-Bias-of-LLMs"),
        openrouter_title=os.getenv("OPENROUTER_TITLE", "PBLLM Benchmark Runner"),
        max_workers=max_workers,
        request_timeout_seconds=timeout,
        max_retries=max_retries,
        base_retry_delay_seconds=retry_base,
        max_retry_delay_seconds=retry_max,
        model_temperature=temperature,
        model_max_tokens=max_tokens,
    )

    return AppConfig(paths=paths, runtime=runtime)
