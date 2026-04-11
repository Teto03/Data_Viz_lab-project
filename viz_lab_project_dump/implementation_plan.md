# Goal Description

The objective is to design an interactive data visualization dashboard using Python and Plotly Dash based on your proposal document. The dashboard will explore the "Paradox of Artificial Performance" by answering the central question: *Does AI Boost Grades While Undermining Real Understanding?*

The dashboard will use the three provided datasets (`ai_impact_student_performance_dataset.csv`, `Survey_AI.csv`, and `students_ai_usage.csv`) to guide the user through five narrative steps:
1. Establishing the baseline performance of AI users vs. non-users.
2. Introducing the paradox (grades vs. concept understanding).
3. Quantifying AI dependency.
4. Exploring the perceptual layer (student survey).
5. Comparing the grade delta (before vs. after AI adoption).

The design will feature a premium, dynamic, and aesthetic dark mode layout with interactive charts, smooth hover effects, glassmorphic elements, and modern typography to meet the "rich aesthetics" requirement.

## User Review Required

- **Dependencies**: The project requires standard data science and web visualization libraries (`dash`, `pandas`, `plotly`). I will create a `requirements.txt` file and prompt you to install them.
- **Aesthetics**: I am planning to implement a custom premium dark mode aesthetic using vanilla CSS (`assets/style.css`). This provides the most flexibility for creating a "wow" factor compared to stock bootstrap templates.

## Proposed Changes

### Dashboard Application

#### [NEW] `app.py`
The central Python application containing:
- Data loading and preprocessing pipelines for the 3 CSV files.
- Dash application instance setup.
- App layout structuring the narrative arc into distinct sections.
- Callbacks for interactivity (e.g., filtering by demographic or AI tool, updating charts).
- Plotly Figure generators for each analytical layer:
  - **Baseline**: Bar charts comparing average `final_score`.
  - **Paradox**: Scatter plot or 2D density plot for `final_score` vs. `concept_understanding_score`.
  - **Dependency**: Heatmap or bubble chart mapping `ai_dependency_score` against academic outcomes.
  - **Perceptions**: Horizontal bar charts and pie charts derived from `Survey_AI.csv`.
  - **Impact**: Slope chart visualizing `grades_before_ai` to `grades_after_ai`.

#### [NEW] `assets/style.css`
A vanilla CSS file to structure the dashboard layout using CSS Grid/Flexbox and apply rich styling:
- Dark mode theme base (deep slate/blue hues).
- Glassmorphism effects (translucent backgrounds with blur) for widget cards.
- Custom modern fonts (e.g., Google's Inter or Roboto) imported via `@import`.
- Micro-animations for hover states and transitions to make the dashboard feel alive.

#### [NEW] `requirements.txt`
A list of necessary python packages to set up the environment.

## Open Questions

> [!IMPORTANT]
> 1. **Color Palette**: I will design a modern dark theme with vibrant accents (like cyan and magenta/purple) to signify AI, which works well for dark mode. Do you approve of this scheme?
> 2. **Layout Approach**: I will use standard Dash HTML components styled with vanilla Flexbox/Grid CSS to achieve a high-end look rather than relying on Bootstrap defaults. Does this approach work for you?

## Verification Plan

### Automated Tests
- Syntax and runtime check by executing `python app.py` to ensure it successfully loads the datasets and binds to the port.

### Manual Verification
- You will be asked to run the dashboard locally, view it in your browser (`http://127.0.0.1:8050/`), and visually confirm the design aesthetics, chart interactions, and data representation align with the proposal's vision.
