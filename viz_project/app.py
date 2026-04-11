"""
=============================================================
  AI Impact Dashboard — app.py  (v2 — fixed)
  "Does AI Boost Grades While Undermining Real Understanding?"
  Francesco Bianchi (264692) · Hassan Faour (265917)
=============================================================
  Datasets:
    df1  →  final_dataset.xlsx   (Aristovnik et al., n=23 218, REALE)
    df2  →  Survey_AI.csv        (n=91, reale)
    df3  →  students_ai_usage.csv (n=100, semi-sintetico)
  Run:  python app.py
  Open: http://127.0.0.1:8050
=============================================================
"""
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# 0. PALETTE & THEME
# ─────────────────────────────────────────────────────────────
BG      = "#0D1B2A"
CARD    = "#132338"
TEAL    = "#2DD4BF"
AMBER   = "#FBBF24"
RED     = "#F87171"
GREEN   = "#34D399"
GREY    = "#64748B"
GRIDD   = "#1E2D3D"
TEXT    = "#F1F5F9"
SUBTEXT = "#94A3B8"
PURP    = "#A78BFA"

FEEL_COL = {"Curiosity": TEAL, "Trust": GREEN, "Indifference": GREY, "Fear": RED}
PURP_COL = {"Research": TEAL, "Coding": AMBER, "Homework": GREY}
FIELD_COL = {
    "Arts & Humanities": PURP,
    "Social Sciences":   TEAL,
    "Applied Sciences":  AMBER,
    "Natural Sciences":  GREEN,
}
USE_LABELS = {1: "Rarely", 2: "Occasionally", 3: "Moderately",
              4: "Considerably", 5: "Extensively"}

def base_layout(title="", height=420):
    return dict(
        height=height,
        title=dict(text=title, font=dict(size=14, color=TEXT), x=0.02),
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(family="'DM Sans', sans-serif", color=TEXT, size=11),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=GRIDD,
                    font=dict(color=SUBTEXT)),
        margin=dict(l=52, r=32, t=52, b=48),
        xaxis=dict(gridcolor=GRIDD, zerolinecolor=GRIDD, tickfont=dict(color=SUBTEXT)),
        yaxis=dict(gridcolor=GRIDD, zerolinecolor=GRIDD, tickfont=dict(color=SUBTEXT)),
    )

# ─────────────────────────────────────────────────────────────
# 1. LOAD & PREPROCESS
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
    "use_label":    df1_raw["Q15"].map(USE_LABELS),
}, index=df1_raw.index)

df1_raw = pd.concat([df1_raw, _extra], axis=1)

# Filter: only ChatGPT users (Q13==1) for usage-based tabs
# NOTE: must be defined BEFORE any function that references df1_users
df1_users = df1_raw[df1_raw["Q13"] == 1].copy()

# ── Dataset 2 — Survey_AI (REAL, n=91) ───────────────────────
df2 = pd.read_csv("Survey_AI.csv")
df2["feeling_label"] = df2["Q5.Feelings"].map(
    {1: "Curiosity", 2: "Fear", 3: "Indifference", 4: "Trust"})
df2 = df2.rename(columns={"Q10.Advantage_evaluation ": "Q10.Advantage_evaluation"})

# ── Dataset 3 — students_ai_usage (semi-sintetico, n=100) ────
df3 = pd.read_csv("students_ai_usage.csv")
df3["grade_delta"]     = df3["grades_after_ai"] - df3["grades_before_ai"]
df3["delta_direction"] = df3["grade_delta"].apply(
    lambda x: "Positive" if x > 0 else "Zero")
df3["sid"] = range(len(df3))

# ─────────────────────────────────────────────────────────────
# 2. KPI HELPER
# ─────────────────────────────────────────────────────────────
def kpi_card(label, value, sub="", color=TEAL):
    return html.Div(style={
        "background": CARD, "borderRadius": "12px", "padding": "20px 24px",
        "borderLeft": f"4px solid {color}", "minWidth": "0",
    }, children=[
        html.Div(label, style={"color": SUBTEXT, "fontSize": "12px",
                               "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.Div(str(value), style={"color": color, "fontSize": "32px",
                                    "fontWeight": "700", "lineHeight": "1.2"}),
        html.Div(sub, style={"color": SUBTEXT, "fontSize": "12px", "marginTop": "4px"}),
    ])

