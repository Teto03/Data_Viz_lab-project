# figures.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Local imports
from config import (TEAL, GREY, AMBER, RED, GREEN, TEXT, SUBTEXT, BG, CARD, GRIDD, 
                    USE_LABELS, FIELD_COL, PURP_COL, FEEL_COL, base_layout)
from data import df1_raw, df1_users, df2, df3

# ── TAB 1 ──
def fig_adoption_donut():
    counts = df1_raw["used_chatgpt"].value_counts()
    colors = [TEAL if c == "Yes" else GREY for c in counts.index]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.60,
        marker_colors=colors, textinfo="label+percent", textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>%{value} studenti (%{percent})<extra></extra>",
        sort=False,
    ))
    fig.add_annotation(x=0.5, y=0.5, text="<b>23 218</b><br>studenti",
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
        x=labels, y=pcts.values, marker_color=colors,
        text=[f"{v:.1f}%" for v in pcts.values], textposition="outside",
        textfont=dict(color=TEXT), hovertemplate="%{x}<br>%{y:.1f}% degli utenti<extra></extra>",
    ))
    fig.update_layout(**base_layout("Intensità d'uso di ChatGPT  (solo utenti, n=16 010)"))
    fig.update_yaxes(title="% utenti ChatGPT", range=[0, 42])
    fig.update_xaxes(title="")
    return fig

def fig_field_adoption():
    grp = (df1_raw.dropna(subset=["field_label"])
               .groupby("field_label")["Q13"]
               .apply(lambda x: (x == 1).mean() * 100)
               .round(1).sort_values(ascending=True).reset_index())
    grp.columns = ["Field", "AdoptionPct"]
    fig = go.Figure(go.Bar(
        x=grp["AdoptionPct"], y=grp["Field"], orientation="h",
        marker_color=[FIELD_COL.get(f, GREY) for f in grp["Field"]],
        text=[f"{v:.1f}%" for v in grp["AdoptionPct"]],
        textposition="outside", textfont=dict(color=TEXT),
        hovertemplate="%{y}: %{x:.1f}% adoption<extra></extra>",
    ))
    fig.update_layout(**base_layout("Tasso di adozione per campo di studi", height=300))
    fig.update_xaxes(title="% studenti che usano ChatGPT", range=[0, 85])
    fig.update_yaxes(title="")
    return fig

# ── TAB 2 ──
def fig_paradox_lines():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    grades_mean = df1_users.groupby("Q15")["Q27b"].mean().reindex(order).round(2)
    crit_mean   = df1_users.groupby("Q15")["Q29e"].mean().reindex(order).round(2)
    gap         = (grades_mean - crit_mean).round(2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=grades_mean.values, mode="lines+markers+text",
        name="Perceived Grade Improvement (Q27b)", line=dict(color=TEAL, width=3),
        marker=dict(size=10, color=TEAL), text=[f"{v:.2f}" for v in grades_mean.values],
        textposition="top center", textfont=dict(color=TEAL, size=11),
        hovertemplate="Intensità: %{x}<br>Voti percepiti: %{y:.2f}/5<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=crit_mean.values, mode="lines+markers+text",
        name="Perceived Critical Thinking Gain (Q29e)", line=dict(color=RED, width=3),
        marker=dict(size=10, color=RED), text=[f"{v:.2f}" for v in crit_mean.values],
        textposition="bottom center", textfont=dict(color=RED, size=11),
        hovertemplate="Intensità: %{x}<br>Critical thinking: %{y:.2f}/5<extra></extra>",
    ))
    for i, (x, g, c, gp) in enumerate(zip(labels, grades_mean, crit_mean, gap)):
        fig.add_shape(type="line", x0=x, x1=x, y0=c, y1=g,
                      line=dict(color=AMBER, width=1.5, dash="dot"))
        if i == 4:
            fig.add_annotation(x=x, y=(g + c) / 2, text=f"  Gap = {gp:.2f}",
                               showarrow=False, font=dict(color=AMBER, size=11), xanchor="left")
    fig.add_annotation(x="Rarely", y=(grades_mean[1] + crit_mean[1]) / 2, text=f"Gap = {gap[1]:.2f}",
                       showarrow=False, font=dict(color=AMBER, size=11), xanchor="right")
    fig.add_annotation(
        x="Moderately", y=4.3,
        text="<b>Il gap si allarga con l'intensità d'uso</b><br>"
             "Più si usa ChatGPT → più si percepisce un vantaggio sui voti<br>"
             "ma il beneficio sul critical thinking cresce meno",
        showarrow=False, font=dict(color=AMBER, size=10),
        bgcolor=CARD, bordercolor=AMBER, borderwidth=1, borderpad=6, align="center",
    )
    fig.update_layout(**base_layout(
        "Il Paradosso — Voti vs Critical Thinking per Intensità d'uso  (Dataset 1, n=16 010, scala 1–5)", height=480))
    fig.update_yaxes(title="Accordo medio (1=disaccordo, 5=accordo)", range=[2.3, 4.8])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

