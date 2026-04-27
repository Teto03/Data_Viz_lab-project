# data.py
import pandas as pd
# ─────────────────────────────────────────────────────────────
# LOAD & PREPROCESS
# ─────────────────────────────────────────────────────────────
# ── Dataset 1 — Aristovnik et al. 2024 (REAL, n=23 218) ──────
df1_raw = pd.read_excel("final_dataset.xlsx")
# Build all derived columns at once with pd.concat to avoid fragmentation warnings
_extra = pd.DataFrame({
    "used_chatgpt": df1_raw["Q13"].map({1.0: "Yes", 2.0: "No"}),
    "level_label":  df1_raw["Q8"].map(
        {1.0: "Bachelor", 2.0: "Master", 3.0: "PhD"}),
    "field_label":  df1_raw["Q10"].map({
        1.0: "Arts & Humanities", 2.0: "Social Sciences",
        3.0: "Applied Sciences",  4.0: "Natural Sciences"}),
    # Note: We can either import USE_LABELS from config, or map it directly here.
    # For simplicity, we rebuild the mapping to decouple Pandas from the UI.
    "use_label":    df1_raw["Q15"].map({1: "Rarely", 2: "Occasionally", 3: "Moderately", 4: "Considerably", 5: "Extensively"}),
}, index=df1_raw.index)
df1_raw = pd.concat([df1_raw, _extra], axis=1)
# Filter: only ChatGPT users (Q13==1) for usage-based tabs
df1_users = df1_raw[df1_raw["Q13"] == 1].copy()
# ── Dataset 2 — Survey_AI (REAL, n=91) ───────────────────────
df2 = pd.read_csv("Survey_AI.csv")
df2["feeling_label"] = df2["Q5.Feelings"].map(
    {1: "Curiosity", 2: "Fear", 3: "Indifference", 4: "Trust"})
df2 = df2.rename(columns={"Q10.Advantage_evaluation ": "Q10.Advantage_evaluation"})
# ── Dataset 3 — students_ai_usage (semi-synthetic, n=100) ────
df3 = pd.read_csv("students_ai_usage.csv")
df3["grade_delta"]     = df3["grades_after_ai"] - df3["grades_before_ai"]
df3["delta_direction"] = df3["grade_delta"].apply(
    lambda x: "Positive" if x > 0 else "Zero")
df3["sid"] = range(len(df3))
# ─────────────────────────────────────────────────────────────
# KPI CALCULATIONS
# ─────────────────────────────────────────────────────────────
adoption_pct = round(len(df1_users) / len(df1_raw) * 100, 1)
grade_gap_ext = round(
    df1_users[df1_users["Q15"] == 5]["Q27b"].mean() -
    df1_users[df1_users["Q15"] == 5]["Q29e"].mean(), 2)
grade_gap_rare = round(
    df1_users[df1_users["Q15"] == 1]["Q27b"].mean() -
    df1_users[df1_users["Q15"] == 1]["Q29e"].mean(), 2)
delta_ai = round(df3[df3["uses_ai"] == "Yes"]["grade_delta"].mean(), 2)
survey_utility = round(df2["Q7.Utility_grade"].mean(), 2)