from __future__ import annotations

from pathlib import Path
import itertools

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multitest import multipletests
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
SCORES_DIR = ROOT / "scores"
RESULTS_DIR = ROOT / "analysis" / "results"
FIG_DIR = ROOT / "analysis" / "figures"


def _prompt_num(v: str) -> int:
    s = str(v).strip().lower()
    if s.startswith("v") and s[1:].isdigit():
        return int(s[1:])
    return 10_000


def load_and_harmonize() -> pd.DataFrame:
    pct = pd.read_csv(SCORES_DIR / "pct_score.csv")
    sap = pd.read_csv(SCORES_DIR / "sap_score.csv")
    val8 = pd.read_csv(SCORES_DIR / "8val_score.csv")

    pct_long = pct.rename(
        columns={
            "econ_score": "score",
        }
    )[["model_name", "prompt_varient", "score"]].copy()
    pct_long["test"] = "pct"
    pct_long["axis"] = "econ"

    pct_soc = pct.rename(columns={"soc_score": "score"})[["model_name", "prompt_varient", "score"]].copy()
    pct_soc["test"] = "pct"
    pct_soc["axis"] = "soc"

    sap_long_parts = []
    for axis_col, axis_name in [
        ("right_score", "right"),
        ("auth_score", "auth"),
        ("prog_score", "prog"),
    ]:
        part = sap.rename(columns={axis_col: "score"})[["model_name", "prompt_varient", "score"]].copy()
        part["test"] = "sap"
        part["axis"] = axis_name
        sap_long_parts.append(part)

    val8_parts = []
    for axis_col, axis_name in [
        ("econ_score", "econ"),
        ("dipl_score", "dipl"),
        ("govt_score", "govt"),
        ("scty_score", "scty"),
    ]:
        part = val8.rename(columns={axis_col: "score"})[["model_name", "prompt_varient", "score"]].copy()
        part["test"] = "8val"
        part["axis"] = axis_name
        val8_parts.append(part)

    combined = pd.concat([pct_long, pct_soc, *sap_long_parts, *val8_parts], ignore_index=True)
    combined["prompt_varient"] = combined["prompt_varient"].astype(str)
    combined["prompt_num"] = combined["prompt_varient"].map(_prompt_num)
    combined = combined.sort_values(["test", "axis", "prompt_num", "model_name"], kind="mergesort").reset_index(drop=True)

    # Trait mapping for MTMM-style comparison
    trait_map = {
        # economic trait proxies
        ("pct", "econ"): "economic",
        ("8val", "econ"): "economic",
        ("sap", "right"): "economic_inverse",  # higher right => less egalitarian
        # authority trait proxies
        ("pct", "soc"): "authority_proxy",
        ("8val", "govt"): "authority_proxy",
        ("sap", "auth"): "authority_proxy",
        # cultural/progressive trait proxies
        ("8val", "scty"): "progressive_proxy",
        ("sap", "prog"): "progressive_proxy",
        # extra 8val axis
        ("8val", "dipl"): "diplomatic",
    }

    combined["trait_proxy"] = [trait_map.get((t, a), "other") for t, a in zip(combined["test"], combined["axis"])]
    combined["method"] = combined["test"] + "_" + combined["axis"]
    return combined


def save_harmonized(df: pd.DataFrame) -> None:
    out_dir = RESULTS_DIR / "harmonized"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "scores_long.csv", index=False)

    wide = df.pivot_table(
        index=["model_name", "prompt_varient", "prompt_num"],
        columns="method",
        values="score",
        aggfunc="mean",
    ).reset_index()
    wide = wide.sort_values(["prompt_num", "model_name"], kind="mergesort")
    wide.to_csv(out_dir / "scores_wide.csv", index=False)


