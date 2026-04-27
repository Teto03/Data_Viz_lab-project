# 📊 AI Impact Dashboard: The Paradox of Artificial Performance

> **"Does AI Boost Grades While Undermining Real Understanding?"**

A Data Visualization project exploring the impact of AI usage (e.g., ChatGPT) on global university students' grades and critical thinking. Built with Python and Plotly Dash.

**Authors:** Francesco Bianchi (264692) & Hassan Faour (265917)

## 📌 About the Project

This dashboard visualizes the "Paradox Gap"—the phenomenon where increased AI usage might correlate with higher grades but lower critical thinking and real understanding. We analyze three different datasets containing data from thousands of students globally to uncover trends in adoption, dependency, and performance.

### Key Insights Explored
- **Adoption:** Global ChatGPT adoption rates by field of study and usage intensity.
- **The Paradox:** Gap between grades and perceived critical thinking based on AI usage intensity.
- **Dependency:** How intensive users rely on AI for more tasks concurrently.
- **Grade Delta:** Analysis of grades before and after AI adoption.
- **Perceptions:** Student emotions, satisfaction, and attitudes toward AI in education.

## 🏗️ Architecture

This project follows a modular structure inside the `viz_project` directory, separated into four main components for better maintainability (Separation of Concerns):
- **`config.py`**: Visual configurations, themes, colors, and base layout styles.
- **`data.py`**: Data ingestion, cleaning, and KPI calculations.
- **`figures.py`**: Plotly chart generation.
- **`app.py`**: Dash initialization and User Interface layout.

## 📂 Datasets Used

1. **Global Survey (`final_dataset.xlsx`)**: REAL dataset (Aristovnik et al., 2024) containing 23,218 records across 109 countries.
2. **Local Survey (`Survey_AI.csv`)**: REAL survey addressing AI perception among students (n=91).
3. **Usage Metrics (`students_ai_usage.csv`)**: Semi-synthetic dataset modeling the impact of AI on grades (n=100).

## 🚀 Setup & Run Instructions

Follow these steps to set up your local environment and run the dashboard.

### 1. Prerequisites

Make sure you have **Python 3** and `pip` installed on your system. 

### 2. Access the Application Folder

Open your terminal and navigate to the `viz_project` folder inside the repository:

```bash
cd viz_project
```

### 3. Create a Virtual Environment (Recommended)

To keep dependencies isolated:

```bash
python -m venv venv
```

Activate it depending on your OS:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies

Install the required Python packages (`dash`, `pandas`, `plotly`, `statsmodels`):

```bash
pip install -r requirements.txt
```

### 5. Run the Dashboard

Launch the main script:

```bash
python app.py
```

Finally, open your browser and navigate to `http://127.0.0.1:8050` to view the dashboard!
