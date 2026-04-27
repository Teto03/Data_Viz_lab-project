# Data Visualization Project

Welcome to the Data Visualization project! Follow these steps to set up your local environment and run the application after cloning the repository from GitHub.

## Prerequisites

Make sure you have **Python 3** and `pip` installed on your system. You can check your version by running `python --version` in your terminal.

## Setup Instructions

### 1. Navigate to the Project Folder

Open your terminal or command prompt and move into the main directory of the cloned project:

```bash
cd Data_Viz_lab-project
```

### 2. Create a Virtual Environment

It is best practice to run Python projects inside a virtual environment to keep dependencies isolated. Create a new one named `venv` by running:

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Before installing dependencies, you must activate the environment based on your operating system:

- **Windows:**

```bash
venv\Scripts\activate
```

- **macOS / Linux:**

```bash
source venv/bin/activate
```

> **Note:** Once activated, your terminal prompt should show `(venv)` at the beginning.

### 4. Install Dependencies

Install all the required Python packages for this project:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

Now you are ready to launch the app! Execute the main script:

```bash
python app.py
```

After running this command, the application will start. If it is a web-based dashboard (like Dash or Streamlit), look for a local URL in your terminal (usually `http://127.0.0.1:8050`) and open it in your browser.

---

## Troubleshooting

- **Python Command:** Depending on your installation, you might need to use `python3` instead of `python`.
- **Pip Upgrade:** If you encounter installation issues, try upgrading pip first:
  ```bash
  python -m pip install --upgrade pip
  ```
- **Missing Requirements:** Ensure the `requirements.txt` file is present in the root folder before running the install command.