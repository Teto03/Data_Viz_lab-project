"""
AI Impact on Student Performance — Data Analysis Script
For: "Does AI Boost Grades While Undermining Real Understanding?"
Authors: Francesco Bianchi, Hassan Faour
"""

import pandas as pd
import numpy as np
from scipy import stats

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
df1 = pd.read_csv('ai_impact_student_performance_dataset.csv')
df2 = pd.read_csv('Survey_AI.csv')
df3 = pd.read_csv('students_ai_usage.csv')

# ─────────────────────────────────────────────
# DERIVED VARIABLES
# ─────────────────────────────────────────────
# Dataset 1
df1['ai_tool_category'] = (
    df1['ai_tools_used']
    .fillna('None')
    .apply(lambda x: x.split('+')[0] if '+' in str(x) else x)
)
df1['dependency_quartile'] = pd.qcut(
    df1['ai_dependency_score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4']
)

# Dataset 2
feeling_map = {1: 'Curiosity', 2: 'Fear', 3: 'Indifference', 4: 'Trust'}
df2['feeling_label'] = df2['Q5.Feelings'].map(feeling_map)

# Dataset 3
df3['grade_delta'] = df3['grades_after_ai'] - df3['grades_before_ai']
df3['delta_direction'] = df3['grade_delta'].apply(
    lambda x: 'Positive' if x > 0 else 'Zero'
)

# Subsets
ai_users_d1 = df1[df1['uses_ai'] == 1]
non_users_d1 = df1[df1['uses_ai'] == 0]
ai_users_d3 = df3[df3['uses_ai'] == 'Yes']
non_users_d3 = df3[df3['uses_ai'] == 'No']

# ─────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────
print("=" * 60)
print("TAB 1 — OVERVIEW")
print("=" * 60)

# KPI 1: Average final score
kpi1_ai = ai_users_d1['final_score'].mean()
kpi1_non = non_users_d1['final_score'].mean()
t1, p1 = stats.ttest_ind(ai_users_d1['final_score'], non_users_d1['final_score'])
print(f"Avg Final Score  — AI users: {kpi1_ai:.2f} | Non-users: {kpi1_non:.2f} | p={p1:.4f}")

# KPI 2: Concept understanding
kpi2_ai = ai_users_d1['concept_understanding_score'].mean()
kpi2_non = non_users_d1['concept_understanding_score'].mean()
t2, p2 = stats.ttest_ind(ai_users_d1['concept_understanding_score'],
                          non_users_d1['concept_understanding_score'])
print(f"Avg Concept Understanding — AI users: {kpi2_ai:.2f} | Non-users: {kpi2_non:.2f} | p={p2:.4f}")

# KPI 3: Grade delta (from Dataset 3)
kpi3 = ai_users_d3['grade_delta'].mean()
print(f"Avg Grade Delta (AI adopters): +{kpi3:.2f} points")

# Bar chart data: AI vs Non-AI by final score and concept
print("\nBar chart — AI vs Non-AI (Final Score & Concept Understanding):")
bar_data = pd.DataFrame({
    'Group': ['AI Users', 'Non-Users'],
    'Final Score': [kpi1_ai, kpi1_non],
    'Concept Understanding': [kpi2_ai, kpi2_non],
    'N': [len(ai_users_d1), len(non_users_d1)]
})
print(bar_data.to_string(index=False))

# Donut: performance categories
print("\nDonut — Performance Category Distribution:")
print(df1['performance_category'].value_counts(normalize=True).round(3) * 100)

# ─────────────────────────────────────────────
# TAB 2 — THE PARADOX
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TAB 2 — THE PARADOX")
print("=" * 60)

# Grouped bar: final_score vs concept_understanding vs ai_dependency by performance category
paradox = df1.groupby('performance_category')[
    ['final_score', 'concept_understanding_score', 'ai_dependency_score']
].mean().round(2)
print("Grouped Bar — Scores by Performance Category:")
print(paradox)

# Ratio concept/final
paradox['concept_per_score_unit'] = (
    paradox['concept_understanding_score'] / paradox['final_score']
).round(4)
print("\nConcept Understanding per Final Score unit:")
print(paradox['concept_per_score_unit'])

# Scatter data: AI-generated content % vs concept understanding
corr_scatter = df1['ai_generated_content_percentage'].corr(
    df1['concept_understanding_score']
)
print(f"\nScatter correlation (AI gen content % vs concept_understanding): r={corr_scatter:.4f}")