# ─────────────────────────────────────────────────────────────
# 3. TAB 1 — OVERVIEW  (Dataset 1 globale)
# ─────────────────────────────────────────────────────────────
def fig_adoption_donut():
    counts = df1_raw["used_chatgpt"].value_counts()
    colors = [TEAL if c == "Yes" else GREY for c in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.60,
        marker_colors=colors,
        textinfo="label+percent",
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>%{value} studenti (%{percent})<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(x=0.5, y=0.5,
                       text="<b>23 218</b><br>studenti",
                       showarrow=False, font=dict(size=13, color=TEXT))
    fig.update_layout(**base_layout("ChatGPT Adoption  (Dataset 1, n=23 218, 109 paesi)"))
    return fig

def fig_usage_intensity_bar():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    counts = df1_users["Q15"].value_counts().reindex(order).fillna(0).astype(int)
    pcts   = (counts / counts.sum() * 100).round(1)
    colors = [GREY, GREY, TEAL, AMBER, RED]
    fig = go.Figure(go.Bar(
        x=labels,
        y=pcts.values,
        marker_color=colors,
        text=[f"{v:.1f}%" for v in pcts.values],
        textposition="outside",
        textfont=dict(color=TEXT),
        hovertemplate="%{x}<br>%{y:.1f}% degli utenti<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        "Intensità d'uso di ChatGPT  (solo utenti, n=16 010)"))
    fig.update_yaxes(title="% utenti ChatGPT", range=[0, 42])
    fig.update_xaxes(title="")
    return fig

def fig_field_adoption():
    grp = (df1_raw.dropna(subset=["field_label"])
               .groupby("field_label")["Q13"]
               .apply(lambda x: (x == 1).mean() * 100)
               .round(1)
               .sort_values(ascending=True)
               .reset_index())
    grp.columns = ["Field", "AdoptionPct"]
    fig = go.Figure(go.Bar(
        x=grp["AdoptionPct"],
        y=grp["Field"],
        orientation="h",
        marker_color=[FIELD_COL.get(f, GREY) for f in grp["Field"]],
        text=[f"{v:.1f}%" for v in grp["AdoptionPct"]],
        textposition="outside",
        textfont=dict(color=TEXT),
        hovertemplate="%{y}: %{x:.1f}% adoption<extra></extra>",
    ))
    fig.update_layout(**base_layout("Tasso di adozione per campo di studi", height=300))
    fig.update_xaxes(title="% studenti che usano ChatGPT", range=[0, 85])
    fig.update_yaxes(title="")
    return fig

# ─────────────────────────────────────────────────────────────
# 4. TAB 2 — THE PARADOX  (Dataset 1: il vero segnale)
# ─────────────────────────────────────────────────────────────
def fig_paradox_lines():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    grades_mean = df1_users.groupby("Q15")["Q27b"].mean().reindex(order).round(2)
    crit_mean   = df1_users.groupby("Q15")["Q29e"].mean().reindex(order).round(2)
    gap         = (grades_mean - crit_mean).round(2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=grades_mean.values,
        mode="lines+markers+text",
        name="Perceived Grade Improvement (Q27b)",
        line=dict(color=TEAL, width=3),
        marker=dict(size=10, color=TEAL),
        text=[f"{v:.2f}" for v in grades_mean.values],
        textposition="top center",
        textfont=dict(color=TEAL, size=11),
        hovertemplate="Intensità: %{x}<br>Voti percepiti: %{y:.2f}/5<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=crit_mean.values,
        mode="lines+markers+text",
        name="Perceived Critical Thinking Gain (Q29e)",
        line=dict(color=RED, width=3),
        marker=dict(size=10, color=RED),
        text=[f"{v:.2f}" for v in crit_mean.values],
        textposition="bottom center",
        textfont=dict(color=RED, size=11),
        hovertemplate="Intensità: %{x}<br>Critical thinking: %{y:.2f}/5<extra></extra>",
    ))
    for i, (x, g, c, gp) in enumerate(zip(labels, grades_mean, crit_mean, gap)):
        fig.add_shape(type="line",
                      x0=x, x1=x, y0=c, y1=g,
                      line=dict(color=AMBER, width=1.5, dash="dot"))
        if i == 4:
            fig.add_annotation(
                x=x, y=(g + c) / 2,
                text=f"  Gap = {gp:.2f}",
                showarrow=False,
                font=dict(color=AMBER, size=11),
                xanchor="left",
            )
    fig.add_annotation(
        x="Rarely", y=(grades_mean[1] + crit_mean[1]) / 2,
        text=f"Gap = {gap[1]:.2f}",
        showarrow=False,
        font=dict(color=AMBER, size=11),
        xanchor="right",
    )
    fig.add_annotation(
        x="Moderately", y=4.3,
        text="<b>Il gap si allarga con l'intensità d'uso</b><br>"
             "Più si usa ChatGPT → più si percepisce un vantaggio sui voti<br>"
             "ma il beneficio sul critical thinking cresce meno",
        showarrow=False,
        font=dict(color=AMBER, size=10),
        bgcolor=CARD, bordercolor=AMBER, borderwidth=1, borderpad=6,
        align="center",
    )
    fig.update_layout(**base_layout(
        "Il Paradosso — Voti vs Critical Thinking per Intensità d'uso  "
        "(Dataset 1, n=16 010, scala 1–5)", height=480))
    fig.update_yaxes(title="Accordo medio (1=disaccordo, 5=accordo)", range=[2.3, 4.8])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

def fig_hinder_vs_grades():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    fields = ["Arts & Humanities", "Social Sciences",
              "Applied Sciences", "Natural Sciences"]
    fig = go.Figure()
    for field in fields:
        sub = df1_users[df1_users["field_label"] == field]
        grp = sub.groupby("Q15")[["Q27b", "Q29e"]].mean().reindex(order)
        gap = (grp["Q27b"] - grp["Q29e"]).round(3)
        fig.add_trace(go.Scatter(
            x=labels,
            y=gap.values,
            mode="lines+markers",
            name=field,
            line=dict(color=FIELD_COL.get(field, GREY), width=2),
            marker=dict(size=8, color=FIELD_COL.get(field, GREY)),
            hovertemplate=f"<b>{field}</b><br>Intensità: %{{x}}<br>"
                          f"Gap (voti−crit.think.): %{{y:.2f}}<extra></extra>",
        ))
    fig.add_hline(y=0, line_dash="dot", line_color=GREY,
                  annotation_text="Nessun gap (voti = critical thinking)",
                  annotation_font_color=GREY, annotation_font_size=9)
    fig.update_layout(**base_layout(
        "Gap (Voti − Critical Thinking) per Campo di Studi × Intensità d'uso",
        height=420))
    fig.update_yaxes(title="Gap percepito (Q27b − Q29e)", range=[-0.1, 0.8])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

# ─────────────────────────────────────────────────────────────
# 5. TAB 3 — PURPOSE & DEPENDENCY  (Dataset 1)
# ─────────────────────────────────────────────────────────────
def fig_purpose_heatmap():
    q18_cols   = [f"Q18{c}" for c in "abcdefghijkl"]
    q18_labels = ["Academic writing", "Professional writing", "Creative writing",
                  "Proofreading", "Brainstorming", "Translating",
                  "Summarizing", "Calculating", "Study assistance",
                  "Personal assistance", "Research", "Coding"]
    order = [1, 2, 3, 4, 5]
    grp   = df1_users.groupby("Q15")[q18_cols].mean().reindex(order).round(2)
    fig = go.Figure(go.Heatmap(
        z=grp.values.T,
        x=[USE_LABELS[i] for i in order],
        y=q18_labels,
        colorscale=[[0.0, CARD], [0.5, "#1E6B74"], [1.0, TEAL]],
        zmin=1, zmax=4,
        texttemplate="%{z}",
        textfont=dict(color=TEXT, size=10),
        hovertemplate="Intensità: %{x}<br>Task: %{y}<br>Media: %{z}<extra></extra>",
        colorbar=dict(
            title=dict(text="Freq.<br>(1–5)", font=dict(color=SUBTEXT)),
            tickfont=dict(color=SUBTEXT)
        ),
    ))
    fig.update_layout(**base_layout(
        "Frequenza d'uso per Task × Intensità  (Dataset 1, scala 1=Never, 5=Always)",
        height=480))
    fig.update_xaxes(title="Intensità d'uso generale (Q15)")
    fig.update_yaxes(title="")
    return fig

def fig_dependency_paradox_bars():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    g_vals  = df1_users.groupby("Q15")["Q27b"].mean().reindex(order).round(2)
    ct_vals = df1_users.groupby("Q15")["Q29e"].mean().reindex(order).round(2)
    hd_vals = df1_users.groupby("Q15")["Q22j"].mean().reindex(order).round(2)
    fig = go.Figure()
    for name, vals, col, offset in [
        ("Perceived Grade Improvement",   g_vals,  TEAL,  -0.27),
        ("Perceived Critical Thinking",   ct_vals, RED,    0.00),
        ("Concern: AI Hinders Learning",  hd_vals, AMBER,  0.27),
    ]:
        fig.add_trace(go.Bar(
            name=name,
            x=labels,
            y=vals.values,
            marker_color=col,
            text=[f"{v:.2f}" for v in vals.values],
            textposition="outside",
            textfont=dict(color=TEXT, size=9),
            width=0.26,
            offset=offset,
        ))
    fig.update_layout(**base_layout(
        "Tre metriche chiave per Intensità d'uso  (Dataset 1, scala 1–5)",
        height=440), barmode="overlay")
    fig.update_yaxes(title="Accordo medio (scala Likert 1–5)", range=[2.4, 4.7])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

# ─────────────────────────────────────────────────────────────
# 6. TAB 4 — GRADE DELTA  (Dataset 3)
# ─────────────────────────────────────────────────────────────
def fig_slope_chart():
    ai_d3  = df3[df3["uses_ai"] == "Yes"].copy()
    non_d3 = df3[df3["uses_ai"] == "No"].copy()
    fig = go.Figure()
    shown_non = False
    for _, row in non_d3.iterrows():
        fig.add_trace(go.Scatter(
            x=["Before AI", "After AI"],
            y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines",
            line=dict(color=GREY, width=1.2),
            opacity=0.25,
            showlegend=not shown_non,
            name="Non-Users (Δ=0)",
            legendgroup="non",
            hovertemplate="Grade: %{y}<extra>Non-User</extra>",
        ))
        shown_non = True
    shown = set()
    for _, row in ai_d3.iterrows():
        purpose = str(row.get("purpose_of_ai", "Unknown"))
        col = PURP_COL.get(purpose, TEAL)
        fig.add_trace(go.Scatter(
            x=["Before AI", "After AI"],
            y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines+markers",
            line=dict(color=col, width=2),
            marker=dict(size=6, color=col),
            opacity=0.75,
            showlegend=purpose not in shown,
            name=f"AI – {purpose}",
            legendgroup=purpose,
            hovertemplate=(
                f"<b>{purpose}</b><br>Grade: %{{y}}<br>"
                f"Δ = +{row['grade_delta']:.0f} pt<extra></extra>"
            ),
        ))
        shown.add(purpose)
    fig.add_annotation(
        x=1, y=ai_d3["grades_after_ai"].max() + 2,
        text=f"<b>Avg Δ AI users: +{ai_d3['grade_delta'].mean():.2f} pt</b>",
        showarrow=False, font=dict(color=GREEN, size=13),
        bgcolor=CARD, bordercolor=GREEN, borderwidth=1, borderpad=6,
    )
    fig.add_annotation(
        x=1, y=non_d3["grades_after_ai"].min() - 3,
        text="⚠ Non-users Δ=0 is a synthetic artifact",
        showarrow=False, font=dict(color=AMBER, size=9),
    )
    fig.update_layout(**base_layout(
        "Slope Chart: Grades Before → After AI adoption  (Dataset 3, n=100)",
        height=480))
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Grade", range=[30, 110])
    return fig

def fig_delta_by_purpose():
    ai_d3 = df3[df3["uses_ai"] == "Yes"].copy()
    grp = (ai_d3.groupby(["purpose_of_ai", "education_level"])["grade_delta"]
               .mean().round(2).reset_index())
    grp.columns = ["Purpose", "Level", "Delta"]
    fig = px.bar(
        grp, x="Purpose", y="Delta", color="Level", barmode="group",
        text="Delta",
        color_discrete_map={"college": TEAL, "school": AMBER},
    )
    fig.update_traces(textposition="outside", textfont=dict(color=TEXT))
    fig.update_layout(**base_layout(
        "Grade Delta by Purpose × Education Level  (AI Users only)"))
    fig.update_yaxes(title="Avg Grade Δ", range=[0, 15])
    fig.update_xaxes(title="")
    return fig

# ─────────────────────────────────────────────────────────────
# 7. TAB 5 — PERCEPTIONS  (Dataset 1 globale + Dataset 2)
# ─────────────────────────────────────────────────────────────
def fig_emotions_radar():
    emo_cols = [f"Q32{c}" for c in "abcdefghijklmno"]
    emo_labels = ["Bored", "Hopeful", "Sad", "Ashamed", "Calm",
                  "Angry", "Relieved", "Happy", "Proud", "Anxious",
                  "Surprised", "Curious", "Excited", "Confused", "Frustrated"]
    vals = df1_users[emo_cols].mean().round(2).tolist()
    vals_c = vals + [vals[0]]
    labs_c = emo_labels + [emo_labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_c, theta=labs_c,
        fill="toself",
        fillcolor="rgba(45,212,191,0.12)",
        line=dict(color=TEAL, width=2),
        marker=dict(color=TEAL, size=6),
        name="Mean emotion",
        hovertemplate="%{theta}: <b>%{r:.2f}/5</b><extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[3.0] * len(labs_c), theta=labs_c,
        fill="toself",
        fillcolor="rgba(100,116,139,0.06)",
        line=dict(color=GREY, width=1, dash="dot"),
        name="Neutral (3.0/5)",
    ))
    fig.update_layout(
        **base_layout("Emozioni provate usando ChatGPT  (Dataset 1, n=16 010, 1=Never 5=Always)",
                      height=460),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[1, 5], gridcolor=GRIDD,
                            tickfont=dict(color=SUBTEXT), tickvals=[1, 2, 3, 4, 5]),
            angularaxis=dict(gridcolor=GRIDD, tickfont=dict(color=TEXT, size=9)),
        ),
    )
    return fig

