# MTMM-Style Construct Validity Analysis Using Cross-Test Trait Correlations

## Executive Summary

The multitrait–multimethod (MTMM) matrix proposed by Campbell and Fiske (1959) is a classical framework for assessing construct validity by jointly examining convergent and discriminant validity in a single correlation matrix. Convergent validity is evaluated primarily via correlations between different methods measuring the same trait (monotrait–heteromethod), whereas discriminant validity is evaluated by contrasting these with correlations between different traits measured either by the same or by different methods (heterotrait–monomethod and heterotrait–heteromethod).[^1][^2][^3][^4][^5][^6]

MTMM logic has been extended with latent variable models such as confirmatory factor analysis (CFA) and structural equation modeling (SEM), which decompose observed cross-test correlations into trait and method components and allow formal tests of hypotheses about convergent and discriminant validity. This report presents the core theory, notation, and equations for MTMM-style validity assessment, shows how cross-test trait correlations enter into the analysis, and illustrates the approach with worked numerical examples and notes on applications and limitations.[^2][^5][^6][^1]

## Construct Validity, Convergent, and Discriminant Validity

Construct validity concerns the degree to which a measure actually reflects the theoretical construct it is intended to represent. Campbell and Fiske argued that construct validity can be evaluated by demonstrating both convergent and discriminant validity using multiple traits and multiple methods.[^4][^7][^1][^2]

Convergent validity is the degree to which measures of the same construct, obtained via different methods, are strongly intercorrelated. Discriminant (or divergent) validity is the degree to which measures of different constructs are not excessively intercorrelated, especially when they share the same method or when both traits and methods differ.[^3][^5][^6][^4]

## MTMM Design and Notation

An MTMM design requires at least two traits and at least two methods, with each trait measured by each method. Let traits be indexed by \(i = 1,\dots, T\) and methods by \(j = 1,\dots, M\), and denote the observed score for trait \(i\) measured by method \(j\) as \(X_{ij}.\)[^5][^2][^4]

A simple latent-variable representation of an MTMM model is
\[
X_{ij} = \lambda^{(T)}_{ij} T_i + \lambda^{(M)}_{ij} M_j + \varepsilon_{ij},\tag{1}
\]
where \(T_i\) is the latent trait factor for trait \(i\), \(M_j\) is the latent method factor for method \(j\), \(\lambda^{(T)}_{ij}\) and \(\lambda^{(M)}_{ij}\) are loadings, and \(\varepsilon_{ij}\) is residual error.[^6][^1][^5]

Under standard assumptions (zero means, mutually uncorrelated errors, and independence of errors from traits and methods), the covariance between two observed indicators \(X_{ij}\) and \(X_{kl}\) is
\[
\operatorname{Cov}(X_{ij}, X_{kl}) = \lambda^{(T)}_{ij}\lambda^{(T)}_{kl}\operatorname{Cov}(T_i, T_k) + \lambda^{(M)}_{ij}\lambda^{(M)}_{kl}\operatorname{Cov}(M_j, M_l).\tag{2}
\]
This decomposition shows explicitly how cross-test correlations are driven by both trait correlations and method correlations.[^8][^1][^5]

## The MTMM Correlation Matrix and Correlation Types

The classical MTMM approach arranges the correlations among all \(X_{ij}\) into blocks defined by traits and methods. The main types of correlations are:[^1][^2][^4]

- **Reliability diagonal (monotrait–monomethod)**: reliability estimates of each measure placed on the main diagonal instead of 1.00 when possible.[^4]
- **Monotrait–heteromethod (MTHM)**: correlations between different methods measuring the same trait, for example \(r(X_{i1}, X_{i2})\).[^3][^6][^4]
- **Heterotrait–monomethod (HTMM)**: correlations between different traits measured by the same method, for example \(r(X_{11}, X_{21})\).[^2][^5][^4]
- **Heterotrait–heteromethod (HTHM)**: correlations between different traits measured by different methods, for example \(r(X_{11}, X_{22})\).[^5][^2][^4]

In Campbell and Fiske’s terminology, the MTHM correlations form the "validity diagonals" within off-diagonal method blocks, while HTMM and HTHM correlations populate the heterotrait triangles.[^7][^2][^4]

## Cross-Test Trait Correlations in MTMM Logic

