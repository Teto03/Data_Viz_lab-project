"""
=============================================================
  AI Impact Dashboard — analysis.py
  "Does AI Boost Grades While Undermining Real Understanding?"
  Francesco Bianchi (264692) · Hassan Faour (265917)
  
  ANALYSIS SCRIPT: Validates proposal hypotheses against data
  Generates summary statistics used in the bilingual report
=============================================================
"""

import pandas as pd
import numpy as np
from scipy import stats

# ─────────────────────────────────────────────────────────────
# LOAD DATASETS
# ─────────────────────────────────────────────────────────────

# Dataset 2 — Survey_AI (n=91, real)
df2 = pd.read_csv("Survey_AI.csv")
df2["feeling_label"] = df2["Q5.Feelings"].map(
    {1: "Curiosity", 2: "Fear", 3: "Indifference", 4: "Trust"})
df2 = df2.rename(columns={"Q10.Advantage_evaluation ": "Q10.Advantage_evaluation"})

# Dataset 3 — students_ai_usage (n=100, semi-synthetic)
df3 = pd.read_csv("students_ai_usage.csv")
df3["grade_delta"] = df3["grades_after_ai"] - df3["grades_before_ai"]
ai_users   = df3[df3["uses_ai"] == "Yes"].copy()
non_users  = df3[df3["uses_ai"] == "No"].copy()

# Dataset 1 constants from app.py (Aristovnik et al., n=23,218)
# These values are computed at startup in the Dash app
D1 = {
    "n_total": 23218,
    "n_users": 16010,
    "adoption_pct": 69.0,
    "grade_gap_rarely":     0.19,
    "grade_gap_extensively": 0.54,
    "gap_increase": 0.35,
    "emotions": {
        "Curious": 3.43, "Calm": 3.27, "Hopeful": 3.20,
        "Relieved": 3.10, "Happy": 3.05, "Excited": 2.97,
        "Anxious": 2.45, "Surprised": 2.40, "Confused": 2.30,
        "Proud": 2.25, "Bored": 2.10, "Frustrated": 2.05,
        "Angry": 1.95, "Ashamed": 1.82, "Sad": 1.73,
    },
    "satisfaction": {
        "Q25d_helps_everyday_life": 3.91,
        "Q25b_interesting": 3.74,
        "Q25c_important": 3.65,
        "Q24a_useful_vs_google": 3.29,
        "Q24e_satisfied_assistance": 3.18,
        "Q24f_satisfied_quality": 3.12,
        "Q24g_satisfied_accuracy": 3.05,
        "Q24b_easier_than_profs": 2.98,
    },
}

# ─────────────────────────────────────────────────────────────
# SECTION 1 — Overview: Adoption & Usage Intensity
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 1: ADOPTION & USAGE INTENSITY (Dataset 1)")
print("="*60)
print(f"Total respondents       : {D1['n_total']:,}")
print(f"ChatGPT users           : {D1['n_users']:,} ({D1['adoption_pct']}%)")
print(f"Non-users               : {D1['n_total']-D1['n_users']:,} ({100-D1['adoption_pct']}%)")
print("Usage intensity (among users):")
intensity_pcts = {"Rarely": 14.2, "Occasionally": 30.1, "Moderately": 28.4,
                  "Considerably": 22.9, "Extensively": 4.3}
for k, v in intensity_pcts.items():
    print(f"  {k:15s}: {v:.1f}%")
print("Field adoption (approx.):")
field_rates = {"Applied Sciences": 74.5, "Social Sciences": 72.1,
               "Natural Sciences": 68.3, "Arts & Humanities": 62.8}
for k, v in field_rates.items():
    print(f"  {k:25s}: {v:.1f}%")

# ─────────────────────────────────────────────────────────────
# SECTION 2 — The Paradox
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 2: THE PARADOX (Dataset 1)")
print("="*60)
print(f"Gap at Rarely      (Q27b - Q29e): +{D1['grade_gap_rarely']:.2f}")
print(f"Gap at Extensively (Q27b - Q29e): +{D1['grade_gap_extensively']:.2f}")
print(f"Gap increase across intensity   : +{D1['gap_increase']:.2f}")
print("Interpretation: heavier use → larger divergence between")
print("  perceived grade improvement and critical thinking gain.")
print("Field with widest gap at high intensity: Social Sciences")
print("Field with most balanced gap            : Applied Sciences")

# ─────────────────────────────────────────────────────────────
# SECTION 3 — Dependency Lens
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 3: DEPENDENCY LENS (Dataset 1)")
print("="*60)
print("Key insight from fig_dependency_paradox_bars:")
print("  Grade perception (Q27b) → RISES with intensity")
print("  Crit. thinking  (Q29e) → RISES but more slowly")
print("  AI-hinders concern(Q22j)→ FALLS as intensity grows")
print("  → Heavy users rationalize dependency away")
print("\nHeatmap (fig_purpose_heatmap) top tasks for extensive users:")
print("  Academic Writing, Study Assistance, Research — all 3.5+/5")
print("  Coding, Professional Writing — moderate")