def fig_satisfaction_bars():
    items = {
        "Q24a": "More useful than Google",
        "Q24b": "Easier than talking to professors",
        "Q24e": "Satisfied – level of assistance",
        "Q24f": "Satisfied – quality of info",
        "Q24g": "Satisfied – accuracy",
        "Q25b": "Using ChatGPT is interesting",
        "Q25c": "Being able to use it is important",
        "Q25d": "Helps in everyday life",
    }
    vals   = {k: df1_users[k].mean().round(2) for k in items}
    labels = list(items.values())
    means  = list(vals.values())
    colors = [TEAL if v >= 3.0 else RED for v in means]
    fig = go.Figure(go.Bar(
        x=means,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.2f}" for v in means],
        textposition="outside",
        textfont=dict(color=TEXT),
        hovertemplate="%{y}<br>Media: %{x:.2f}/5<extra></extra>",
    ))
    fig.add_vline(x=3.0, line_dash="dot", line_color=AMBER,
                  annotation_text="Neutral (3/5)",
                  annotation_font_color=AMBER, annotation_font_size=9)
    fig.update_layout(**base_layout(
        "Soddisfazione & Attitudine verso ChatGPT  (Dataset 1, scala 1–5)",
        height=380))
    fig.update_xaxes(title="Accordo medio", range=[1, 5])
    fig.update_yaxes(title="")
    return fig