"Cross-test trait correlations" refers to correlations between different observed tests (indicators) that reflect relationships among traits across methods. In an MTMM matrix, these include:[^2][^5]

- \(r(X_{ij}, X_{kj})\): same method \(j\), different traits \(i \neq k\), i.e., HTMM correlations dominated by trait correlations and method effects.[^4][^2]
- \(r(X_{ij}, X_{kl})\) with \(i \neq k\) and \(j \neq l\): HTHM correlations, in which similarity in traits and methods is lowest and thus expected to be relatively small if discriminant validity is adequate.[^5][^2][^4]

Comparing the magnitudes and patterns of these cross-test trait correlations with the monotrait–heteromethod validity diagonals is the essence of MTMM-style convergent and discriminant validity analysis.[^6][^3][^4]

## Convergent Validity: Monotrait–Heteromethod Correlations

In the MTMM framework, convergent validity is primarily evaluated via monotrait–heteromethod (MTHM) correlations, that is, correlations between different methods measuring the same trait.[^3][^6][^4]

Formally, for trait \(i\) measured by methods \(j\) and \(l\), the convergent validity coefficient is
\[
\rho^{\text{conv}}_{i;jl} = \operatorname{Corr}(X_{ij}, X_{il}).\tag{3}
\]
High and statistically significant values of \(\rho^{\text{conv}}_{i;jl}\) across method pairs provide evidence that the common variance in \(X_{ij}\) and \(X_{il}\) is due to the intended trait \(T_i\), not merely shared method characteristics.[^6][^3][^4]

In latent-variable terms, when the factor loadings on the trait factor are reasonably large and trait factors are correlated as expected, the correlations between trait factor scores across methods (or between latent trait factors linked to different methods) serve as convergent validity indices corrected for measurement error. Modern SEM approaches therefore examine convergent validity by inspecting trait factor correlations or by comparing trait factor loadings and average variance extracted (AVE) to error and method variance.[^5][^6]

## Discriminant Validity: Cross-Trait Correlations

Discriminant validity is evaluated by ensuring that correlations among different traits are lower than correlations among measures of the same trait. In MTMM terms this involves both:[^3][^4][^6]

- HTMM correlations: \(\operatorname{Corr}(X_{ij}, X_{kj})\) for \(i \neq k\), same method.[^2][^4]
- HTHM correlations: \(\operatorname{Corr}(X_{ij}, X_{kl})\) for \(i \neq k, j \neq l\), different traits and different methods.[^4][^2][^5]

Let
\[
\rho^{\text{htmm}}_{ik;j} = \operatorname{Corr}(X_{ij}, X_{kj}),\quad i \neq k,\tag{4}
\]
\[
\rho^{\text{hthm}}_{ik;jl} = \operatorname{Corr}(X_{ij}, X_{kl}),\quad i \neq k, j \neq l.\tag{5}
\]
Discriminant validity requires that, for each trait \(i\), the convergent validity coefficients \(\rho^{\text{conv}}_{i;jl}\) are substantively larger than all relevant \(\rho^{\text{htmm}}_{ik;j}\) and \(\rho^{\text{hthm}}_{ik;jl}.\)[^6][^3][^4]

At the latent level, discriminant validity is examined by looking at correlations between trait factors \(\operatorname{Corr}(T_i, T_k)\) and ensuring that they are not so high as to suggest the traits are empirically indistinguishable. Additional criteria such as the Fornell–Larcker criterion (AVE for each construct exceeding squared inter-construct correlations) and the heterotrait–monotrait (HTMT) ratio of trait correlations have been proposed, especially in SEM contexts, to formalize discriminant validity assessments.[^9][^10][^5][^6]

## Campbell and Fiske’s Classical Criteria

Campbell and Fiske proposed qualitative criteria for evaluating MTMM matrices that can be restated in terms of cross-test trait correlations.[^7][^2][^4]

Key criteria include:

