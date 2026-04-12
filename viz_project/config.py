# config.py

# ─────────────────────────────────────────────────────────────
# PALETTE & THEME
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