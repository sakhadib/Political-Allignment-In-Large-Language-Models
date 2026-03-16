from pathlib import Path
import pandas as pd
import json

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "analysis" / "results"

anova = pd.read_csv(RES / "anova" / "two_way_anova_effects.csv")
summary = pd.read_csv(RES / "anova" / "two_way_anova_summary_matrix.csv", header=[0,1], index_col=[0,1])
mtmm = pd.read_csv(RES / "mtmm" / "mtmm_trait_aligned_pairwise_correlations.csv")
mtmm_rel = pd.read_csv(RES / "mtmm" / "mtmm_trait_aligned_relation_summary.csv")
cluster = pd.read_csv(RES / "clustering" / "clustering_comparison_metrics.csv")
scores_wide = pd.read_csv(RES / "harmonized" / "scores_wide.csv")

print("=== Dataset coverage ===")
print("Results subfolders:", sorted([p.name for p in RES.iterdir() if p.is_dir()]))
print("rows scores_wide:", len(scores_wide))
print("models:", scores_wide["model_name"].nunique())
print("prompt variants:", scores_wide["prompt_varient"].nunique())

print("\n=== ANOVA checks ===")
for axis in ["econ", "soc"]:
    row = anova[(anova["test"] == "pct") & (anova["axis"] == axis) & (anova["source"] == "C(model_name)")].iloc[0]
    print(f"pct_{axis} model eta_sq = {row['eta_sq']:.3f}")

core = anova[(anova["source"] == "C(prompt_varient)") & (
    ((anova["test"] == "8val") & (anova["axis"] == "econ")) |
    ((anova["test"] == "pct") & (anova["axis"] == "econ")) |
    ((anova["test"] == "sap") & (anova["axis"] == "right"))
)]
print("core prompt eta_sq:", core[["test","axis","eta_sq"]].to_dict("records"))
print("all prompt significant_fdr_bh:", anova[anova["source"] == "C(prompt_varient)"]["significant_fdr_bh"].value_counts().to_dict())

sap_prog_prompt = anova[(anova["test"] == "sap") & (anova["axis"] == "prog") & (anova["source"] == "C(prompt_varient)")].iloc[0]
sap_prog_model = anova[(anova["test"] == "sap") & (anova["axis"] == "prog") & (anova["source"] == "C(model_name)")].iloc[0]
print("sap_prog prompt eta_sq:", round(float(sap_prog_prompt["eta_sq"]), 3), "p_fdr:", sap_prog_prompt["p_value_fdr_bh"])
print("sap_prog model eta_sq:", round(float(sap_prog_model["eta_sq"]), 3))

print("\n=== MTMM checks ===")
def pick(m1, m2):
    m = mtmm[((mtmm.method_1 == m1) & (mtmm.method_2 == m2)) | ((mtmm.method_1 == m2) & (mtmm.method_2 == m1))]
    return m.iloc[0]

for a,b in [
    ("economic_left_pct","economic_left_8val"),
    ("economic_left_pct","economic_left_sap"),
    ("authority_pct","authority_sap"),
    ("authority_pct","progressive_sap"),
    ("authority_pct","progressive_8val"),
]:
    r = pick(a,b)
    print(f"{a} vs {b}: r={r.pearson_r:.3f}, p={r.p_value:.3g}, p_fdr={r.p_value_fdr_bh:.3g}")

print("relation summary:")
print(mtmm_rel.to_string(index=False))

print("\n=== Clustering checks ===")
print(cluster.to_string(index=False))

labels_r2 = pd.read_csv(RES / "clustering" / "labels_r2_pct_prompt_model.csv")
labels_r4 = pd.read_csv(RES / "clustering" / "labels_r4_8val_prompt_model.csv")

def cluster_composition(df):
    out = df.groupby("cluster")["model_name"].unique().to_dict()
    return {int(k): sorted(v.tolist()) for k,v in out.items()}

print("r2 cluster composition:", cluster_composition(labels_r2))
print("r4 cluster composition:", cluster_composition(labels_r4))

stable_r2 = labels_r2.groupby("model_name")["cluster"].nunique().max()
stable_r4 = labels_r4.groupby("model_name")["cluster"].nunique().max()
print("max unique clusters per model across prompts (r2, r4):", stable_r2, stable_r4)

print("\n=== Phase 1 spot checks from scores_wide ===")
deepseek = scores_wide[scores_wide["model_name"] == "DeepSeek v3.2"]
for v in ["v1", "v2", "v3", "v4", "v8"]:
    row = deepseek[deepseek["prompt_varient"] == v]
    if not row.empty:
        print(f"DeepSeek pct_econ {v}: {float(row['pct_econ'].iloc[0]):.2f}")

gemini = scores_wide[scores_wide["model_name"] == "Gemini 2.5 Flash"]
if not gemini.empty:
    g1 = gemini[gemini["prompt_varient"] == "v1"]["pct_econ"].iloc[0]
    g8 = gemini[gemini["prompt_varient"] == "v8"]["pct_econ"].iloc[0]
    print(f"Gemini pct_econ v1 -> v8: {g1:.2f} -> {g8:.2f}")

grok = scores_wide[scores_wide["model_name"] == "Grok 4.1 Fast"]
if not grok.empty:
    print(
        "Grok ranges:",
        {
            "pct_econ": (round(float(grok["pct_econ"].min()), 2), round(float(grok["pct_econ"].max()), 2)),
            "sap_right": (round(float(grok["sap_right"].min()), 2), round(float(grok["sap_right"].max()), 2)),
            "pct_soc": (round(float(grok["pct_soc"].min()), 2), round(float(grok["pct_soc"].max()), 2)),
        },
    )

print("\n=== Phase 5 base-vs-instruct artifact checks ===")
base_dir = RES / "base_vs_instruct"
pc = json.loads((base_dir / "_pc_scores.json").read_text())
sap = json.loads((base_dir / "_sapply_scores.json").read_text())
v8 = json.loads((base_dir / "_8values_scores.json").read_text())
print("base_vs_instruct files:", ["_pc_scores.json", "_sapply_scores.json", "_8values_scores.json"])
print("rows (pc, sap, 8val):", len(pc), len(sap), len(v8))

def by_responder(rows, field):
    return {r["responder"]: r[field] for r in rows}

sap_right = by_responder(sap, "right_score")
sap_prog = by_responder(sap, "prog_score")
v8_econ = by_responder(v8, "econ_score")
v8_scty = by_responder(v8, "scty_score")
print("70B sapply Right base->instruct:", sap_right["meta_meta-llama-3-70b[0]"], "->", sap_right["meta_meta-llama-3-70b-instruct[0]"])
print("70B sapply Prog  base->instruct:", sap_prog["meta_meta-llama-3-70b[0]"], "->", sap_prog["meta_meta-llama-3-70b-instruct[0]"])
print("8B 8values Econ  base->instruct:", v8_econ["meta_meta-llama-3-8b[0]"], "->", v8_econ["meta_meta-llama-3-8b-instruct[0]"])
print("8B 8values Scty  base->instruct:", v8_scty["meta_meta-llama-3-8b[0]"], "->", v8_scty["meta_meta-llama-3-8b-instruct[0]"])

print("\n=== Phase 4 identity-performance artifact checks ===")
id_dir = RES / "identity_performance_dec"
pdf = id_dir / "vertopal.com_experimental-remediation.pdf"
print("identity_performance_dec pdf exists:", pdf.exists())
if pdf.exists():
    print("identity_performance_dec pdf size bytes:", pdf.stat().st_size)
