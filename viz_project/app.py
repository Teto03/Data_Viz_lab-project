# app.py
"""
=============================================================
  AI Impact Dashboard — app.py  (v2 — Refactored)
  "Does AI Boost Grades While Undermining Real Understanding?"
  Francesco Bianchi (264692) · Hassan Faour (265917)
=============================================================
"""
import dash
from dash import dcc, html

# Local imports
from config import BG, CARD, TEAL, AMBER, RED, GREEN, GREY, TEXT, SUBTEXT
from data import adoption_pct, grade_gap_ext, grade_gap_rare, delta_ai, survey_utility
import figures as f

# ─────────────────────────────────────────────────────────────
# UI HELPERS
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

PANEL = {"background": CARD, "borderRadius": "12px", "padding": "24px", "marginBottom": "20px"}

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

# ─────────────────────────────────────────────────────────────
# DASH INIT & LAYOUT
# ─────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="AI & Learning — The Paradox")
app.index_string = """
<!DOCTYPE html>
<html>
<head>
  {%metas%}
  <title>{%title%}</title>
  {%favicon%}
  {%css%}
  <link href="[https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap](https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap)" rel="stylesheet">
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
            # TAB 1
            dcc.Tab(label="1 · Overview", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}, children=[
                        section("ChatGPT Adoption — Global Picture",
                                [dcc.Graph(figure=f.fig_adoption_donut(), config={"displayModeBar": False})],
                                insight="69% degli studenti universitari globali ha usato ChatGPT (Dataset 1, n=23 218, 109 paesi...)."),
                        section("Intensità d'uso tra gli utenti ChatGPT",
                                [dcc.Graph(figure=f.fig_usage_intensity_bar(), config={"displayModeBar": False})],
                                insight="La maggioranza usa ChatGPT in modo Occasionally/Moderately..."),
                    ]),
                    section("Tasso di adozione per campo di studi",
                            [dcc.Graph(figure=f.fig_field_adoption(), config={"displayModeBar": False})],
                            insight="Applied Sciences e Social Sciences hanno i tassi di adozione più alti..."),
                ])
            ]),
            # TAB 2
            dcc.Tab(label="2 · The Paradox ⭐", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Il Paradosso — Dati Reali (n=16 010)",
                            [dcc.Graph(figure=f.fig_paradox_lines(), config={"displayModeBar": False})],
                            insight="SEGNALE REALE (non sintetico): all'aumentare dell'intensità d'uso..."),
                    section("Gap per Campo di Studi × Intensità d'uso",
                            [dcc.Graph(figure=f.fig_hinder_vs_grades(), config={"displayModeBar": False})],
                            insight="Il paradosso è consistente tra tutti i campi di studi..."),
                ])
            ]),
            # TAB 3
            dcc.Tab(label="3 · Dependency Lens", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Heatmap: Task di utilizzo × Intensità d'uso",
                            [dcc.Graph(figure=f.fig_purpose_heatmap(), config={"displayModeBar": False})],
                            insight="Gli utenti intensivi usano ChatGPT per più task simultaneamente..."),
                    section("Tre metriche chiave per Intensità d'uso",
                            [dcc.Graph(figure=f.fig_dependency_paradox_bars(), config={"displayModeBar": False})],
                            insight="Notare: la preoccupazione 'AI hinders learning' (amber) DECRESCE..."),
                ])
            ]),
            # TAB 4
            dcc.Tab(label="4 · Grade Delta", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    section("Slope Chart: Grades Before → After AI adoption",
                            [dcc.Graph(figure=f.fig_slope_chart(), config={"displayModeBar": False})],
                            insight="Dataset 3 (semi-sintetico): tutti i 40 studenti AI migliorano..."),
                    section("Grade Delta by Purpose × Education Level",
                            [dcc.Graph(figure=f.fig_delta_by_purpose(), config={"displayModeBar": False})],
                            insight="Research college (+12.0) > Coding (+10.8) > Homework (+9.0)..."),
                ])
            ]),
            # TAB 5
            dcc.Tab(label="5 · Perceptions", style=TAB_STYLE, selected_style=TAB_SEL, children=[
                html.Div(style={"paddingTop": "24px"}, children=[
                    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}, children=[
                        section("Emozioni usando ChatGPT  (Dataset 1, n=16 010)",
                                [dcc.Graph(figure=f.fig_emotions_radar(), config={"displayModeBar": False})],
                                insight="Curious e Calm dominano..."),
                        section("Soddisfazione & Attitudine  (Dataset 1)",
                                [dcc.Graph(figure=f.fig_satisfaction_bars(), config={"displayModeBar": False})],
                                insight="'Using ChatGPT is interesting' e 'Helps in everyday life' sono i valori più alti..."),
                    ]),
                    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"}, children=[
                        section("Sentimento verso l'AI per Anno di Studio  (Survey_AI, n=91)",
                                [dcc.Graph(figure=f.fig_feelings_stacked(), config={"displayModeBar": False})],
                                insight="Curiosità domina..."),
                        section("Vantaggi e Svantaggi AI nell'Educazione  (Survey_AI)",
                                [dcc.Graph(figure=f.fig_edu_advantages(), config={"displayModeBar": False})],
                                insight="Gli studenti concordano SIA con i vantaggi SIA con lo svantaggio..."),
                    ]),
                ])
            ]),
        ]),
        # ── FOOTER ──
        html.Div(style={"padding": "32px 0 40px", "textAlign": "center",
                        "color": SUBTEXT, "fontSize": "11px", "letterSpacing": "1px"}, children=[
            html.Div("Dataset 1: final_dataset.xlsx — Aristovnik et al. (2024), n=23 218, 109 paesi (REALE) · Dataset 2: Survey_AI.csv (n=91, reale) · Dataset 3: students_ai_usage.csv (n=100, semi-sintetico)"),
            html.Div("Francesco Bianchi 264692 · Hassan Faour 265917 · Built with Python / Plotly Dash", style={"marginTop": "6px"}),
        ]),
    ]
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)