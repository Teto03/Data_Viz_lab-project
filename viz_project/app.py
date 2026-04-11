"""
=============================================================
  AI Impact Dashboard — app.py
  "Does AI Boost Grades While Undermining Real Understanding?"
  Francesco Bianchi (264692) · Hassan Faour (265917)
=============================================================
  Run:  python app.py
  Open: http://127.0.0.1:8050
=============================================================
"""

import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# 0. PALETTE & THEME
# ─────────────────────────────────────────────────────────────
BG       = "#0D1B2A"
CARD     = "#132338"
TEAL     = "#2DD4BF"
AMBER    = "#FBBF24"
RED      = "#F87171"
GREEN    = "#34D399"
GREY     = "#64748B"
GRIDD    = "#1E2D3D"
TEXT     = "#F1F5F9"
SUBTEXT  = "#94A3B8"

PERF_COL = {"High": TEAL, "Medium": AMBER, "Low": RED}
PURP_COL = {"Research": TEAL, "Coding": AMBER, "Homework": GREY}
FEEL_COL = {"Curiosity": TEAL, "Trust": GREEN, "Indifference": GREY, "Fear": RED}

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
df1 = pd.read_csv("ai_impact_student_performance_dataset.csv")
df2 = pd.read_csv("Survey_AI.csv")
df3 = pd.read_csv("students_ai_usage.csv")

# ── Dataset 1 ──
df1["ai_tool_cat"] = (
    df1["ai_tools_used"].fillna("None")
    .apply(lambda x: x.split("+")[0].strip() if "+" in str(x) else str(x).strip())
)
ai_mask = df1["uses_ai"] == 1
df1.loc[ai_mask, "dep_q"] = pd.qcut(
    df1.loc[ai_mask, "ai_dependency_score"], q=4, labels=["Q1","Q2","Q3","Q4"]
)
df1.loc[ai_mask, "eth_q"] = pd.qcut(
    df1.loc[ai_mask, "ai_ethics_score"], q=4, labels=["Q1","Q2","Q3","Q4"]
)

# ── Dataset 2 ──
df2["feeling_label"] = df2["Q5.Feelings"].map(
    {1:"Curiosity", 2:"Fear", 3:"Indifference", 4:"Trust"}
)
df2 = df2.rename(columns={"Q10.Advantage_evaluation ": "Q10.Advantage_evaluation"})

# ── Dataset 3 ──
df3["grade_delta"]     = df3["grades_after_ai"] - df3["grades_before_ai"]
df3["delta_direction"] = df3["grade_delta"].apply(lambda x: "Positive" if x > 0 else "Zero")
df3["sid"]             = range(len(df3))


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
        html.Div(sub,  style={"color": SUBTEXT, "fontSize": "12px", "marginTop": "4px"}),
    ])


# ─────────────────────────────────────────────────────────────
# 3. TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────

def fig_overview_bar():
    """
    PERCHÉ: la prima domanda della proposal è "do AI users score higher?"
    Risposta: NO (p=0.88). Due barre quasi identiche per final_score
    E concept_understanding→ evidenzia subito il limite del dataset sintetico
    e invita lo spettatore a cercare il segnale altrove (Tab 4).
    """
    ai  = df1[df1["uses_ai"] == 1]
    non = df1[df1["uses_ai"] == 0]

    fig = go.Figure()
    for label, vals, col in [
        ("AI Users",   [ai["final_score"].mean(), ai["concept_understanding_score"].mean()],  TEAL),
        ("Non-Users",  [non["final_score"].mean(), non["concept_understanding_score"].mean()], GREY),
    ]:
        fig.add_trace(go.Bar(
            name=label,
            x=["Final Score (0–100)", "Concept Understanding (0–10)"],
            y=[round(v, 2) for v in vals],
            marker_color=col,
            text=[f"{v:.2f}" for v in vals],
            textposition="outside",
            textfont=dict(color=TEXT),
            width=0.32,
        ))

    fig.add_annotation(
        x="Final Score (0–100)", y=62,
        text="Δ = −0.04  (p = 0.88, non-significativo)",
        showarrow=False,
        font=dict(size=10, color=AMBER),
        bgcolor=CARD,
        bordercolor=AMBER, borderwidth=1, borderpad=4,
    )
    fig.update_layout(**base_layout("Media punteggi: AI Users vs Non-Users  (Dataset 1, n=8 000)"),
                      barmode="group")
    fig.update_yaxes(range=[0, 75])
    return fig


