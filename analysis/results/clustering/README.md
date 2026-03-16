# Clustering comparison: 8Values R4 vs Political Compass R2

Method: KMeans(k=2), standardized features, random_state=42, n_init=50.

## Prompt-model level
- R2 silhouette: 0.5952
- R4 silhouette: 0.5359

## Model-mean level
- R2 silhouette: 0.4310
- R4 silhouette: 0.4090

Artifacts:
- clustering_comparison_metrics.csv
- labels_r2_pct_prompt_model.csv
- labels_r4_8val_prompt_model.csv
- labels_r2_pct_model_mean.csv
- labels_r4_8val_model_mean.csv
- figure: analysis/figures/clustering_8val4d_vs_pct2d_prompt_model.png