def fig_feelings_stacked():
    order_feel = ["Curiosity", "Trust", "Indifference", "Fear"]
    ct     = pd.crosstab(df2["feeling_label"], df2["Q13.Year_of_study"])
    ct_pct = (ct.div(ct.sum()) * 100).round(1)
    fig = go.Figure()
    for feel in order_feel:
        if feel not in ct_pct.index:
            continue
        vals = ct_pct.loc[feel]
        fig.add_trace(go.Bar(
            name=feel,
            x=[f"Year {y}" for y in vals.index],
            y=vals.values,
            marker_color=FEEL_COL.get(feel, GREY),
            text=[f"{v:.0f}%" for v in vals.values],
            textposition="inside",
            textfont=dict(color=BG, size=11),
        ))
    fig.update_layout(**base_layout(
        "Feeling Toward AI by Year of Study  (Survey_AI, n=91)"),
        barmode="stack")
    fig.update_yaxes(title="% students", range=[0, 105])
    fig.update_xaxes(title="")
    return fig

def fig_edu_advantages():
    labels = ["Teaching\nAdvantage (Q8)", "Learning\nAdvantage (Q9)",
              "Evaluation\nAdvantage (Q10)", "Educational\nDisadvantage (Q11)"]
    cols   = ["Q8.Advantage_teaching", "Q9.Advantage_learning",
              "Q10.Advantage_evaluation", "Q11.Disadvantage_educational_process"]
    vals   = [round(df2[c].mean(), 2) for c in cols]
    colors = [TEAL, TEAL, TEAL, RED]
    fig = go.Figure(go.Bar(
        x=labels, y=vals,
        marker_color=colors,
        text=[f"{v}" for v in vals],
        textposition="outside",
        textfont=dict(color=TEXT),
        width=0.5,
        hovertemplate="%{x}<br>Mean: %{y:.2f}<br><i>(1=strong agree, 5=disagree)</i><extra></extra>",
    ))
    fig.add_hline(y=3, line_dash="dot", line_color=AMBER,
                  annotation_text="Neutral (3/5)",
                  annotation_font_color=AMBER, annotation_font_size=10)
    fig.update_layout(**base_layout(
        "AI in Education — Advantages & Disadvantages  (Survey_AI, n=91 — 1=agree, 5=disagree)"))
    fig.update_yaxes(title="Mean score", range=[0, 4])
    fig.update_xaxes(title="")
    return fig