def fig_donut():
    """
    PERCHÉ: mostra la distribuzione delle performance category,
    utile come contesto prima di approfondire (Tab 2).
    """
    counts = df1["performance_category"].value_counts()
    colors = [PERF_COL.get(c, GREY) for c in counts.index]

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
    fig.add_annotation(x=0.5, y=0.5, text="<b>8 000</b><br>studenti",
                       showarrow=False, font=dict(size=13, color=TEXT))
    fig.update_layout(**base_layout("Distribuzione Performance Category"))
    return fig


# ─────────────────────────────────────────────────────────────
# 4. TAB 2 — THE PARADOX
# ─────────────────────────────────────────────────────────────

def fig_paradox_grouped_bar():
    """
    PERCHÉ: cuore narrativo della proposal. Mette a confronto
    Final Score, Concept Understanding e AI Dependency per ogni
    categoria di performance. Il punto chiave: AI Dependency è PIATTA
    tra High / Medium / Low → la dipendenza AI non spiega la differenza
    di punteggio. La linea tratteggiata amber lo evidenzia visivamente.
    """
    order = ["High", "Medium", "Low"]
    grp = (
        df1.groupby("performance_category")
        [["final_score", "concept_understanding_score", "ai_dependency_score"]]
        .mean().round(2).reindex(order)
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Barre: Final Score (asse sx, scala 0-100)
    fig.add_trace(go.Bar(
        name="Final Score",
        x=order,
        y=grp["final_score"],
        marker_color=[PERF_COL[c] for c in order],
        opacity=0.85,
        text=grp["final_score"].values,
        textposition="outside",
        width=0.3,
        offset=-0.17,
    ), secondary_y=False)

    # Barre: Concept Understanding (asse dx, scala 0-10) – pattern tratteggiato
    fig.add_trace(go.Bar(
        name="Concept Understanding",
        x=order,
        y=grp["concept_understanding_score"],
        marker_color=[PERF_COL[c] for c in order],
        marker_pattern_shape="x",
        opacity=0.55,
        text=grp["concept_understanding_score"].values,
        textposition="outside",
        width=0.3,
        offset=0.17,
    ), secondary_y=True)

    # Linea: AI Dependency (asse dx) – dovrebbe variare con le perf ma è piatta
    fig.add_trace(go.Scatter(
        name="AI Dependency Score",
        x=order,
        y=grp["ai_dependency_score"],
        mode="lines+markers+text",
        line=dict(color=AMBER, width=2.5, dash="dot"),
        marker=dict(size=10, color=AMBER),
        text=[f"  {v}" for v in grp["ai_dependency_score"].values],
        textposition="middle right",
        textfont=dict(color=AMBER),
    ), secondary_y=True)

    fig.add_annotation(
        x="Medium", y=5.9, yref="y2",
        text="AI Dependency è piatta tra tutte le categorie",
        showarrow=True, arrowhead=2, ax=0, ay=-30,
        font=dict(color=AMBER, size=10), arrowcolor=AMBER,
    )

    lo = base_layout("Il Paradosso — Score vs Comprensione vs Dipendenza AI per Categoria", height=460)
    lo.update({
        "barmode": "overlay",
        "yaxis":  dict(title="Final Score (0–100)",          range=[0, 100],
                       gridcolor=GRIDD, tickfont=dict(color=SUBTEXT)),
        "yaxis2": dict(title="Concept Understanding / Dependency (0–10)",
                       range=[0, 11], gridcolor="rgba(0,0,0,0)",
                       tickfont=dict(color=SUBTEXT), overlaying="y", side="right"),
    })
    fig.update_layout(**lo)
    return fig


def fig_scatter_paradox():
    """
    PERCHÉ: la proposal prevede uno scatter AI-generated content %
    vs Concept Understanding, colorato per performance category.
    r = 0.022 → nuvola di punti piatta. Il messaggio è esplicito:
    nei dati sintetici questa relazione non esiste; nella realtà
    è la domanda centrale che il dashboard vuole porre.
    """
    sample = df1.sample(600, random_state=42)

    fig = go.Figure()
    for cat in ["High", "Medium", "Low"]:
        sub = sample[sample["performance_category"] == cat]
        fig.add_trace(go.Scatter(
            x=sub["ai_generated_content_percentage"],
            y=sub["concept_understanding_score"],
            mode="markers",
            name=cat,
            marker=dict(color=PERF_COL[cat], size=5, opacity=0.5),
            hovertemplate=f"<b>{cat}</b><br>AI Content: %{{x}}%<br>Concept: %{{y:.1f}}<extra></extra>",
        ))

    # Trendline OLS manuale
    x_v = sample["ai_generated_content_percentage"].values
    y_v = sample["concept_understanding_score"].values
    m, b = np.polyfit(x_v, y_v, 1)
    x_line = np.linspace(0, 100, 100)
    fig.add_trace(go.Scatter(
        x=x_line, y=m * x_line + b,
        mode="lines", name="Trend (r = 0.02)",
        line=dict(color=AMBER, width=2, dash="dot"),
    ))

    fig.add_annotation(
        x=85, y=9.6,
        text="<b>r = 0.022</b> — nessuna relazione<br><i>(dati sintetici)</i>",
        showarrow=False, font=dict(color=AMBER, size=11),
        bgcolor=CARD, bordercolor=AMBER, borderwidth=1, borderpad=5,
    )

    fig.update_layout(**base_layout(
        "AI-Generated Content % vs Concept Understanding (campione 600)", height=440
    ))
    fig.update_xaxes(title="AI-Generated Content (%)", range=[-2, 102])
    fig.update_yaxes(title="Concept Understanding Score (0–10)", range=[0, 11])
    return fig


# ─────────────────────────────────────────────────────────────
# 5. TAB 3 — DEPENDENCY LENS
# ─────────────────────────────────────────────────────────────

def fig_heatmap():
    """
    PERCHÉ: la proposal vuole una heatmap Dependency × Ethics → Concept.
    Il range reale è 5.14–5.77 (quasi uniforme): il messaggio è che
    nei dati sintetici la leva dipendenza/etica non produce gradiente.
    La scala di colore è volutamente sensibile (zmin/zmax stretti) per
    rendere visibile anche la variazione minima esistente.
    """
    ai = df1[df1["uses_ai"] == 1].copy()
    ai["dep_q"] = pd.qcut(ai["ai_dependency_score"], q=4, labels=["Q1","Q2","Q3","Q4"])
    ai["eth_q"] = pd.qcut(ai["ai_ethics_score"],     q=4, labels=["Q1","Q2","Q3","Q4"])

    hm = (
        ai.groupby(["dep_q","eth_q"])["concept_understanding_score"]
        .mean().unstack().round(2)
        .reindex(index=["Q4","Q3","Q2","Q1"])   # Q4=più dipendente in basso
    )

    fig = go.Figure(go.Heatmap(
        z=hm.values,
        x=[f"Ethics {c}" for c in hm.columns],
        y=[f"Dep {r}" for r in hm.index],
        colorscale=[[0.0, "#3B82F6"], [0.5, CARD], [1.0, TEAL]],
        zmin=4.9, zmax=6.0,
        texttemplate="%{z}",
        textfont=dict(color=TEXT, size=12),
        hovertemplate="Dipendenza: %{y}<br>Etica: %{x}<br>Concept Score medio: %{z}<extra></extra>",
        colorbar=dict(title=dict(text="Concept<br>Score",
                         font=dict(color=SUBTEXT)),
              tickfont=dict(color=SUBTEXT)),
    ))
    fig.add_annotation(
        x=0.5, y=-0.18, xref="paper", yref="paper",
        text="⚠ Range effettivo: 5.14 – 5.77 — nessun gradiente significativo (dataset sintetico)",
        showarrow=False, font=dict(size=9, color=AMBER),
    )
    fig.update_layout(**base_layout(
        "Concept Understanding: Dipendenza AI × Score Etico (AI users, n=5 128)", height=400
    ))
    return fig


def fig_dependency_bars():
    """
    PERCHÉ: complementa la heatmap mostrando in modo diretto
    come Concept Understanding e Final Score si distribuiscono
    per quartile di dipendenza. Utile per il "slider threshold"
    previsto dalla proposal (qui come barre statiche).
    """
    ai = df1[df1["uses_ai"] == 1].copy()
    ai["dep_q"] = pd.qcut(ai["ai_dependency_score"], q=4, labels=["Q1","Q2","Q3","Q4"])
    grp = ai.groupby("dep_q")[["concept_understanding_score","final_score"]].mean().round(2)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Concept Understanding",
        x=grp.index.astype(str),
        y=grp["concept_understanding_score"],
        marker_color=TEAL,
        text=grp["concept_understanding_score"].values,
        textposition="outside",
        width=0.35, offset=-0.19,
    ))
    fig.add_trace(go.Bar(
        name="Final Score / 10",
        x=grp.index.astype(str),
        y=(grp["final_score"] / 10).round(2),
        marker_color=GREY,
        text=grp["final_score"].apply(lambda v: f"{v:.1f}").values,
        textposition="outside",
        width=0.35, offset=0.19,
    ))
    fig.update_layout(**base_layout(
        "Punteggi per Quartile di Dipendenza AI (Q1=bassa, Q4=alta)"
    ), barmode="overlay")
    fig.update_xaxes(title="Quartile di Dipendenza AI")
    fig.update_yaxes(title="Score", range=[0, 8.5])
    return fig