def fig_hinder_vs_grades():
    order  = [1, 2, 3, 4, 5]
    labels = [USE_LABELS[i] for i in order]
    fields = ["Arts & Humanities", "Social Sciences", "Applied Sciences", "Natural Sciences"]
    fig = go.Figure()
    for field in fields:
        sub = df1_users[df1_users["field_label"] == field]
        grp = sub.groupby("Q15")[["Q27b", "Q29e"]].mean().reindex(order)
        gap = (grp["Q27b"] - grp["Q29e"]).round(3)
        fig.add_trace(go.Scatter(
            x=labels, y=gap.values, mode="lines+markers", name=field,
            line=dict(color=FIELD_COL.get(field, GREY), width=2),
            marker=dict(size=8, color=FIELD_COL.get(field, GREY)),
            hovertemplate=f"<b>{field}</b><br>Intensità: %{{x}}<br>Gap (voti−crit.think.): %{{y:.2f}}<extra></extra>",
        ))
    fig.add_hline(y=0, line_dash="dot", line_color=GREY,
                  annotation_text="Nessun gap (voti = critical thinking)",
                  annotation_font_color=GREY, annotation_font_size=9)
    fig.update_layout(**base_layout("Gap (Voti − Critical Thinking) per Campo di Studi × Intensità d'uso", height=420))
    fig.update_yaxes(title="Gap percepito (Q27b − Q29e)", range=[-0.1, 0.8])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

# ── TAB 3 ──
def fig_purpose_heatmap():
    q18_cols   = [f"Q18{c}" for c in "abcdefghijkl"]
    q18_labels = ["Academic writing", "Professional writing", "Creative writing",
                  "Proofreading", "Brainstorming", "Translating", "Summarizing", 
                  "Calculating", "Study assistance", "Personal assistance", "Research", "Coding"]
    order = [1, 2, 3, 4, 5]
    grp   = df1_users.groupby("Q15")[q18_cols].mean().reindex(order).round(2)
    fig = go.Figure(go.Heatmap(
        z=grp.values.T, x=[USE_LABELS[i] for i in order], y=q18_labels,
        colorscale=[[0.0, CARD], [0.5, "#1E6B74"], [1.0, TEAL]],
        zmin=1, zmax=4, texttemplate="%{z}", textfont=dict(color=TEXT, size=10),
        hovertemplate="Intensità: %{x}<br>Task: %{y}<br>Media: %{z}<extra></extra>",
        colorbar=dict(title=dict(text="Freq.<br>(1–5)", font=dict(color=SUBTEXT)), tickfont=dict(color=SUBTEXT)),
    ))
    fig.update_layout(**base_layout("Frequenza d'uso per Task × Intensità  (Dataset 1, scala 1=Never, 5=Always)", height=480))
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
            name=name, x=labels, y=vals.values, marker_color=col,
            text=[f"{v:.2f}" for v in vals.values], textposition="outside",
            textfont=dict(color=TEXT, size=9), width=0.26, offset=offset,
        ))
    fig.update_layout(**base_layout("Tre metriche chiave per Intensità d'uso  (Dataset 1, scala 1–5)", height=440), barmode="overlay")
    fig.update_yaxes(title="Accordo medio (scala Likert 1–5)", range=[2.4, 4.7])
    fig.update_xaxes(title="Intensità d'uso di ChatGPT")
    return fig

# ── TAB 4 ──
def fig_slope_chart():
    ai_d3  = df3[df3["uses_ai"] == "Yes"].copy()
    non_d3 = df3[df3["uses_ai"] == "No"].copy()
    fig = go.Figure()
    shown_non = False
    for _, row in non_d3.iterrows():
        fig.add_trace(go.Scatter(
            x=["Before AI", "After AI"], y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines", line=dict(color=GREY, width=1.2), opacity=0.25,
            showlegend=not shown_non, name="Non-Users (Δ=0)", legendgroup="non",
            hovertemplate="Grade: %{y}<extra>Non-User</extra>",
        ))
        shown_non = True
    shown = set()
    for _, row in ai_d3.iterrows():
        purpose = str(row.get("purpose_of_ai", "Unknown"))
        col = PURP_COL.get(purpose, TEAL)
        fig.add_trace(go.Scatter(
            x=["Before AI", "After AI"], y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines+markers", line=dict(color=col, width=2), marker=dict(size=6, color=col),
            opacity=0.75, showlegend=purpose not in shown, name=f"AI – {purpose}",
            legendgroup=purpose, hovertemplate=f"<b>{purpose}</b><br>Grade: %{{y}}<br>Δ = +{row['grade_delta']:.0f} pt<extra></extra>",
        ))
        shown.add(purpose)
    fig.add_annotation(
        x=1, y=ai_d3["grades_after_ai"].max() + 2,
        text=f"<b>Avg Δ AI users: +{ai_d3['grade_delta'].mean():.2f} pt</b>",
        showarrow=False, font=dict(color=GREEN, size=13),
        bgcolor=CARD, bordercolor=GREEN, borderwidth=1, borderpad=6,
    )
    fig.add_annotation(x=1, y=non_d3["grades_after_ai"].min() - 3, text="⚠ Non-users Δ=0 is a synthetic artifact", showarrow=False, font=dict(color=AMBER, size=9))
    fig.update_layout(**base_layout("Slope Chart: Grades Before → After AI adoption  (Dataset 3, n=100)", height=480))
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
        text="Delta", color_discrete_map={"college": TEAL, "school": AMBER},
    )
    fig.update_traces(textposition="outside", textfont=dict(color=TEXT))
    fig.update_layout(**base_layout("Grade Delta by Purpose × Education Level  (AI Users only)"))
    fig.update_yaxes(title="Avg Grade Δ", range=[0, 15])
    fig.update_xaxes(title="")
    return fig

