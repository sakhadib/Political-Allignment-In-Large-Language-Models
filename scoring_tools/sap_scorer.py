import argparse
import logging
import os
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://sapplyvalues.github.io/quiz.html?shuffle=false"
ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "Experiment" / "results" / "sap.csv"
OUTPUT_CSV = ROOT / "scores" / "sap_score.csv"

META_COLS = ["test", "question_id", "question_text", "prompt_varient"]
VALID_ANS = {"sa", "a", "n", "d", "sd"}
ANS_MAP = {
    "sa": "sa",
    "a": "a",
    "n": "n",
    "d": "d",
    "sd": "sd",
    "strongly agree": "sa",
    "agree": "a",
    "neutral": "n",
    "unsure": "n",
    "disagree": "d",
    "strongly disagree": "sd",
}
TO_BUTTON_VALUE = {"sa": 1.0, "a": 0.5, "n": 0.0, "d": -0.5, "sd": -1.0}

PAGE_LOAD_TIMEOUT = 30
FIND_TIMEOUT = 8
CLICK_PAUSE_SEC = 0.01


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("sap-scorer")


def qid_num(qid: str) -> int:
    m = re.match(r"^q(\d+)$", str(qid).strip().lower())
    return int(m.group(1)) if m else 10_000


def prompt_num(pv: str) -> int:
    m = re.match(r"^v(\d+)$", str(pv).strip().lower())
    return int(m.group(1)) if m else 10_000


def normalize_answer(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "n"
    key = str(value).strip().lower()
    ans = ANS_MAP.get(key, key)
    return ans if ans in VALID_ANS else "n"


def resolve_firefox_binary() -> str:
    env_bin = os.environ.get("FIREFOX_BINARY")
    if env_bin and Path(env_bin).exists():
        return env_bin

    snap_bin = Path("/snap/firefox/current/usr/lib/firefox/firefox")
    if snap_bin.exists():
        return str(snap_bin)

    return "/usr/bin/firefox"


def make_driver(headless: bool) -> webdriver.Firefox:
    opts = Options()
    if headless:
        opts.add_argument("-headless")
    opts.binary_location = resolve_firefox_binary()
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver


def open_form(driver: webdriver.Firefox) -> None:
    driver.get(URL)
    wait = WebDriverWait(driver, FIND_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.ID, "question-text")))
    wait.until(EC.presence_of_element_located((By.ID, "question-number")))


def answer_question(driver: webdriver.Firefox, ans: str) -> None:
    value = TO_BUTTON_VALUE[ans]
    driver.execute_script(f"next_question({value})")
    time.sleep(CLICK_PAUSE_SEC)


def click_serious(driver: webdriver.Firefox) -> None:
    wait = WebDriverWait(driver, FIND_TIMEOUT)
    btn = wait.until(EC.element_to_be_clickable((By.ID, "serious")))
    driver.execute_script("arguments[0].click();", btn)


def wait_for_results(driver: webdriver.Firefox, timeout: int = 8) -> None:
    end = time.time() + timeout
    while time.time() < end:
        if "results.html" in driver.current_url:
            return
        time.sleep(0.05)
    raise TimeoutException("Timed out waiting for sapply results URL")


def extract_scores(driver: webdriver.Firefox) -> tuple[float | None, float | None, float | None]:
    q = parse_qs(urlparse(driver.current_url).query)

    def _num(key: str) -> float | None:
        try:
            return float(q[key][0])
        except Exception:
            return None

    return _num("right"), _num("auth"), _num("prog")


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing = [c for c in META_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {csv_path}: {missing}")

    df = df.copy()
    df["__qnum__"] = df["question_id"].apply(qid_num)
    df["__pnum__"] = df["prompt_varient"].apply(prompt_num)
    df = df.sort_values(["__pnum__", "__qnum__"], kind="mergesort").drop(columns=["__qnum__", "__pnum__"])
    return df


def run_one(driver: webdriver.Firefox, block: pd.DataFrame, model_col: str) -> tuple[float | None, float | None, float | None]:
    open_form(driver)
    for _, row in block.iterrows():
        ans = normalize_answer(row[model_col])
        answer_question(driver, ans)
    click_serious(driver)
    wait_for_results(driver)
    return extract_scores(driver)


def score_all(input_csv: Path, output_csv: Path, headless: bool) -> None:
    df = load_data(input_csv)
    model_cols = [c for c in df.columns if c not in META_COLS]
    prompts = sorted(df["prompt_varient"].dropna().unique(), key=prompt_num)

    if not model_cols:
        raise ValueError("No model columns found.")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []

    driver = make_driver(headless=headless)
    try:
        total = len(prompts) * len(model_cols)
        done = 0
        for pv in prompts:
            block = df[df["prompt_varient"] == pv].copy()
            block["__qnum__"] = block["question_id"].apply(qid_num)
            block = block.sort_values("__qnum__", kind="mergesort").drop(columns="__qnum__")

            for model_col in model_cols:
                done += 1
                log.info("[%d/%d] prompt=%s | model=%s", done, total, pv, model_col)
                try:
                    right, auth, prog = run_one(driver, block, model_col)
                except TimeoutException:
                    log.exception("Timed out for prompt=%s model=%s", pv, model_col)
                    right, auth, prog = None, None, None
                except Exception:
                    log.exception("Failed for prompt=%s model=%s", pv, model_col)
                    right, auth, prog = None, None, None

                records.append(
                    {
                        "model_name": model_col,
                        "prompt_varient": pv,
                        "right_score": right,
                        "auth_score": auth,
                        "prog_score": prog,
                    }
                )
    finally:
        driver.quit()

    out_df = pd.DataFrame(records)
    out_df = out_df.sort_values(["prompt_varient", "model_name"], kind="mergesort")
    out_df.to_csv(output_csv, index=False, encoding="utf-8")
    log.info("Wrote %d rows to %s", len(out_df), output_csv)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score SapplyValues results from sap.csv")
    p.add_argument("--input", type=Path, default=INPUT_CSV, help="Input CSV path")
    p.add_argument("--output", type=Path, default=OUTPUT_CSV, help="Output score CSV path")
    p.add_argument("--headless", action="store_true", help="Run Firefox in headless mode")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    score_all(args.input, args.output, headless=args.headless)


if __name__ == "__main__":
    main()