1. **Nontrivial validity diagonals**: All MTHM correlations (validity diagonals) should be significantly greater than zero and of substantial magnitude.[^2][^4]
2. **Validity diagonals exceed heterotrait correlations in same heteromethod block**: Each convergent validity coefficient for a trait should be larger than all correlations involving other traits within the same methods block (local discriminant validity).[^7][^4][^2]
3. **Validity diagonals exceed heterotrait–monomethod correlations**: Convergent validity correlations for a trait should be larger than HTMM correlations in the same method block, suggesting that trait variance dominates method variance.[^4][^2]
4. **Similarity of trait intercorrelation patterns across methods**: The pattern of correlations among traits (i.e., their relative ordering and approximate magnitudes) should be similar across methods, indicating that methods do not drastically distort trait relationships.[^11][^2][^4]

These criteria rely heavily on comparing cross-test trait correlations both within and across methods to the monotrait–heteromethod validity diagonals.[^7][^2][^4]

## Worked Numerical Example (3 Traits × 3 Methods)

Consider an MTMM design with three traits (A, B, C) each measured by three methods (1, 2, 3), yielding observed variables \(A_1, A_2, A_3, B_1, B_2, B_3, C_1, C_2, C_3\). The table below presents a hypothetical correlation matrix organized by methods.

|        | A1  | B1  | C1  | A2  | B2  | C2  | A3  | B3  | C3  |
|--------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| A1     | .80 | .40 | .35 | .65 | .30 | .25 | .60 | .28 | .20 |
| B1     | .40 | .82 | .45 | .32 | .60 | .38 | .30 | .55 | .35 |
| C1     | .35 | .45 | .78 | .28 | .40 | .62 | .25 | .38 | .58 |
| A2     | .65 | .32 | .28 | .81 | .42 | .36 | .68 | .35 | .30 |
| B2     | .30 | .60 | .40 | .42 | .79 | .48 | .36 | .63 | .42 |
| C2     | .25 | .38 | .62 | .36 | .48 | .77 | .32 | .45 | .60 |
| A3     | .60 | .30 | .25 | .68 | .36 | .32 | .83 | .44 | .38 |
| B3     | .28 | .55 | .38 | .35 | .63 | .45 | .44 | .80 | .50 |
| C3     | .20 | .35 | .58 | .30 | .42 | .60 | .38 | .50 | .76 |

In this matrix, the reliability diagonal is approximated by the entries on the main diagonal (e.g., \(.80\) for \(A_1\), \(.81\) for \(A_2\), etc.), which would ideally be replaced by estimated reliabilities. The key validity diagonals (MTHM) for trait A are \(r(A_1, A_2) = .65\), \(r(A_1, A_3) = .60\), and \(r(A_2, A_3) = .68\), which are all substantial and higher than .50, supporting convergent validity for trait A.[^4]

For discriminant validity, cross-trait HTMM correlations for method 1 include \(r(A_1,B_1) = .40\), \(r(A_1,C_1) = .35\), and \(r(B_1,C_1) = .45\), all of which are smaller than the MTHM correlations for the corresponding traits, indicating that same-trait cross-method correlations dominate same-method cross-trait correlations. Similarly, HTHM correlations such as \(r(A_1,B_2) = .30\), \(r(A_2,B_3) = .35\), and \(r(B_1,C_2) = .38\) are generally lower than the validity diagonals, which supports discriminant validity across both traits and methods.[^6][^2][^4]

Finally, the pattern of trait intercorrelations appears consistent across methods: for each method, correlations between A and B and between B and C tend to be higher than correlations between A and C, suggesting a stable trait structure across methods, which satisfies Campbell and Fiske’s fourth criterion.[^11][^2][^4]

## SEM-Based MTMM Indices for Convergent and Discriminant Validity

Modern practice often analyzes MTMM data via CFA or more general SEM rather than purely descriptive MTMM matrices. In SEM, an MTMM model specifies latent trait factors \(T_i\) and method factors \(M_j\) with observed indicators \(X_{ij}\) as in equation (1), and computes the latent covariance matrix \(\operatorname{Corr}(T_1,\dots,T_T, M_1,\dots,M_M).\)[^8][^3][^5][^6]

Within this framework, convergent validity can be quantified using:

- **Trait factor loadings**: large and statistically significant \(\lambda^{(T)}_{ij}\) across methods for each trait.[^5][^6]
- **Average variance extracted (AVE)** for each trait, defined as
  \[
  \text{AVE}_i = \frac{\sum_j (\lambda^{(T)}_{ij})^2}{\sum_j (\lambda^{(T)}_{ij})^2 + \sum_j \operatorname{Var}(\varepsilon_{ij})},\tag{6}
  \]
  with values above about 0.50 often interpreted as adequate convergence.[^6]