# ─────────────────────────────────────────────────────────────
# 6. TAB 4 — GRADE DELTA
# ─────────────────────────────────────────────────────────────

def fig_slope_chart():
    """
    PERCHÉ: questo è il segnale più forte di tutto il progetto.
    Ogni linea è uno studente. AI users: tutte le linee salgono
    (delta medio +9.82). Non-users: piatte a zero (artefatto sintetico,
    annotato). Colorato per purpose_of_ai → Research in cima.
    """
    ai_d3  = df3[df3["uses_ai"] == "Yes"].copy()
    non_d3 = df3[df3["uses_ai"] == "No"].copy()

    fig = go.Figure()

    # Non-users: linee piatte grigie, semi-trasparenti
    shown_non = False
    for _, row in non_d3.iterrows():
        fig.add_trace(go.Scatter(
            x=["Prima dell'AI", "Dopo l'AI"],
            y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines",
            line=dict(color=GREY, width=1.2),
            opacity=0.25,
            showlegend=not shown_non,
            name="Non-Users (Δ=0)",
            legendgroup="non",
            hovertemplate=f"Voto: %{{y}}<extra>Non-User</extra>",
        ))
        shown_non = True

    # AI users: colorati per purpose
    shown = set()
    for _, row in ai_d3.iterrows():
        purpose = str(row.get("purpose_of_ai", "Unknown"))
        col = PURP_COL.get(purpose, TEAL)
        fig.add_trace(go.Scatter(
            x=["Prima dell'AI", "Dopo l'AI"],
            y=[row["grades_before_ai"], row["grades_after_ai"]],
            mode="lines+markers",
            line=dict(color=col, width=2),
            marker=dict(size=6, color=col),
            opacity=0.75,
            showlegend=purpose not in shown,
            name=f"AI – {purpose}",
            legendgroup=purpose,
            hovertemplate=(
                f"<b>{purpose}</b><br>"
                "Voto: %{y}<br>"
                f"Δ = +{row['grade_delta']:.0f} pt<extra></extra>"
            ),
        ))
        shown.add(purpose)

    # Annotazione delta medio
    fig.add_annotation(
        x=1, y=ai_d3["grades_after_ai"].max() + 2,
        text=f"<b>Δ medio AI users: +{ai_d3['grade_delta'].mean():.2f} pt</b>",
        showarrow=False, font=dict(color=GREEN, size=13),
        bgcolor=CARD, bordercolor=GREEN, borderwidth=1, borderpad=6,
    )
    fig.add_annotation(
        x=1, y=non_d3["grades_after_ai"].min() - 3,
        text="⚠ Non-users Δ=0 è artefatto sintetico",
        showarrow=False, font=dict(color=AMBER, size=9),
    )

    fig.update_layout(**base_layout(
        "Slope Chart: Voti Prima → Dopo l'adozione AI  (Dataset 3, n=100)", height=480
    ))
    fig.update_xaxes(title="")
    fig.update_yaxes(title="Voto", range=[30, 110])
    return fig


