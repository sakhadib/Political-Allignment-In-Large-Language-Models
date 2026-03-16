from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
SCORES_DIR = ROOT / "scores"
OUT_DIR = ROOT / "analysis" / "results" / "clustering"
FIG_DIR = ROOT / "analysis" / "figures"


def _load_joined() -> pd.DataFrame:
    pct = pd.read_csv(SCORES_DIR / "pct_score.csv")
    val8 = pd.read_csv(SCORES_DIR / "8val_score.csv")

    merged = pct.merge(val8, on=["model_name", "prompt_varient"], suffixes=("_pct", "_8val"), how="inner")
    merged = merged.sort_values(["prompt_varient", "model_name"], kind="mergesort").reset_index(drop=True)
    return merged


def _fit_kmeans_metrics(df: pd.DataFrame, feature_cols: list[str], random_state: int = 42) -> tuple[np.ndarray, dict]:
    X = df[feature_cols].to_numpy(dtype=float)
    Xs = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=2, n_init=50, random_state=random_state)
    labels = km.fit_predict(Xs)

    metrics = {
        "silhouette": float(silhouette_score(Xs, labels)),
        "calinski_harabasz": float(calinski_harabasz_score(Xs, labels)),
        "davies_bouldin": float(davies_bouldin_score(Xs, labels)),
        "inertia": float(km.inertia_),
    }
    return labels, metrics


def _export_labels(df: pd.DataFrame, labels: np.ndarray, space_name: str, unit: str) -> None:
    out = df[["model_name", "prompt_varient"]].copy()
    out["space"] = space_name
    out["unit"] = unit
    out["cluster"] = labels
    out.to_csv(OUT_DIR / f"labels_{space_name}_{unit}.csv", index=False)


def _plot_prompt_level(joined: pd.DataFrame, labels_r2: np.ndarray, labels_r4: np.ndarray) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # R2 (Political Compass style) direct scatter
    x = joined["econ_score_pct"].to_numpy()
    y = joined["soc_score"].to_numpy()

    # R4 reduced to 2D by PCA for plotting
    X4 = joined[["econ_score_8val", "dipl_score", "govt_score", "scty_score"]].to_numpy(dtype=float)
    X4s = StandardScaler().fit_transform(X4)
    pca = PCA(n_components=2, random_state=42)
    Z = pca.fit_transform(X4s)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    sc1 = axes[0].scatter(x, y, c=labels_r2, cmap="tab10", alpha=0.85, s=36)
    axes[0].set_title("R2 Political Compass projection (PCT econ/soc)")
    axes[0].set_xlabel("econ_score_pct")
    axes[0].set_ylabel("soc_score")
    axes[0].grid(alpha=0.25)

    sc2 = axes[1].scatter(Z[:, 0], Z[:, 1], c=labels_r4, cmap="tab10", alpha=0.85, s=36)
    axes[1].set_title("R4 8Values (PCA visualization)")
    axes[1].set_xlabel("PC1")
    axes[1].set_ylabel("PC2")
    axes[1].grid(alpha=0.25)

    # avoid unused variable lint and keep consistent legend info possibility
    _ = (sc1, sc2)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "clustering_8val4d_vs_pct2d_prompt_model.png", dpi=240)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    joined = _load_joined()

    # Define the two spaces requested
    r2_cols = ["econ_score_pct", "soc_score"]
    r4_cols = ["econ_score_8val", "dipl_score", "govt_score", "scty_score"]

    rows = []

    # Unit A: prompt-model level (all rows)
    labels_r2_pm, m_r2_pm = _fit_kmeans_metrics(joined, r2_cols)
    labels_r4_pm, m_r4_pm = _fit_kmeans_metrics(joined, r4_cols)

    _export_labels(joined, labels_r2_pm, "r2_pct", "prompt_model")
    _export_labels(joined, labels_r4_pm, "r4_8val", "prompt_model")

    rows.append({"unit": "prompt_model", "space": "r2_pct", **m_r2_pm, "n_samples": len(joined), "n_features": len(r2_cols)})
    rows.append({"unit": "prompt_model", "space": "r4_8val", **m_r4_pm, "n_samples": len(joined), "n_features": len(r4_cols)})

    _plot_prompt_level(joined, labels_r2_pm, labels_r4_pm)

    # Unit B: model-mean level (mean across prompt variants)
    model_mean = joined.groupby("model_name", as_index=False).agg(
        econ_score_pct=("econ_score_pct", "mean"),
        soc_score=("soc_score", "mean"),
        econ_score_8val=("econ_score_8val", "mean"),
        dipl_score=("dipl_score", "mean"),
        govt_score=("govt_score", "mean"),
        scty_score=("scty_score", "mean"),
    )
    # Add synthetic prompt id for export format consistency
    model_mean["prompt_varient"] = "mean_over_prompts"

    labels_r2_mm, m_r2_mm = _fit_kmeans_metrics(model_mean, r2_cols)
    labels_r4_mm, m_r4_mm = _fit_kmeans_metrics(model_mean, r4_cols)

    _export_labels(model_mean, labels_r2_mm, "r2_pct", "model_mean")
    _export_labels(model_mean, labels_r4_mm, "r4_8val", "model_mean")

    rows.append({"unit": "model_mean", "space": "r2_pct", **m_r2_mm, "n_samples": len(model_mean), "n_features": len(r2_cols)})
    rows.append({"unit": "model_mean", "space": "r4_8val", **m_r4_mm, "n_samples": len(model_mean), "n_features": len(r4_cols)})

    out = pd.DataFrame(rows)
    out = out.sort_values(["unit", "space"], kind="mergesort")
    out.to_csv(OUT_DIR / "clustering_comparison_metrics.csv", index=False)

    # Short narrative artifact
    pm = out[out["unit"] == "prompt_model"].set_index("space")
    mm = out[out["unit"] == "model_mean"].set_index("space")

    summary_lines = [
        "# Clustering comparison: 8Values R4 vs Political Compass R2\n",
        "\n",
        "Method: KMeans(k=2), standardized features, random_state=42, n_init=50.\n",
        "\n",
        "## Prompt-model level\n",
        f"- R2 silhouette: {pm.loc['r2_pct', 'silhouette']:.4f}\n",
        f"- R4 silhouette: {pm.loc['r4_8val', 'silhouette']:.4f}\n",
        "\n",
        "## Model-mean level\n",
        f"- R2 silhouette: {mm.loc['r2_pct', 'silhouette']:.4f}\n",
        f"- R4 silhouette: {mm.loc['r4_8val', 'silhouette']:.4f}\n",
        "\n",
        "Artifacts:\n",
        "- clustering_comparison_metrics.csv\n",
        "- labels_r2_pct_prompt_model.csv\n",
        "- labels_r4_8val_prompt_model.csv\n",
        "- labels_r2_pct_model_mean.csv\n",
        "- labels_r4_8val_model_mean.csv\n",
        "- figure: analysis/figures/clustering_8val4d_vs_pct2d_prompt_model.png\n",
    ]
    (OUT_DIR / "README.md").write_text("".join(summary_lines), encoding="utf-8")

    print("Clustering comparison complete.")


if __name__ == "__main__":
    main()