# Check extreme groups
high_ai_content = df1[df1['ai_generated_content_percentage'] >= 75]
low_ai_content = df1[df1['ai_generated_content_percentage'] <= 25]
print(f"High AI content (>=75%) — concept mean: {high_ai_content['concept_understanding_score'].mean():.2f} (n={len(high_ai_content)})")
print(f"Low AI content (<=25%)  — concept mean: {low_ai_content['concept_understanding_score'].mean():.2f} (n={len(low_ai_content)})")

# ─────────────────────────────────────────────
# TAB 3 — DEPENDENCY LENS
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TAB 3 — DEPENDENCY LENS")
print("=" * 60)

df_ai_dep = ai_users_d1.copy()
df_ai_dep['dep_quartile'] = pd.qcut(
    df_ai_dep['ai_dependency_score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4']
)
df_ai_dep['ethics_quartile'] = pd.qcut(
    df_ai_dep['ai_ethics_score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4']
)

heatmap_data = df_ai_dep.groupby(
    ['dep_quartile', 'ethics_quartile']
)['concept_understanding_score'].mean().unstack().round(2)
print("Heatmap (dep_quartile × ethics_quartile → mean concept_understanding):")
print(heatmap_data)

print("\nConcept Understanding by Dependency Quartile:")
dep_summary = df_ai_dep.groupby('dep_quartile')[
    ['concept_understanding_score', 'final_score']
].mean().round(2)
print(dep_summary)

print("\nValue range in heatmap:", heatmap_data.values.min().round(2),
      "–", heatmap_data.values.max().round(2))

# ─────────────────────────────────────────────
# TAB 4 — GRADE DELTA
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TAB 4 — GRADE DELTA (Dataset 3)")
print("=" * 60)

print(f"AI users (n={len(ai_users_d3)}): mean delta = +{ai_users_d3['grade_delta'].mean():.2f}")
print(f"Non-users (n={len(non_users_d3)}): mean delta = {non_users_d3['grade_delta'].mean():.2f}")

print("\nGrade Delta by Purpose × Education Level:")
cross = ai_users_d3.groupby(
    ['purpose_of_ai', 'education_level']
)['grade_delta'].agg(['mean', 'count']).round(2)
print(cross)

print("\nSlope chart data — first 10 AI users:")
slope_data = ai_users_d3[
    ['grades_before_ai', 'grades_after_ai', 'grade_delta', 'purpose_of_ai', 'education_level']
].head(10)
print(slope_data.to_string(index=False))

# ─────────────────────────────────────────────
# TAB 5 — STUDENT PERCEPTIONS (Survey_AI)
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("TAB 5 — STUDENT PERCEPTIONS")
print("=" * 60)

print("Feelings by Year of Study (%):")
feelings_year = pd.crosstab(
    df2['feeling_label'], df2['Q13.Year_of_study'], normalize='columns'
).round(3) * 100
print(feelings_year)

print("\nOverall Feelings Distribution:")
print(df2['feeling_label'].value_counts(normalize=True).round(3) * 100)

risk_cols = [
    'Q3#1.AI_dehumanization', 'Q3#2.Job_replacement',
    'Q3#3.Problem_solving', 'Q3#4.AI_rulling_society'
]
print("\nRadar — Mean Risk Perceptions (1–5 scale):")
for col in risk_cols:
    label = col.split('.')[1]
    print(f"  {label}: {df2[col].mean():.2f}")

edu_cols = [
    'Q8.Advantage_teaching', 'Q9.Advantage_learning',
    'Q10.Advantage_evaluation ', 'Q11.Disadvantage_educational_process'
]
print("\nBar — Education Advantages/Disadvantages (mean):")
for col in edu_cols:
    label = col.strip().split('.')[1]
    print(f"  {label}: {df2[col].mean():.2f}")

print(f"\nUtility Grade (Q7): mean={df2['Q7.Utility_grade'].mean():.2f}, median={df2['Q7.Utility_grade'].median():.1f}")

# Gender split
gender_map = {1: 'Female', 2: 'Male'}
df2['gender_label'] = df2['Q12.Gender'].map(gender_map)
print("\nGender split:", df2['gender_label'].value_counts(normalize=True).round(3).to_dict())

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