def fig_delta_by_purpose():
    """
    PERCHÉ: la proposal chiede di vedere se il purpose of use
    modera il delta. Research > Coding > Homework è il pattern
    atteso (uso cognitivo > uso passivo). I dati lo confermano
    parzialmente: Research college = +12.0, Homework college = +9.0.
    """
    ai_d3 = df3[df3["uses_ai"] == "Yes"].copy()
    grp = ai_d3.groupby(["purpose_of_ai","education_level"])["grade_delta"].mean().round(2).reset_index()
    grp.columns = ["Purpose","Level","Delta"]

    fig = px.bar(
        grp, x="Purpose", y="Delta", color="Level", barmode="group",
        text="Delta",
        color_discrete_map={"college": TEAL, "school": AMBER},
    )
    fig.update_traces(textposition="outside", textfont=dict(color=TEXT))
    fig.update_layout(**base_layout(
        "Grade Delta medio per Purpose × Education Level  (AI Users only)"
    ))
    fig.update_yaxes(title="Δ Voto medio", range=[0, 15])
    fig.update_xaxes(title="")
    return fig


# ─────────────────────────────────────────────────────────────
# 7. TAB 5 — PERCEPTIONS
# ─────────────────────────────────────────────────────────────

def fig_feelings_stacked():
    """
    PERCHÉ: la proposal vuole uno stacked bar feelings × year of study.
    Curiosità domina (68.1%), Trust è bassa (7.7%) → gli studenti
    sono pragmatici, non ingenui. Il confronto per anno mostra
    che gli studenti del 1° anno hanno più paura (17.6% vs 10.5%).
    """
    order_feel = ["Curiosity", "Trust", "Indifference", "Fear"]
    ct = pd.crosstab(df2["feeling_label"], df2["Q13.Year_of_study"])
    ct_pct = (ct.div(ct.sum()) * 100).round(1)  # percentuale per anno

    fig = go.Figure()
    for feel in order_feel:
        if feel not in ct_pct.index:
            continue
        vals = ct_pct.loc[feel]
        fig.add_trace(go.Bar(
            name=feel,
            x=[f"Anno {y}" for y in vals.index],
            y=vals.values,
            marker_color=FEEL_COL.get(feel, GREY),
            text=[f"{v:.0f}%" for v in vals.values],
            textposition="inside",
            textfont=dict(color=BG, size=11),
        ))

    fig.update_layout(**base_layout(
        "Sentimento verso l'AI per Anno di Studio  (Survey, n=91)"
    ), barmode="stack")
    fig.update_yaxes(title="% studenti", range=[0, 105])
    fig.update_xaxes(title="")
    return fig