# ─────────────────────────────────────────────────────────────
# 8. KPI CALCULATIONS
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

# ─────────────────────────────────────────────────────────────
# 9. DASH LAYOUT
# ─────────────────────────────────────────────────────────────
PANEL = {"background": CARD, "borderRadius": "12px", "padding": "24px",
         "marginBottom": "20px"}

app = dash.Dash(__name__, title="AI & Learning — The Paradox")
app.index_string = """
<!DOCTYPE html>
<html>
<head>
  {%metas%}
  <title>{%title%}</title>
  {%favicon%}
  {%css%}
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: """ + BG + """; font-family: 'DM Sans', sans-serif; color: """ + TEXT + """; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: """ + BG + """; }
    ::-webkit-scrollbar-thumb { background: """ + GREY + """; border-radius: 3px; }
  </style>
</head>
<body>{%app_entry%}{%config%}{%scripts%}{%renderer%}</body>
</html>
"""

TABS_STYLE = {"backgroundColor": BG, "border": "none", "padding": "0 32px"}
TAB_STYLE  = {"backgroundColor": BG, "color": SUBTEXT, "border": "none",
              "padding": "12px 20px", "fontFamily": "'DM Sans',sans-serif",
              "fontSize": "13px", "fontWeight": "500"}
TAB_SEL    = {**TAB_STYLE, "color": TEAL,
              "borderBottom": f"2px solid {TEAL}", "backgroundColor": CARD}