Discriminant validity can then be tested via:

- **Latent trait correlations**: ensuring \(\operatorname{Corr}(T_i, T_k)\) is substantively below 1.0 and preferably below some threshold such as 0.85, indicating that traits are empirically distinct.[^5][^6]
- **Fornell–Larcker criterion**: for each pair of traits \(i\) and \(k\), discriminant validity holds if
  \[
  \text{AVE}_i > (\operatorname{Corr}(T_i, T_k))^2 \quad \text{and} \quad \text{AVE}_k > (\operatorname{Corr}(T_i, T_k))^2.\tag{7}
  \]
- **HTMT ratio of correlations**: defined for traits \(i\) and \(k\) as the ratio of the average of cross-trait correlations (heterotrait) to the geometric mean of within-trait correlations (monotrait), with suggested cutoffs such as 0.85 or 0.90.[^10][^9]

These indices operationalize the same logic as classical MTMM analysis—comparing cross-test trait correlations involving different traits with those involving the same trait—but in a latent-variable framework that adjusts for measurement error and can be tested statistically.[^10][^5][^6]

## Additive and Multiplicative Structures and Model-Specific Criteria

Reichardt and Coleman discussed two basic structures for MTMM data, additive and multiplicative, and showed that Campbell and Fiske’s qualitative criteria can be inadequate or misleading depending on which structure holds. In additive structures (as in equation (1)), trait and method effects sum to form observed scores, whereas in multiplicative structures traits and methods interact, altering the interpretation of cross-test correlations.[^10]

They argued that model-specific criteria for convergent and discriminant validity, derived from explicit latent-variable models of the MTMM data, provide more defensible inferences than purely descriptive rules applied to observed correlation matrices. This reinforces the contemporary practice of using SEM-based MTMM models, where convergent and discriminant validity can be evaluated via factor loadings, trait and method correlations, and fit indices rather than relying solely on visual inspection of cross-test trait correlations.[^10][^5][^6]

## Practical Steps for MTMM-Style Validity Analysis

When conducting MTMM-style construct validity analysis using cross-test trait correlations, a practical workflow is:

1. **Design**: Select at least two traits and two methods, ensuring that each trait is measured by each method (complete MTMM design where feasible).[^2][^4][^5]
2. **Data preparation**: Compute the full correlation matrix among all indicators, replacing diagonal entries with reliability estimates if available.[^4]
3. **Organize as MTMM matrix**: Arrange correlations by methods (or traits) into blocks that highlight MTHM, HTMM, and HTHM blocks.[^2][^4]
4. **Inspect convergent validity**: Identify MTHM validity diagonals and verify that they are substantially positive and larger than neighboring heterotrait correlations.[^3][^6][^4]
5. **Inspect discriminant validity**: Compare HTMM and HTHM cross-trait correlations to MTHM correlations and check for patterns where cross-trait correlations approach or exceed validity diagonals, which would threaten discriminant validity.[^6][^2][^4]
6. **Extend via SEM** (recommended): Fit an appropriate MTMM SEM (e.g., correlated traits–correlated methods, correlated traits–uncorrelated methods, or latent difference models) and assess trait loadings, trait and method factor correlations, AVE, HTMT, and overall model fit.[^8][^3][^5][^6]

These steps ensure that MTMM-style validity analysis makes systematic use of cross-test trait correlations rather than relying on isolated bivariate relationships.[^2][^4][^6]

## Applications

MTMM-style construct validity analysis has been widely used in psychological testing, personality assessment, educational measurement, and health outcomes research to separate trait variance from method variance and to evaluate the distinctiveness of related constructs. For example, studies assessing student achievement or self-concept across test formats (multiple-choice vs. constructed-response), rater perspectives (self vs. teacher vs. parent), or occasions often employ MTMM designs to examine whether trait structures replicate across methods while controlling for method effects.[^12][^13][^1][^11][^5][^2]