# ── TAB 5 ──
def fig_emotions_radar():
    emo_cols = [f"Q32{c}" for c in "abcdefghijklmno"]
    emo_labels = ["Bored", "Hopeful", "Sad", "Ashamed", "Calm", "Angry", "Relieved", "Happy", 
                  "Proud", "Anxious", "Surprised", "Curious", "Excited", "Confused", "Frustrated"]
    vals = df1_users[emo_cols].mean().round(2).tolist()
    vals_c = vals + [vals[0]]
    labs_c = emo_labels + [emo_labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_c, theta=labs_c, fill="toself", fillcolor="rgba(45,212,191,0.12)",
        line=dict(color=TEAL, width=2), marker=dict(color=TEAL, size=6),
        name="Mean emotion", hovertemplate="%{theta}: <b>%{r:.2f}/5</b><extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[3.0] * len(labs_c), theta=labs_c, fill="toself", fillcolor="rgba(100,116,139,0.06)",
        line=dict(color=GREY, width=1, dash="dot"), name="Neutral (3.0/5)",
    ))
    fig.update_layout(
        **base_layout("Emozioni provate usando ChatGPT  (Dataset 1, n=16 010, 1=Never 5=Always)", height=460),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[1, 5], gridcolor=GRIDD,
                            tickfont=dict(color=SUBTEXT), tickvals=[1, 2, 3, 4, 5]),
            angularaxis=dict(gridcolor=GRIDD, tickfont=dict(color=TEXT, size=9)),
        ),
    )
    return fig

def fig_satisfaction_bars():
    items = {"Q24a": "More useful than Google", "Q24b": "Easier than talking to professors",
             "Q24e": "Satisfied – level of assistance", "Q24f": "Satisfied – quality of info",
             "Q24g": "Satisfied – accuracy", "Q25b": "Using ChatGPT is interesting",
             "Q25c": "Being able to use it is important", "Q25d": "Helps in everyday life"}
    vals   = {k: df1_users[k].mean().round(2) for k in items}
    labels = list(items.values())
    means  = list(vals.values())
    colors = [TEAL if v >= 3.0 else RED for v in means]
    fig = go.Figure(go.Bar(
        x=means, y=labels, orientation="h", marker_color=colors,
        text=[f"{v:.2f}" for v in means], textposition="outside",
        textfont=dict(color=TEXT), hovertemplate="%{y}<br>Media: %{x:.2f}/5<extra></extra>",
    ))
    fig.add_vline(x=3.0, line_dash="dot", line_color=AMBER, annotation_text="Neutral (3/5)",
                  annotation_font_color=AMBER, annotation_font_size=9)
    fig.update_layout(**base_layout("Soddisfazione & Attitudine verso ChatGPT  (Dataset 1, scala 1–5)", height=380))
    fig.update_xaxes(title="Accordo medio", range=[1, 5])
    fig.update_yaxes(title="")
    return fig

def fig_feelings_stacked():
    order_feel = ["Curiosity", "Trust", "Indifference", "Fear"]
    ct     = pd.crosstab(df2["feeling_label"], df2["Q13.Year_of_study"])
    ct_pct = (ct.div(ct.sum()) * 100).round(1)
    fig = go.Figure()
    for feel in order_feel:
        if feel not in ct_pct.index: continue
        vals = ct_pct.loc[feel]
        fig.add_trace(go.Bar(
            name=feel, x=[f"Year {y}" for y in vals.index], y=vals.values,
            marker_color=FEEL_COL.get(feel, GREY), text=[f"{v:.0f}%" for v in vals.values],
            textposition="inside", textfont=dict(color=BG, size=11),
        ))
    fig.update_layout(**base_layout("Feeling Toward AI by Year of Study  (Survey_AI, n=91)"), barmode="stack")
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
        x=labels, y=vals, marker_color=colors, text=[f"{v}" for v in vals],
        textposition="outside", textfont=dict(color=TEXT), width=0.5,
        hovertemplate="%{x}<br>Mean: %{y:.2f}<br><i>(1=strong agree, 5=disagree)</i><extra></extra>",
    ))
    fig.add_hline(y=3, line_dash="dot", line_color=AMBER, annotation_text="Neutral (3/5)",
                  annotation_font_color=AMBER, annotation_font_size=10)
    fig.update_layout(**base_layout("AI in Education — Advantages & Disadvantages  (Survey_AI, n=91 — 1=agree, 5=disagree)"))
    fig.update_yaxes(title="Mean score", range=[0, 4])
    fig.update_xaxes(title="")
    return fig