def fig_radar_risk():
    """
    PERCHÉ: il radar visualizza le 4 dimensioni di rischio percepito
    (Q3). Il profilo asimmetrico è il finding chiave: problem-solving
    (beneficio) = 4.20/5, mentre rischi sociali (dehumanization,
    AI ruling society) restano sotto 2.6 → gli studenti vedono
    l'AI come strumento, non come minaccia esistenziale.
    """
    labels = ["Dehumanization\n(Q3#1)", "Job\nReplacement\n(Q3#2)",
              "Problem\nSolving\n(Q3#3)", "AI Ruling\nSociety\n(Q3#4)"]
    cols   = ["Q3#1.AI_dehumanization","Q3#2.Job_replacement",
              "Q3#3.Problem_solving","Q3#4.AI_rulling_society"]
    vals   = df2[cols].mean().round(2).tolist()
    vals_closed = vals + [vals[0]]   # chiudi il radar
    labels_closed = labels + [labels[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor=f"rgba(45,212,191,0.15)",
        line=dict(color=TEAL, width=2),
        marker=dict(color=TEAL, size=7),
        name="Percezione media",
        hovertemplate="%{theta}: <b>%{r:.2f}/5</b><extra></extra>",
    ))

    # Media campione (area grigia di riferimento)
    avg = 2.5
    ref = [avg] * len(labels_closed)
    fig.add_trace(go.Scatterpolar(
        r=ref, theta=labels_closed,
        fill="toself",
        fillcolor="rgba(100,116,139,0.08)",
        line=dict(color=GREY, width=1, dash="dot"),
        name="Neutro (2.5/5)",
    ))

    fig.update_layout(
        **base_layout("Percezione dei Rischi AI (scala 1–5, Survey n=91)", height=420),
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[0,5], gridcolor=GRIDD,
                            tickfont=dict(color=SUBTEXT), tickvals=[1,2,3,4,5]),
            angularaxis=dict(gridcolor=GRIDD, tickfont=dict(color=TEXT, size=10)),
        ),
    )
    return fig