def run_two_way_anova(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (test, axis), sub in df.groupby(["test", "axis"], sort=True):
        # OLS ANOVA with categorical factors
        model = ols("score ~ C(model_name) + C(prompt_varient)", data=sub).fit()
        anov = anova_lm(model, typ=2).reset_index().rename(columns={"index": "source"})

        ss_total = float(((sub["score"] - sub["score"].mean()) ** 2).sum())
        for _, r in anov.iterrows():
            source = str(r["source"])
            if source == "Residual":
                continue
            ss = float(r["sum_sq"])
            p = float(r["PR(>F)"])
            df_num = float(r["df"])
            eta2 = ss / ss_total if ss_total > 0 else np.nan
            rows.append(
                {
                    "test": test,
                    "axis": axis,
                    "source": source,
                    "df": df_num,
                    "sum_sq": ss,
                    "f_value": float(r["F"]),
                    "p_value": p,
                    "eta_sq": eta2,
                }
            )

    out = pd.DataFrame(rows)
    # Multiple testing correction across all factor tests
    reject, p_adj, _, _ = multipletests(out["p_value"].values, method="fdr_bh")
    out["p_value_fdr_bh"] = p_adj
    out["significant_fdr_bh"] = reject

    out_dir = RESULTS_DIR / "anova"
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / "two_way_anova_effects.csv", index=False)

    summary = (
        out.pivot_table(index=["test", "axis"], columns="source", values=["eta_sq", "p_value", "p_value_fdr_bh"], aggfunc="first")
        .sort_index()
    )
    summary.to_csv(out_dir / "two_way_anova_summary_matrix.csv")
    return out


def plot_prompt_model_spread(df: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # One compact figure: for each test-axis pair, spread by prompt
    pairs = sorted(df[["test", "axis"]].drop_duplicates().itertuples(index=False, name=None))
    n = len(pairs)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(18, 4.2 * nrows), squeeze=False)

    for i, (test, axis) in enumerate(pairs):
        r, c = divmod(i, ncols)
        ax = axes[r][c]
        sub = df[(df["test"] == test) & (df["axis"] == axis)].copy()
        sub = sub.sort_values("prompt_num", kind="mergesort")
        sns.boxplot(data=sub, x="prompt_varient", y="score", color="#C9DAF8", ax=ax)
        sns.stripplot(data=sub, x="prompt_varient", y="score", hue="model_name", size=3.5, alpha=0.8, dodge=False, ax=ax)
        ax.set_title(f"{test}:{axis}")
        ax.set_xlabel("prompt_varient")
        ax.set_ylabel("score")
        if i == 0:
            ax.legend(title="model", bbox_to_anchor=(1.02, 1), loc="upper left")
        else:
            if ax.get_legend() is not None:
                ax.get_legend().remove()

    # turn off empty axes
    for j in range(n, nrows * ncols):
        r, c = divmod(j, ncols)
        axes[r][c].axis("off")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "prompt_model_spread.png", dpi=220)
    plt.close(fig)


def _method_meta(method: str) -> tuple[str, str]:
    # method format: <test>_<axis>
    t, a = method.split("_", 1)
    return t, a


