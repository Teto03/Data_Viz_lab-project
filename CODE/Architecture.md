# Architecture — AI Impact Dashboard

The project follows a modular structure based on the **Separation of Concerns** principle, split across four files:

```text
CODE/
 ├── config.py      # Colors, theme constants, and base Plotly layout
 ├── data.py        # Data ingestion, cleaning, and KPI calculations
 ├── figures.py     # Plotly chart generation (one function per chart)
 └── app.py         # Dash initialization, UI layout, and entry point
```

## Module responsibilities

| File | Responsibility |
|------|---------------|
| `config.py` | Palette constants (`BG`, `TEAL`, `AMBER`, …), field/feeling/purpose color maps, `USE_LABELS`, `base_layout()` helper |
| `data.py` | Loads all three datasets, builds derived columns, filters ChatGPT users, computes KPI scalars exported to `app.py` |
| `figures.py` | One function per chart; imports constants from `config` and DataFrames from `data`; returns a `go.Figure` |
| `app.py` | Defines `kpi_card()` / `section()` helpers, assembles the five-tab Dash layout, starts the server |