def fig_edu_advantages():
    """
    PERCHÉ: Q8–Q11 mostrano la dualità percettiva degli studenti —
    riconoscono sia vantaggi (teaching, learning) che svantaggi
    nel processo educativo. Scala inversa: 1=forte accordo, 5=disaccordo.
    Questo co-esistere di beneficio e svantaggio percepito è la versione
    "soggettiva" del paradosso proposto.
    Nota: valori vicini a 2 = forte accordo.
    """
    labels = ["Vantaggio\nInsegnamento\n(Q8)", "Vantaggio\nApprendimento\n(Q9)",
              "Vantaggio\nValutazione\n(Q10)", "Svantaggio\nProcesso Edu.\n(Q11)"]
    cols   = ["Q8.Advantage_teaching","Q9.Advantage_learning",
              "Q10.Advantage_evaluation","Q11.Disadvantage_educational_process"]
    vals   = [round(df2[c].mean(), 2) for c in cols]
    colors = [TEAL, TEAL, TEAL, RED]

    fig = go.Figure(go.Bar(
        x=labels, y=vals,
        marker_color=colors,
        text=[f"{v}" for v in vals],
        textposition="outside",
        textfont=dict(color=TEXT),
        width=0.5,
        hovertemplate="%{x}<br>Media: %{y:.2f}<br><i>(1=forte accordo, 5=disaccordo)</i><extra></extra>",
    ))

    # Linea di riferimento = neutro (valore 3)
    fig.add_hline(y=3, line_dash="dot", line_color=AMBER,
                  annotation_text="Neutro (3/5)",
                  annotation_font_color=AMBER, annotation_font_size=10)

    fig.add_annotation(
        x=3.2, y=2.6,
        text="← Gli studenti concordano con\nSIA i vantaggi CHE gli svantaggi",
        showarrow=False,
        font=dict(color=SUBTEXT, size=9),
    )

    fig.update_layout(**base_layout(
        "Vantaggi e Svantaggi AI nel processo educativo  (Survey n=91 — 1=accordo, 5=disaccordo)"
    ))
    fig.update_yaxes(title="Punteggio medio", range=[0, 4])
    fig.update_xaxes(title="")
    return fig


# ─────────────────────────────────────────────────────────────
# 8. DASH LAYOUT
# ─────────────────────────────────────────────────────────────
kpis = dict(
    final_ai   = round(df1[df1["uses_ai"]==1]["final_score"].mean(), 1),
    final_non  = round(df1[df1["uses_ai"]==0]["final_score"].mean(), 1),
    concept_ai = round(df1[df1["uses_ai"]==1]["concept_understanding_score"].mean(), 2),
    concept_non= round(df1[df1["uses_ai"]==0]["concept_understanding_score"].mean(), 2),
    delta      = round(df3[df3["uses_ai"]=="Yes"]["grade_delta"].mean(), 2),
    utility    = round(df2["Q7.Utility_grade"].mean(), 2),
)

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

TABS_STYLE   = {"backgroundColor": BG,   "border": "none", "padding": "0 32px"}
TAB_STYLE    = {"backgroundColor": BG,   "color": SUBTEXT,   "border": "none",
                "padding": "12px 20px",  "fontFamily": "'DM Sans',sans-serif",
                "fontSize": "13px",      "fontWeight": "500"}
TAB_SEL      = {**TAB_STYLE, "color": TEAL,
                "borderBottom": f"2px solid {TEAL}", "backgroundColor": CARD}

def section(title, children, insight=None):
    inner = [html.H3(title, style={"color": TEXT, "fontWeight": "600",
                                   "marginBottom": "16px", "fontSize": "15px"})]
    if insight:
        inner.append(html.Div(insight, style={
            "background": f"rgba(251,191,36,0.08)", "borderLeft": f"3px solid {AMBER}",
            "padding": "10px 14px", "borderRadius": "4px", "fontSize": "12px",
            "color": SUBTEXT, "marginBottom": "16px", "lineHeight": "1.6",
        }))
    inner += children
    return html.Div(inner, style=PANEL)