def run_mtmm(df: pd.DataFrame) -> pd.DataFrame:
    # Work in wide form at (model, prompt) granularity
    wide = df.pivot_table(
        index=["model_name", "prompt_varient", "prompt_num"],
        columns="method",
        values="score",
        aggfunc="mean",
    ).reset_index()

    methods = [c for c in wide.columns if c not in {"model_name", "prompt_varient", "prompt_num"}]
    pairs = []
    for m1, m2 in itertools.combinations(methods, 2):
        x = wide[m1]
        y = wide[m2]
        r, p = stats.pearsonr(x, y)
        t1, a1 = _method_meta(m1)
        t2, a2 = _method_meta(m2)

        # classify MTMM relation type using trait proxies from long df mapping
        trait1 = df.loc[df["method"] == m1, "trait_proxy"].iloc[0]
        trait2 = df.loc[df["method"] == m2, "trait_proxy"].iloc[0]

        same_trait = trait1 == trait2
        same_method_family = t1 == t2

        if same_trait and not same_method_family:
            rel = "monotrait_heteromethod"
        elif (not same_trait) and same_method_family:
            rel = "heterotrait_monomethod"
        elif (not same_trait) and (not same_method_family):
            rel = "heterotrait_heteromethod"
        else:
            # same trait, same method family (e.g., two axes mapped same trait within one test)
            rel = "monotrait_monomethod_family"

        pairs.append(
            {
                "method_1": m1,
                "method_2": m2,
                "test_1": t1,
                "axis_1": a1,
                "test_2": t2,
                "axis_2": a2,
                "trait_1": trait1,
                "trait_2": trait2,
                "relation_type": rel,
                "pearson_r": r,
                "p_value": p,
            }
        )

    mtmm = pd.DataFrame(pairs)
    reject, p_adj, _, _ = multipletests(mtmm["p_value"].values, method="fdr_bh")
    mtmm["p_value_fdr_bh"] = p_adj
    mtmm["significant_fdr_bh"] = reject

    out_dir = RESULTS_DIR / "mtmm"
    out_dir.mkdir(parents=True, exist_ok=True)
    mtmm.to_csv(out_dir / "mtmm_pairwise_correlations.csv", index=False)

    # Matrix export (raw r)
    corr = wide[methods].corr(method="pearson")
    corr.to_csv(out_dir / "mtmm_correlation_matrix.csv")

    # Relation-type summary
    rel_summary = mtmm.groupby("relation_type", as_index=False).agg(
        n_pairs=("pearson_r", "count"),
        mean_r=("pearson_r", "mean"),
        median_r=("pearson_r", "median"),
        min_r=("pearson_r", "min"),
        max_r=("pearson_r", "max"),
        frac_significant_fdr=("significant_fdr_bh", "mean"),
    )
    rel_summary.to_csv(out_dir / "mtmm_relation_summary.csv", index=False)

    # Heatmap
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9.5, 7.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("MTMM-style Cross-Method Correlation Matrix (Pearson r)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mtmm_heatmap.png", dpi=220)
    plt.close()

    return mtmm


