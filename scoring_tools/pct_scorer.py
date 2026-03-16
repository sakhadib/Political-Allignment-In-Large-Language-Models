import argparse
import logging
import os
import re
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


URL = "https://politicalcompass.github.io/"
ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "Experiment" / "results" / "pct.csv"
OUTPUT_CSV = ROOT / "scores" / "pct_score.csv"

META_COLS = ["test", "question_id", "question_text", "prompt_varient"]
VALID_ANS = {"sa", "a", "d", "sd"}
# Political Compass has no neutral radio in this setup; map N to A.
ANS_MAP = {
    "sa": "sa",
    "a": "a",
    "n": "a",
    "d": "d",
    "sd": "sd",
    "strongly agree": "sa",
    "agree": "a",
    "neutral": "a",
    "unsure": "a",
    "disagree": "d",
    "strongly disagree": "sd",
}

PAGE_LOAD_TIMEOUT = 30
FIND_TIMEOUT = 8
CLICK_PAUSE_SEC = 0.01


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("pct-scorer")


def qid_num(qid: str) -> int:
    m = re.match(r"^q(\d+)$", str(qid).strip().lower())
    return int(m.group(1)) if m else 10_000


def prompt_num(pv: str) -> int:
    m = re.match(r"^v(\d+)$", str(pv).strip().lower())
    return int(m.group(1)) if m else 10_000


def normalize_answer(value: object) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return "a"
    key = str(value).strip().lower()
    ans = ANS_MAP.get(key, key)
    return ans if ans in VALID_ANS else "a"


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
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form")))
    wait.until(EC.presence_of_element_located((By.ID, "displayEcon")))
    wait.until(EC.presence_of_element_located((By.ID, "displaySoc")))


def click_answer(driver: webdriver.Firefox, qid: str, ans: str) -> None:
    sel = f"input.form-check-input[name='{qid}'][value='{ans}']"
    wait = WebDriverWait(driver, FIND_TIMEOUT)
    el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
    driver.execute_script("arguments[0].click();", el)
    time.sleep(CLICK_PAUSE_SEC)


def read_scores(driver: webdriver.Firefox) -> tuple[float | None, float | None]:
    econ_raw = driver.find_element(By.ID, "displayEcon").text.strip()
    soc_raw = driver.find_element(By.ID, "displaySoc").text.strip()
    try:
        econ = float(econ_raw)
    except ValueError:
        econ = None
    try:
        soc = float(soc_raw)
    except ValueError:
        soc = None
    return econ, soc


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


def run_one(driver: webdriver.Firefox, block: pd.DataFrame, model_col: str) -> tuple[float | None, float | None]:
    open_form(driver)

    for _, row in block.iterrows():
        qid = str(row["question_id"]).strip().lower()
        ans = normalize_answer(row[model_col])
        click_answer(driver, qid, ans)

    return read_scores(driver)


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
                    econ, soc = run_one(driver, block, model_col)
                except TimeoutException:
                    log.exception("Timed out for prompt=%s model=%s", pv, model_col)
                    econ, soc = None, None
                except Exception:
                    log.exception("Failed for prompt=%s model=%s", pv, model_col)
                    econ, soc = None, None

                records.append(
                    {
                        "model_name": model_col,
                        "prompt_varient": pv,
                        "econ_score": econ,
                        "soc_score": soc,
                    }
                )
    finally:
        driver.quit()

    out_df = pd.DataFrame(records)
    out_df = out_df.sort_values(["prompt_varient", "model_name"], kind="mergesort")
    out_df.to_csv(output_csv, index=False, encoding="utf-8")
    log.info("Wrote %d rows to %s", len(out_df), output_csv)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Score Political Compass results from pct.csv")
    p.add_argument("--input", type=Path, default=INPUT_CSV, help="Input CSV path")
    p.add_argument("--output", type=Path, default=OUTPUT_CSV, help="Output score CSV path")
    p.add_argument("--headless", action="store_true", help="Run Firefox in headless mode")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    score_all(args.input, args.output, headless=args.headless)


if __name__ == "__main__":
    main()
