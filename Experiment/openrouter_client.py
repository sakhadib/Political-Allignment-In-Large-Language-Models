from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import random
import re
import time
from email.utils import parsedate_to_datetime
from typing import Any, Callable
from urllib import error, request


_VALID_TOKENS_BY_TEST = {
    "pct": {"SA", "A", "D", "SD"},
    "default": {"SA", "A", "N", "D", "SD"},
}


@dataclass(frozen=True)
class OpenRouterResult:
    response: str | None
    raw_response: str
    timestamp: str
    attempts: int
    cancelled: bool = False


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        url: str,
        referer: str,
        title: str,
        timeout_seconds: float,
        max_retries: int,
        base_retry_delay_seconds: float,
        max_retry_delay_seconds: float,
        temperature: float,
        max_tokens: int,
    ) -> None:
        self.api_key = api_key
        self.url = url
        self.referer = referer
        self.title = title
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.base_retry_delay_seconds = base_retry_delay_seconds
        self.max_retry_delay_seconds = max_retry_delay_seconds
        self.temperature = temperature
        self.max_tokens = max_tokens

    def infer(
        self,
        model_id: str,
        prompt: str,
        test: str,
        on_retry: Callable[[int], None] | None = None,
        should_stop: Callable[[], bool] | None = None,
    ) -> OpenRouterResult:
        last_error = ""

        for attempt in range(1, self.max_retries + 2):
            if should_stop is not None and should_stop():
                cancelled_timestamp = datetime.now(timezone.utc).isoformat()
                return OpenRouterResult(
                    response=None,
                    raw_response=json.dumps({"error": "cancelled_by_user"}, ensure_ascii=False),
                    timestamp=cancelled_timestamp,
                    attempts=max(1, attempt - 1),
                    cancelled=True,
                )

            timestamp = datetime.now(timezone.utc).isoformat()
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
            body = json.dumps(payload).encode("utf-8")
            req = request.Request(
                self.url,
                data=body,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.referer,
                    "X-Title": self.title,
                    "User-Agent": "PBLLM-Benchmark/1.0",
                },
            )

            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                    raw_bytes = resp.read()
                raw_text = raw_bytes.decode("utf-8", errors="replace")
                data = json.loads(raw_text)

                # OpenRouter can return error payloads in JSON body.
                if isinstance(data, dict) and "error" in data:
                    raise RuntimeError(f"API_ERROR: {json.dumps(data.get('error'), ensure_ascii=False)}")

                text = self._extract_message_text(data)
                parsed = self._extract_answer_token(text, test=test)
                return OpenRouterResult(
                    response=parsed,
                    raw_response=raw_text,
                    timestamp=timestamp,
                    attempts=attempt,
                    cancelled=False,
                )
            except error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
                last_error = f"HTTP {e.code}: {e.reason}; body={err_body}"
                if attempt <= self.max_retries:
                    retry_after = self._parse_retry_after_seconds(e)
                    if retry_after is not None:
                        self._sleep_cooperative(retry_after, should_stop, attempt)
                        continue
            except Exception as e:  # noqa: BLE001
                last_error = f"{type(e).__name__}: {e}"

            if attempt <= self.max_retries:
                if on_retry is not None:
                    on_retry(attempt + 1)
                delay = min(
                    self.max_retry_delay_seconds,
                    self.base_retry_delay_seconds * (2 ** (attempt - 1)),
                )
                sleep_for = delay + random.uniform(0, delay * 0.2)
                cancelled = self._sleep_cooperative(sleep_for, should_stop, attempt)
                if cancelled:
                    cancelled_timestamp = datetime.now(timezone.utc).isoformat()
                    return OpenRouterResult(
                        response=None,
                        raw_response=json.dumps({"error": "cancelled_by_user"}, ensure_ascii=False),
                        timestamp=cancelled_timestamp,
                        attempts=attempt,
                        cancelled=True,
                    )

        failed_timestamp = datetime.now(timezone.utc).isoformat()
        error_payload = {"error": last_error}
        return OpenRouterResult(
            response=None,
            raw_response=json.dumps(error_payload, ensure_ascii=False),
            timestamp=failed_timestamp,
            attempts=self.max_retries + 1,
            cancelled=False,
        )

    @staticmethod
    def _extract_message_text(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for part in content:
                    if isinstance(part, dict):
                        if "text" in part and isinstance(part["text"], str):
                            parts.append(part["text"])
                    elif isinstance(part, str):
                        parts.append(part)
                if parts:
                    return "\n".join(parts)
            return str(content)
        except Exception:  # noqa: BLE001
            return json.dumps(data, ensure_ascii=False)

    @staticmethod
    def _extract_answer_token(text: str, test: str) -> str | None:
        allowed = _VALID_TOKENS_BY_TEST.get(test, _VALID_TOKENS_BY_TEST["default"])

        # 1) Try strict JSON parse first.
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and "answer" in parsed:
                candidate = str(parsed["answer"]).strip().upper()
                if candidate in allowed:
                    return candidate
            if isinstance(parsed, dict) and "rating" in parsed:
                candidate = str(parsed["rating"]).strip().upper()
                if candidate in allowed:
                    return candidate
        except Exception:
            pass

        # 2) Regex fallback to recover from minor format drift.
        m = re.search(r'"answer"\s*:\s*"(SA|SD|A|N|D)"', text, flags=re.IGNORECASE)
        if m:
            candidate = m.group(1).upper()
            if candidate in allowed:
                return candidate

        m_rating = re.search(r'"rating"\s*:\s*"(SA|SD|A|N|D)"', text, flags=re.IGNORECASE)
        if m_rating:
            candidate = m_rating.group(1).upper()
            if candidate in allowed:
                return candidate

        # 3) Final fallback: exact single-token response.
        token = text.strip().upper()
        if token in allowed:
            return token

        # 4) Last valid standalone token fallback (robust to extra text).
        matches = list(re.finditer(r"\b(SA|SD|A|N|D)\b", text, flags=re.IGNORECASE))
        if matches:
            candidate = matches[-1].group(1).upper()
            if candidate in allowed:
                return candidate

        return None

    @staticmethod
    def _parse_retry_after_seconds(exc: error.HTTPError) -> float | None:
        headers = getattr(exc, "headers", None)
        if headers is None:
            return None

        value = headers.get("Retry-After")
        if not value:
            return None

        try:
            return max(0.0, float(value))
        except ValueError:
            try:
                dt = parsedate_to_datetime(value)
                now = datetime.now(timezone.utc)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return max(0.0, (dt - now).total_seconds())
            except Exception:  # noqa: BLE001
                return None

    @staticmethod
    def _sleep_cooperative(
        duration_seconds: float,
        should_stop: Callable[[], bool] | None,
        attempt: int,
    ) -> bool:
        del attempt
        if should_stop is None:
            time.sleep(duration_seconds)
            return False

        end_time = time.perf_counter() + max(0.0, duration_seconds)
        while time.perf_counter() < end_time:
            if should_stop():
                return True
            time.sleep(0.05)
        return False