def section(title, children, insight=None):
    inner = [html.H3(title, style={"color": TEXT, "fontWeight": "600",
                                   "marginBottom": "16px", "fontSize": "15px"})]
    if insight:
        inner.append(html.Div(insight, style={
            "background": "rgba(251,191,36,0.08)",
            "borderLeft": f"3px solid {AMBER}",
            "padding": "10px 14px", "borderRadius": "4px",
            "fontSize": "12px", "color": SUBTEXT,
            "marginBottom": "16px", "lineHeight": "1.6",
        }))
    inner += children
    return html.Div(inner, style=PANEL)

app.layout = html.Div(
    style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px"},
    children=[
        # ── HEADER ──
        html.Div(style={"padding": "36px 0 20px"}, children=[
            html.Div("DATA VISUALIZATION PROJECT · Bianchi & Faour", style={
                "color": SUBTEXT, "fontSize": "11px", "letterSpacing": "2px",
                "textTransform": "uppercase", "marginBottom": "8px"}),
            html.H1("Does AI Boost Grades While Undermining Real Understanding?",
                    style={"color": TEXT, "fontSize": "26px", "fontWeight": "700",
                           "lineHeight": "1.3", "marginBottom": "6px"}),
            html.Div("The Paradox of Artificial Performance",
                     style={"color": TEAL, "fontSize": "14px", "fontWeight": "500"}),
        ]),
        # ── KPI CARDS ──
        html.Div(style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "16px", "marginBottom": "24px"}, children=[
            kpi_card("ChatGPT Adoption", f"{adoption_pct}%",
                     f"of 23 218 global students  (Dataset 1)", TEAL),
            kpi_card("Paradox Gap (Extensive use)",
                     f"+{grade_gap_ext}",
                     f"Grades−CritThink gap (Rarely: +{grade_gap_rare})", AMBER),
            kpi_card("Grade Delta — AI Adopters", f"+{delta_ai} pt",
                     "avg over 40 students  (Dataset 3)", GREEN),
            kpi_card("Perceived AI Utility", f"{survey_utility}/10",
                     "median 8.0 · n=91  (Survey_AI)", RED),
        ]),
        # ── TABS ──
        dcc.Tabs(style=TABS_STYLE, children=[
            # TAB 1 — OVERVIEW
            dcc.Tab(label="1 · Overview", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    html.Div(style={"display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "20px"}, children=[
                        section("ChatGPT Adoption — Global Picture",
                                [dcc.Graph(figure=fig_adoption_donut(),
                                           config={"displayModeBar": False})],
                                insight="69% degli studenti universitari globali ha usato ChatGPT "
                                        "(Dataset 1, n=23 218, 109 paesi — dati reali Aristovnik et al. 2024). "
                                        "Questo sostituisce il dataset sintetico precedente con un campione "
                                        "autentico su scala globale."),
                        section("Intensità d'uso tra gli utenti ChatGPT",
                                [dcc.Graph(figure=fig_usage_intensity_bar(),
                                           config={"displayModeBar": False})],
                                insight="La maggioranza usa ChatGPT in modo Occasionally/Moderately. "
                                        "Solo il 4.3% lo usa Extensively — ma questo gruppo mostra "
                                        "il paradosso più marcato (vedi Tab 2)."),
                    ]),
                    section("Tasso di adozione per campo di studi",
                            [dcc.Graph(figure=fig_field_adoption(),
                                       config={"displayModeBar": False})],
                            insight="Applied Sciences e Social Sciences hanno i tassi di adozione "
                                    "più alti. Arts & Humanities adotta meno ma con gap "
                                    "paradossale comparabile."),
                ])
            ]),
            # TAB 2 — THE PARADOX
            dcc.Tab(label="2 · The Paradox ⭐", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Il Paradosso — Dati Reali (n=16 010)",
                            [dcc.Graph(figure=fig_paradox_lines(),
                                       config={"displayModeBar": False})],
                            insight="SEGNALE REALE (non sintetico): all'aumentare dell'intensità d'uso, "
                                    "la percezione di miglioramento dei voti cresce più rapidamente "
                                    "della percezione di guadagno nel critical thinking. "
                                    "Il gap è +0.19 per uso raro, +0.54 per uso estensivo. "
                                    "Scala Likert 1–5 (1=strongly disagree, 5=strongly agree)."),
                    section("Gap per Campo di Studi × Intensità d'uso",
                            [dcc.Graph(figure=fig_hinder_vs_grades(),
                                       config={"displayModeBar": False})],
                            insight="Il paradosso è consistente tra tutti i campi di studi. "
                                    "Social Sciences mostra il gap più ampio agli alti livelli di uso. "
                                    "Applied Sciences ha il profilo più equilibrato."),
                ])
            ]),
            # TAB 3 — DEPENDENCY LENS
            dcc.Tab(label="3 · Dependency Lens", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Heatmap: Task di utilizzo × Intensità d'uso",
                            [dcc.Graph(figure=fig_purpose_heatmap(),
                                       config={"displayModeBar": False})],
                            insight="Gli utenti intensivi usano ChatGPT per più task simultaneamente, "
                                    "con picchi su Academic Writing, Research e Study Assistance. "
                                    "Questo profilo multi-task è associato al gap paradossale più grande."),
                    section("Tre metriche chiave per Intensità d'uso",
                            [dcc.Graph(figure=fig_dependency_paradox_bars(),
                                       config={"displayModeBar": False})],
                            insight="Notare: la preoccupazione 'AI hinders learning' (amber) DECRESCE "
                                    "con l'intensità d'uso — chi usa di più tende a preoccuparsi di meno. "
                                    "Questo potrebbe indicare una forma di razionalizzazione cognitiva "
                                    "o genuina esperienza positiva — il dataset non consente di distinguere."),
                ])
            ]),
            # TAB 4 — GRADE DELTA
            dcc.Tab(label="4 · Grade Delta", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Slope Chart: Grades Before → After AI adoption",
                            [dcc.Graph(figure=fig_slope_chart(),
                                       config={"displayModeBar": False})],
                            insight="Dataset 3 (semi-sintetico): tutti i 40 studenti AI migliorano "
                                    "(Δ medio = +9.82 pt). Research college ottiene il delta più alto (+12 pt). "
                                    "Corrobora il segnale percettivo del Tab 2 con dati before/after."),
                    section("Grade Delta by Purpose × Education Level",
                            [dcc.Graph(figure=fig_delta_by_purpose(),
                                       config={"displayModeBar": False})],
                            insight="Research college (+12.0) > Coding (+10.8) > Homework (+9.0). "
                                    "L'uso cognitivamente impegnativo produce guadagni maggiori — "
                                    "coerente con il Dataset 1 dove uso per Research è il più comune "
                                    "tra gli utenti intensivi."),
                ])
            ]),
            # TAB 5 — PERCEPTIONS
            dcc.Tab(label="5 · Perceptions", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    html.Div(style={"display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "20px"}, children=[
                        section("Emozioni usando ChatGPT  (Dataset 1, n=16 010)",
                                [dcc.Graph(figure=fig_emotions_radar(),
                                           config={"displayModeBar": False})],
                                insight="Curious (3.43) e Calm (3.27) dominano — "
                                        "profilo emotivo positivo-pragmatico. "
                                        "Ashamed (1.82) e Sad (1.73) restano bassi: "
                                        "l'uso di ChatGPT non genera colpa significativa."),
                        section("Soddisfazione & Attitudine  (Dataset 1)",
                                [dcc.Graph(figure=fig_satisfaction_bars(),
                                           config={"displayModeBar": False})],
                                insight="'Using ChatGPT is interesting' (3.74) e "
                                        "'Helps in everyday life' (3.91) sono i valori più alti. "
                                        "'More useful than Google' è sopra il neutro (3.29) ma diviso."),
                    ]),
                    html.Div(style={"display": "grid",
                                    "gridTemplateColumns": "1fr 1fr",
                                    "gap": "20px"}, children=[
                        section("Sentimento verso l'AI per Anno di Studio  (Survey_AI, n=91)",
                                [dcc.Graph(figure=fig_feelings_stacked(),
                                           config={"displayModeBar": False})],
                                insight="Curiosità domina (68.1%), Trust bassa (7.7%). "
                                        "Anno 1 mostra più paura (17.6% vs 10.5%). "
                                        "Profilo coerente con il Dataset 1 (emozioni globali)."),
                        section("Vantaggi e Svantaggi AI nell'Educazione  (Survey_AI)",
                                [dcc.Graph(figure=fig_edu_advantages(),
                                           config={"displayModeBar": False})],
                                insight="Gli studenti concordano SIA con i vantaggi (Q9: 1.88/5) "
                                        "SIA con lo svantaggio (Q11: 2.10/5). "
                                        "Questa co-esistenza è la versione soggettiva del paradosso — "
                                        "confermata anche dal Dataset 1 su scala globale."),
                    ]),
                ])
            ]),
        ]),
        # ── FOOTER ──
        html.Div(style={"padding": "32px 0 40px", "textAlign": "center",
                        "color": SUBTEXT, "fontSize": "11px", "letterSpacing": "1px"}, children=[
            html.Div(
                "Dataset 1: final_dataset.xlsx — Aristovnik et al. (2024), n=23 218, 109 paesi (REALE) · "
                "Dataset 2: Survey_AI.csv (n=91, reale) · "
                "Dataset 3: students_ai_usage.csv (n=100, semi-sintetico)"),
            html.Div("Francesco Bianchi 264692 · Hassan Faour 265917 · Built with Python / Plotly Dash",
                     style={"marginTop": "6px"}),
        ]),
    ]
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)