def run_mtmm_trait_aligned() -> pd.DataFrame:
    pct = pd.read_csv(SCORES_DIR / "pct_score.csv")
    sap = pd.read_csv(SCORES_DIR / "sap_score.csv")
    val8 = pd.read_csv(SCORES_DIR / "8val_score.csv")

    merged = pct.merge(sap, on=["model_name", "prompt_varient"], how="inner").merge(
        val8, on=["model_name", "prompt_varient"], how="inner"
    )

    # Align directions so higher means "more of trait" consistently.
    # economic_left: larger => more egalitarian/left
    merged["economic_left_pct"] = -merged["econ_score_x"]
    merged["economic_left_8val"] = merged["econ_score_y"]
    merged["economic_left_sap"] = -merged["right_score"]

    # authority: larger => more authority/statism
    merged["authority_pct"] = -merged["soc_score"]
    merged["authority_8val"] = merged["govt_score"]
    merged["authority_sap"] = merged["auth_score"]

    # progressive: larger => more culturally progressive
    merged["progressive_8val"] = merged["scty_score"]
    merged["progressive_sap"] = merged["prog_score"]

    cols = [
        "economic_left_pct",
        "economic_left_8val",
        "economic_left_sap",
        "authority_pct",
        "authority_8val",
        "authority_sap",
        "progressive_8val",
        "progressive_sap",
    ]

    # Method metadata for MTMM relation typing
    trait_of = {
        "economic_left_pct": "economic",
        "economic_left_8val": "economic",
        "economic_left_sap": "economic",
        "authority_pct": "authority",
        "authority_8val": "authority",
        "authority_sap": "authority",
        "progressive_8val": "progressive",
        "progressive_sap": "progressive",
    }
    method_family_of = {
        "economic_left_pct": "pct",
        "economic_left_8val": "8val",
        "economic_left_sap": "sap",
        "authority_pct": "pct",
        "authority_8val": "8val",
        "authority_sap": "sap",
        "progressive_8val": "8val",
        "progressive_sap": "sap",
    }

    rows = []
    for c1, c2 in itertools.combinations(cols, 2):
        r, p = stats.pearsonr(merged[c1], merged[c2])
        same_trait = trait_of[c1] == trait_of[c2]
        same_family = method_family_of[c1] == method_family_of[c2]

        if same_trait and not same_family:
            rel = "monotrait_heteromethod"
        elif (not same_trait) and same_family:
            rel = "heterotrait_monomethod"
        elif (not same_trait) and (not same_family):
            rel = "heterotrait_heteromethod"
        else:
            rel = "monotrait_monomethod_family"

        rows.append(
            {
                "method_1": c1,
                "method_2": c2,
                "trait_1": trait_of[c1],
                "trait_2": trait_of[c2],
                "family_1": method_family_of[c1],
                "family_2": method_family_of[c2],
                "relation_type": rel,
                "pearson_r": r,
                "p_value": p,
            }
        )

    aligned = pd.DataFrame(rows)
    reject, p_adj, _, _ = multipletests(aligned["p_value"].values, method="fdr_bh")
    aligned["p_value_fdr_bh"] = p_adj
    aligned["significant_fdr_bh"] = reject

    out_dir = RESULTS_DIR / "mtmm"
    out_dir.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(out_dir / "mtmm_trait_aligned_pairwise_correlations.csv", index=False)

    corr = merged[cols].corr(method="pearson")
    corr.to_csv(out_dir / "mtmm_trait_aligned_correlation_matrix.csv")

    rel_summary = aligned.groupby("relation_type", as_index=False).agg(
        n_pairs=("pearson_r", "count"),
        mean_r=("pearson_r", "mean"),
        median_r=("pearson_r", "median"),
        min_r=("pearson_r", "min"),
        max_r=("pearson_r", "max"),
        frac_significant_fdr=("significant_fdr_bh", "mean"),
    )
    rel_summary.to_csv(out_dir / "mtmm_trait_aligned_relation_summary.csv", index=False)

    plt.figure(figsize=(9.5, 7.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("MTMM-style Trait-Aligned Correlation Matrix (Pearson r)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "mtmm_trait_aligned_heatmap.png", dpi=220)
    plt.close()

    return aligned


def write_readme(anova_df: pd.DataFrame, mtmm_df: pd.DataFrame, mtmm_aligned_df: pd.DataFrame) -> None:
    text = []
    text.append("# Analysis outputs\n")
    text.append("This folder contains requested analyses:\n")
    text.append("1. Harmonized score table\n")
    text.append("2. Prompt robustness (Two-Way ANOVA)\n")
    text.append("3. MTMM-style construct validity correlations\n")

    # concise highlights
    top_model_effect = anova_df[anova_df["source"] == "C(model_name)"].sort_values("eta_sq", ascending=False).head(3)
    top_prompt_effect = anova_df[anova_df["source"] == "C(prompt_varient)"].sort_values("eta_sq", ascending=False).head(3)

    text.append("\n## Quick highlights\n")
    text.append("### Largest model effects (eta_sq)\n")
    for _, r in top_model_effect.iterrows():
        text.append(f"- {r['test']}:{r['axis']} eta_sq={r['eta_sq']:.3f}, p_fdr={r['p_value_fdr_bh']:.3g}\n")

    text.append("\n### Largest prompt effects (eta_sq)\n")
    for _, r in top_prompt_effect.iterrows():
        text.append(f"- {r['test']}:{r['axis']} eta_sq={r['eta_sq']:.3f}, p_fdr={r['p_value_fdr_bh']:.3g}\n")

    rel = mtmm_df.groupby("relation_type")["pearson_r"].mean().sort_values(ascending=False)
    text.append("\n### MTMM relation mean r\n")
    for k, v in rel.items():
        text.append(f"- {k}: {v:.3f}\n")

    rel_aligned = mtmm_aligned_df.groupby("relation_type")["pearson_r"].mean().sort_values(ascending=False)
    text.append("\n### MTMM trait-aligned relation mean r\n")
    for k, v in rel_aligned.items():
        text.append(f"- {k}: {v:.3f}\n")

    (ROOT / "analysis" / "README.md").write_text("".join(text), encoding="utf-8")


def main() -> None:
    df = load_and_harmonize()
    save_harmonized(df)

    anova_df = run_two_way_anova(df)
    plot_prompt_model_spread(df)

    mtmm_df = run_mtmm(df)
    mtmm_aligned_df = run_mtmm_trait_aligned()

    write_readme(anova_df, mtmm_df, mtmm_aligned_df)
    print("Analysis complete. Outputs written under analysis/results and analysis/figures")


if __name__ == "__main__":
    main()
