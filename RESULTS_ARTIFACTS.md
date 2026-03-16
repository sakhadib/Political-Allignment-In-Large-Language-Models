# Results Artifacts Index

## anova/two_way_anova_effects.csv
- **File name:** two_way_anova_effects.csv
- **File location:** analysis/results/anova/two_way_anova_effects.csv
- **Description:** This file contains per-axis two-way ANOVA outputs for model identity and prompt variant effects. It includes effect sizes, p-values, and FDR-adjusted significance flags used for prompt-robustness claims.

## anova/two_way_anova_summary_matrix.csv
- **File name:** two_way_anova_summary_matrix.csv
- **File location:** analysis/results/anova/two_way_anova_summary_matrix.csv
- **Description:** This file is a compact matrix-style summary of ANOVA statistics across tests and axes. It is useful for quick comparison of eta-squared and significance values between factors.

## base_vs_instruct/_8values_scores.json
- **File name:** _8values_scores.json
- **File location:** analysis/results/base_vs_instruct/_8values_scores.json
- **Description:** This file stores 8Values scores for base and instruct variants of the Llama models. It is used to quantify alignment shifts across economic, diplomatic, government, and societal dimensions.

## base_vs_instruct/_pc_scores.json
- **File name:** _pc_scores.json
- **File location:** analysis/results/base_vs_instruct/_pc_scores.json
- **Description:** This file stores Political Compass scores for base and instruct variants of the Llama models. It provides direct evidence for changes in PCT economic and social positioning after instruction tuning.

## base_vs_instruct/_sapply_scores.json
- **File name:** _sapply_scores.json
- **File location:** analysis/results/base_vs_instruct/_sapply_scores.json
- **Description:** This file stores SapplyValues scores for base and instruct variants of the Llama models. It is used to measure shifts in right/left, authority, and progressivism traits after alignment.

## clustering/clustering_comparison_metrics.csv
- **File name:** clustering_comparison_metrics.csv
- **File location:** analysis/results/clustering/clustering_comparison_metrics.csv
- **Description:** This file reports clustering quality metrics for 2D PCT space and 4D 8Values space. It includes silhouette, Calinski-Harabasz, Davies-Bouldin, inertia, and sample/feature counts.

## clustering/labels_r2_pct_model_mean.csv
- **File name:** labels_r2_pct_model_mean.csv
- **File location:** analysis/results/clustering/labels_r2_pct_model_mean.csv
- **Description:** This file contains K-means cluster labels for model-mean points in the 2D PCT space. It shows which model belongs to which cluster after averaging over prompt variants.

## clustering/labels_r2_pct_prompt_model.csv
- **File name:** labels_r2_pct_prompt_model.csv
- **File location:** analysis/results/clustering/labels_r2_pct_prompt_model.csv
- **Description:** This file contains K-means cluster labels for every prompt-model instance in 2D PCT space. It is used to verify prompt-level cluster stability.

## clustering/labels_r4_8val_model_mean.csv
- **File name:** labels_r4_8val_model_mean.csv
- **File location:** analysis/results/clustering/labels_r4_8val_model_mean.csv
- **Description:** This file contains K-means cluster labels for model-mean points in the 4D 8Values space. It supports model-level separation analysis in higher-dimensional trait space.

## clustering/labels_r4_8val_prompt_model.csv
- **File name:** labels_r4_8val_prompt_model.csv
- **File location:** analysis/results/clustering/labels_r4_8val_prompt_model.csv
- **Description:** This file contains K-means cluster labels for every prompt-model instance in 4D 8Values space. It is used to assess whether cluster assignments remain invariant under paraphrase changes.

## clustering/README.md
- **File name:** README.md
- **File location:** analysis/results/clustering/README.md
- **Description:** This file documents the clustering artifacts and how they should be interpreted. It explains output files and summarizes the comparison setup.

## harmonized/scores_long.csv
- **File name:** scores_long.csv
- **File location:** analysis/results/harmonized/scores_long.csv
- **Description:** This file stores harmonized scores in long format for statistical modeling workflows. It is suitable for ANOVA pipelines and grouped analysis.

## harmonized/scores_wide.csv
- **File name:** scores_wide.csv
- **File location:** analysis/results/harmonized/scores_wide.csv
- **Description:** This file stores harmonized scores in wide format with one row per model-prompt instance. It is convenient for direct range checks and cross-axis comparisons.

## mtmm/mtmm_correlation_matrix.csv
- **File name:** mtmm_correlation_matrix.csv
- **File location:** analysis/results/mtmm/mtmm_correlation_matrix.csv
- **Description:** This file provides the baseline MTMM correlation matrix across methods and traits. It offers a global view of how psychometric proxies correlate before trait alignment filters.

## mtmm/mtmm_pairwise_correlations.csv
- **File name:** mtmm_pairwise_correlations.csv
- **File location:** analysis/results/mtmm/mtmm_pairwise_correlations.csv
- **Description:** This file contains pairwise MTMM correlations with relation-type labels and significance values. It is used for detailed convergent and discriminant validity checks.

## mtmm/mtmm_relation_summary.csv
- **File name:** mtmm_relation_summary.csv
- **File location:** analysis/results/mtmm/mtmm_relation_summary.csv
- **Description:** This file summarizes correlation behavior by MTMM relation class. It reports aggregate metrics such as mean and median correlation for each class.

## mtmm/mtmm_trait_aligned_correlation_matrix.csv
- **File name:** mtmm_trait_aligned_correlation_matrix.csv
- **File location:** analysis/results/mtmm/mtmm_trait_aligned_correlation_matrix.csv
- **Description:** This file provides the trait-aligned MTMM correlation matrix with direction-normalized constructs. It is used to inspect construct relationships after harmonized trait mapping.

## mtmm/mtmm_trait_aligned_pairwise_correlations.csv
- **File name:** mtmm_trait_aligned_pairwise_correlations.csv
- **File location:** analysis/results/mtmm/mtmm_trait_aligned_pairwise_correlations.csv
- **Description:** This file provides trait-aligned pairwise correlations, p-values, FDR corrections, and relation labels. It serves as the primary evidence table for construct validity claims.

## mtmm/mtmm_trait_aligned_relation_summary.csv
- **File name:** mtmm_trait_aligned_relation_summary.csv
- **File location:** analysis/results/mtmm/mtmm_trait_aligned_relation_summary.csv
- **Description:** This file summarizes trait-aligned correlation classes and their significance fractions. It supports concise reporting of convergent versus heterotrait patterns.