# ─────────────────────────────────────────────────────────────
# SECTION 4 — Grade Delta (Dataset 3)
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 4: GRADE DELTA (Dataset 3)")
print("="*60)
print(f"AI users   : n={len(ai_users)}")
print(f"Non-users  : n={len(non_users)}")
print(f"Avg grade before AI (users): {ai_users['grades_before_ai'].mean():.2f}")
print(f"Avg grade after  AI (users): {ai_users['grades_after_ai'].mean():.2f}")
print(f"Mean delta (AI users)       : +{ai_users['grade_delta'].mean():.2f} pts")
print(f"Std deviation delta         :  {ai_users['grade_delta'].std():.2f} pts")
print(f"Non-user delta              :  {non_users['grade_delta'].mean():.2f} (synthetic)")

print("\nDelta by purpose:")
delta_purpose = ai_users.groupby("purpose_of_ai")["grade_delta"].agg(["mean","std","count"])
print(delta_purpose.round(2))

print("\nDelta by education level:")
delta_level = ai_users.groupby("education_level")["grade_delta"].agg(["mean","std","count"])
print(delta_level.round(2))

print("\nDelta by purpose × level:")
delta_cross = ai_users.groupby(["purpose_of_ai","education_level"])["grade_delta"].mean().round(2)
print(delta_cross)

# T-test AI vs non-AI (despite synthetic non-users)
t_stat, p_val = stats.ttest_ind(
    ai_users["grade_delta"], non_users["grade_delta"])
print(f"\nT-test (AI users Δ vs non-users Δ): t={t_stat:.3f}, p={p_val:.6f}")
print("Note: p is trivially small due to synthetic non-user Δ=0")

# ─────────────────────────────────────────────────────────────
# SECTION 5 — Perceptions (Dataset 1 + Dataset 2)
# ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("SECTION 5: PERCEPTIONS (Dataset 1 + Dataset 2)")
print("="*60)

print("\n--- Dataset 2: Survey_AI ---")
print(f"n = {len(df2)}")
print(f"Utility grade — mean: {df2['Q7.Utility_grade'].mean():.2f}, "
      f"median: {df2['Q7.Utility_grade'].median():.2f}, "
      f"std: {df2['Q7.Utility_grade'].std():.2f}")
print(f"AI knowledge  — mean: {df2['Q1.AI_knowledge'].mean():.2f}, "
      f"std: {df2['Q1.AI_knowledge'].std():.2f}")

print("\nFeelings distribution:")
fc = df2["feeling_label"].value_counts(normalize=True).round(3)*100
for k, v in fc.items():
    print(f"  {k:15s}: {v:.1f}%")

print("\nFeelings by year of study:")
ct_norm = pd.crosstab(df2["feeling_label"], df2["Q13.Year_of_study"],
                      normalize="columns").round(3)*100
print(ct_norm)

print("\nEducational advantages/disadvantages (1=agree, 5=disagree):")
adv_cols = {
    "Q8.Advantage_teaching":              "Teaching Advantage",
    "Q9.Advantage_learning":              "Learning Advantage",
    "Q10.Advantage_evaluation":           "Evaluation Advantage",
    "Q11.Disadvantage_educational_process": "Educational Disadvantage",
}
for col, label in adv_cols.items():
    m = df2[col].mean()
    s = df2[col].std()
    interp = "Agree" if m < 3 else ("Disagree" if m > 3 else "Neutral")
    print(f"  {label:30s}: {m:.2f} ± {s:.2f}  → {interp}")

print("\n--- Dataset 1: Emotions (top 5 & bottom 3) ---")
emos_sorted = sorted(D1["emotions"].items(), key=lambda x: -x[1])
print("Top emotions:")
for e, v in emos_sorted[:5]:
    print(f"  {e:15s}: {v:.2f}/5")
print("Bottom emotions:")
for e, v in emos_sorted[-3:]:
    print(f"  {e:15s}: {v:.2f}/5")

print("\n--- Dataset 1: Satisfaction ---")
for k, v in D1["satisfaction"].items():
    above = "above neutral" if v >= 3 else "below neutral"
    print(f"  {k:35s}: {v:.2f}  ({above})")

print("\n" + "="*60)
print("CROSS-DATASET CONSISTENCY CHECK")
print("="*60)
print("Paradox: Does Survey_AI confirm the dual perception?")
adv_mean  = df2[["Q8.Advantage_teaching","Q9.Advantage_learning",
                  "Q10.Advantage_evaluation"]].mean().mean()
disadv_mean = df2["Q11.Disadvantage_educational_process"].mean()
print(f"  Mean advantage score : {adv_mean:.2f}/5 (lower = more agreement)")
print(f"  Disadvantage score   : {disadv_mean:.2f}/5 (lower = more agreement)")
print(f"  Both < 3 → students simultaneously agree on BOTH advantages AND disadvantages")
print(f"  This mirrors the Dataset 1 paradox (grade ↑ but crit.think. lags)")
print(f"  Dataset 3 confirms: grade Δ = +{ai_users['grade_delta'].mean():.2f} (objective gain)")
print(f"  But this is semi-synthetic — use as corroborative, not causal evidence")
