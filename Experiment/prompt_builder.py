from __future__ import annotations

from pathlib import Path


class PromptBuilder:
    def __init__(self, default_template_path: Path, pct_template_path: Path) -> None:
        self.default_template = default_template_path.read_text(encoding="utf-8")
        self.pct_template = pct_template_path.read_text(encoding="utf-8")

    def build(self, test: str, instruction_prefix_text: str, question_text: str) -> str:
        template = self.pct_template if test == "pct" else self.default_template
        prompt = template.replace("{PREFIX}", instruction_prefix_text)
        prompt = prompt.replace("{QUESTION}", question_text)
        return prompt
