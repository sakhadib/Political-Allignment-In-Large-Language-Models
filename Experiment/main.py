from __future__ import annotations

import argparse

from config import build_config
from experiment_runner import ExperimentRunner


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PBLLM benchmark experiment runner.")
    parser.add_argument(
        "--try_failed",
        action="store_true",
        help="Retry only unresolved failed records from results/responses.jsonl.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = build_config()
    runner = ExperimentRunner(config)
    runner.run(try_failed_only=args.try_failed)


if __name__ == "__main__":
    main()