app.layout = html.Div(style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 24px"}, children=[

    # ── HEADER ──
    html.Div(style={"padding": "36px 0 20px"}, children=[
        html.Div("DATA VISUALIZATION PROJECT · Bianchi & Faour", style={
            "color": SUBTEXT, "fontSize": "11px", "letterSpacing": "2px",
            "textTransform": "uppercase", "marginBottom": "8px",
        }),
        html.H1("Does AI Boost Grades While Undermining Real Understanding?",
                style={"color": TEXT, "fontSize": "26px", "fontWeight": "700",
                       "lineHeight": "1.3", "marginBottom": "6px"}),
        html.Div("The Paradox of Artificial Performance",
                 style={"color": TEAL, "fontSize": "14px", "fontWeight": "500"}),
    ]),

    # ── KPI CARDS ──
    html.Div(style={"display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "16px", "marginBottom": "24px"}, children=[
        kpi_card("Final Score — AI Users",   f"{kpis['final_ai']}",
                 f"vs Non-Users: {kpis['final_non']}  (Δ≈0, p=0.88)", TEAL),
        kpi_card("Concept Understanding",   f"{kpis['concept_ai']}",
                 f"AI vs Non-AI: {kpis['concept_non']}  (Δ≈0, p=0.73)", GREY),
        kpi_card("Grade Delta — AI Adopters", f"+{kpis['delta']} pt",
                 "media su 40 studenti  (Dataset 3)", GREEN),
        kpi_card("Perceived AI Utility",    f"{kpis['utility']}/10",
                 "mediana 8.0 · n=91 studenti  (Survey)", AMBER),
    ]),

    # ── TABS ──
    dcc.Tabs(style=TABS_STYLE, children=[

        # TAB 1 — OVERVIEW
        dcc.Tab(label="1 · Overview", style=TAB_STYLE, selected_style=TAB_SEL, children=[
            html.Div(style={"paddingTop": "24px"}, children=[
                html.Div(style={"display":"grid","gridTemplateColumns":"2fr 1fr","gap":"20px"}, children=[
                    section("Media punteggi: AI Users vs Non-Users",
                            [dcc.Graph(figure=fig_overview_bar(), config={"displayModeBar": False})],
                            insight="Dataset sintetico: le medie sono quasi identiche (p=0.88). "
                                    "Questo non significa che l'AI non abbia effetto — significa che "
                                    "il dataset 1 non può rispondere a questa domanda. "
                                    "Il segnale reale è nel Tab 4 (Grade Delta, Dataset 3)."),
                    section("Distribuzione Performance Category",
                            [dcc.Graph(figure=fig_donut(), config={"displayModeBar": False})],
                            insight="La maggioranza degli studenti (58.8%) ricade nella categoria Medium. "
                                    "Solo il 9.4% è High performer."),
                ])
            ])
        ]),

        # TAB 2 — THE PARADOX
        dcc.Tab(label="2 · The Paradox", style=TAB_STYLE, selected_style=TAB_SEL, children=[
            html.Div(style={"paddingTop": "24px"}, children=[
                section("Punteggi per Categoria di Performance",
                        [dcc.Graph(figure=fig_paradox_grouped_bar(), config={"displayModeBar": False})],
                        insight="Il finding chiave: la linea tratteggiata amber (AI Dependency) è piatta "
                                "tra High, Medium e Low performer. Chi ottiene voti alti non è più o meno "
                                "dipendente dall'AI — la dipendenza non spiega il gap di performance."),
                section("AI Content % vs Concept Understanding",
                        [dcc.Graph(figure=fig_scatter_paradox(), config={"displayModeBar": False})],
                        insight="r = 0.022: nessuna correlazione. Nei dati sintetici, produrre più contenuto "
                                "AI-generated non abbassa (né alza) la comprensione concettuale. "
                                "Nella realtà questa è la domanda aperta che il dashboard vuole porre."),
            ])
        ]),

        # TAB 3 — DEPENDENCY LENS
        dcc.Tab(label="3 · Dependency Lens", style=TAB_STYLE, selected_style=TAB_SEL, children=[
            html.Div(style={"paddingTop": "24px"}, children=[
                html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px"}, children=[
                    section("Heatmap: Dipendenza × Etica → Concept Understanding",
                            [dcc.Graph(figure=fig_heatmap(), config={"displayModeBar": False})],
                            insight="Range effettivo: 5.14–5.77. La quasi-uniformità è il messaggio: "
                                    "nel dataset sintetico non emerge alcun gradiente. "
                                    "Nella realtà, ci aspetteremmo alta dipendenza + bassa etica → "
                                    "concept score più basso."),
                    section("Punteggi per Quartile di Dipendenza",
                            [dcc.Graph(figure=fig_dependency_bars(), config={"displayModeBar": False})],
                            insight="Anche qui: nessuna variazione sistematica tra Q1 (bassa dipendenza) "
                                    "e Q4 (alta dipendenza). La struttura del grafico resta utile come "
                                    "template per dati reali."),
                ])
            ])
        ]),

        # TAB 4 — GRADE DELTA
        dcc.Tab(label="4 · Grade Delta ⭐", style=TAB_STYLE, selected_style=TAB_SEL, children=[
            html.Div(style={"paddingTop": "24px"}, children=[
                section("Slope Chart: Voti Prima → Dopo l'AI",
                        [dcc.Graph(figure=fig_slope_chart(), config={"displayModeBar": False})],
                        insight="Segnale più forte del progetto: tutti i 40 studenti AI migliorano "
                                "(Δ medio = +9.82 pt, range +5 a +15). "
                                "Research college ottiene il delta più alto (+12 pt). "
                                "Le linee grigie piatte (non-users) sono un artefatto sintetico."),
                section("Grade Delta per Purpose × Education Level",
                        [dcc.Graph(figure=fig_delta_by_purpose(), config={"displayModeBar": False})],
                        insight="Research college (+12.0) > Coding (+10.8) > Homework (+9.0). "
                                "L'uso cognitivamente impegnativo dell'AI produce guadagni maggiori — "
                                "coerente con la narrativa della proposal."),
            ])
        ]),

        # TAB 5 — PERCEPTIONS
        dcc.Tab(label="5 · Perceptions", style=TAB_STYLE, selected_style=TAB_SEL, children=[
            html.Div(style={"paddingTop": "24px"}, children=[
                html.Div(style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"20px"}, children=[
                    section("Sentimento verso l'AI per Anno di Studio",
                            [dcc.Graph(figure=fig_feelings_stacked(), config={"displayModeBar": False})],
                            insight="Curiosità domina (68.1%), Trust è bassa (7.7%). "
                                    "Gli studenti del 1° anno mostrano più paura (17.6% vs 10.5% al 2°). "
                                    "Adozione pragmatica, non ingenua."),
                    section("Percezione dei Rischi AI (Radar Q3)",
                            [dcc.Graph(figure=fig_radar_risk(), config={"displayModeBar": False})],
                            insight="Problem-solving (4.20/5) è l'unico item vicino all'accordo pieno. "
                                    "Rischi sociali (dehumanization 2.52, AI ruling society 2.43) "
                                    "restano sotto il neutro. Il profilo asimmetrico è il finding chiave."),
                ]),
                section("Vantaggi e Svantaggi AI nell'Educazione (Q8–Q11)",
                        [dcc.Graph(figure=fig_edu_advantages(), config={"displayModeBar": False})],
                        insight="Gli studenti concordano SIA con i vantaggi (Q8 learning: 1.88/5) "
                                "SIA con lo svantaggio nel processo educativo (Q11: 2.10/5). "
                                "Questa co-esistenza è la versione soggettiva del paradosso."),
            ])
        ]),
    ]),

    # ── FOOTER ──
    html.Div(style={"padding": "32px 0 40px", "textAlign": "center",
                    "color": SUBTEXT, "fontSize": "11px", "letterSpacing": "1px"}, children=[
        html.Div("Dataset 1: ai_impact_student_performance_dataset.csv (n=8 000, sintetico)  ·  "
                 "Dataset 2: Survey_AI.csv (n=91, reale)  ·  "
                 "Dataset 3: students_ai_usage.csv (n=100, semi-sintetico)"),
        html.Div("Francesco Bianchi 264692  ·  Hassan Faour 265917  ·  "
                 "Built with Python / Plotly Dash",
                 style={"marginTop": "6px"}),
    ]),
])

if __name__ == "__main__":
    app.run(debug=True, port=8050)