MTMM logic also underlies more complex designs such as multitrait–multimethod–multioccasion (MTMM-MO), where traits are measured across both multiple methods and multiple time points, and multilevel MTMM models, where data are additionally nested (e.g., students within classrooms). In these settings, cross-test trait correlations across methods, occasions, and levels are essential for determining whether constructs maintain their identity while allowing for method- and context-specific influences.[^13][^5]

## Limitations and Modern Perspectives

Classical MTMM matrix analysis is descriptive and can be ambiguous when different criteria conflict, when reliability is low, or when method effects are strong, making it difficult to draw clear conclusions solely from cross-test correlations. Moreover, Campbell and Fiske’s qualitative rules do not provide formal statistical tests and can fail under certain data-generating mechanisms, prompting calls for more rigorous model-based criteria.[^10][^5][^6]

Latent-variable MTMM models, including CFA and more general SEMs, address many of these limitations by separating trait, method, and error variance, allowing formal hypothesis testing and providing corrected estimates of trait correlations and validity coefficients. However, such models can be complex to specify and may suffer from identification problems, Heywood cases, or poor fit if the chosen structure does not match the data, so substantive theory and careful model comparison remain crucial.[^8][^3][^5][^6]

## Conclusion

MTMM-style construct validity analysis using cross-test trait correlations provides a powerful framework for jointly assessing convergent and discriminant validity of psychological and educational measures. By systematically comparing correlations among measures of the same trait across methods to correlations among different traits within and across methods, researchers can evaluate whether their measures capture intended constructs rather than artifacts of particular testing procedures or raters.[^1][^3][^4][^6][^2]

Modern SEM-based MTMM models extend this framework by decomposing observed correlations into trait and method components, enabling more precise and testable statements about convergent and discriminant validity while preserving the core insight of Campbell and Fiske’s original matrix approach.[^10][^5][^6]

---

## References

1. [Multitrait-multimethod matrix - Wikipedia](https://en.wikipedia.org/wiki/Multitrait-multimethod_matrix)

2. [157](https://conservancy.umn.edu/server/api/core/bitstreams/daebbb59-1d94-4580-833a-b6d7965dc6de/content)

3. [Examining Quadratic Relationships Between Traits and ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC6426770/) - Multitrait-multimethod (MTMM) analysis is one of the most frequently employed methods to examine the...

4. [Multitrait-Multimethod Matrix - Research Methods ...](https://conjointly.com/kb/multitrait-multimethod-matrix/) - Along with the MTMM, Campbell and Fiske introduced two new types of validity – convergent and discri...

5. [Examining Trait × Method Interactions Using Mixture Distribution Multitrait ...](https://pmc.ncbi.nlm.nih.gov/articles/PMC5624226/)

6. [[PDF] Convergent and Discriminant Validity Evaluation 1 - Mplus](https://www.statmodel.com/download/CDVC_LVM_BJMSP.pdf)

7. [Multitrait-Multimethod Matrix Validation | PDF](https://www.scribd.com/doc/59230335/1959-Campbell-D-T-Fiske-D-W-Convergent-and-ant-Validation-by-the-Multitrait-multimethod-Matrix-Psychological-Bulletin-56-2) - It outlines four key aspects of validity: 1) convergent validity shown through correlations between ...

8. [SEM: MTMM (David A. Kenny)](https://davidakenny.net/cm/mtmm.htm)

9. [How to assess discriminant validity in SEM (structural equation modeling)](https://www.youtube.com/watch?v=DgThpoiq_WQ) - This video describes the best way to assess discriminant validity in SEM using the AMOS software.  P...

10. [The Criteria for Convergent and Discriminant Validity in a ...](https://pubmed.ncbi.nlm.nih.gov/26790046/) - by CS Reichardt · 1995 · Cited by 82 — The well-known criteria for assessing convergent and discrimi...

11. [[PDF] A Multitrait-Multimethod Validity Investigation of the 2002 ...](https://www.umass.edu/remp/docs/MCAS-RR-5.pdf)

12. [[PDF] Multitrait-Multimethod Comparisons of Selected and Constructed ...](https://pages.uoregon.edu/stevensj/papers/mtmm.pdf)

13. [Multilevel Structural Equation Modeling of Multitrait ... - Refubium](https://refubium.fu-berlin.de/bitstream/handle/fub188/7141/Thesis_Koch_gedreht.pdf?sequence=1&isAllowed=y&save=y)

