# Data Visualization Project — Run Instructions

There are two ways to run the application: **Docker** (recommended) or **manually** with Python.

---

## Option A — Docker (Recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) installed on your system. No Python setup required.

From the **root of the repository** (one level above this folder), run:

```bash
docker compose up --build
```

Open your browser at `http://localhost:8050`.

To stop the container:

```bash
docker compose down
```

> On subsequent runs you can skip `--build` and just use `docker compose up`.

---

## Option B — Manual (Python)

**Prerequisites:** Python 3 and `pip` installed on your system.

### 1. Navigate to this folder

```bash
cd CODE
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python3 app.py
```

Open your browser at `http://127.0.0.1:8050`.

---

## Troubleshooting

- **`python` not found:** try `python3` instead.
- **Pip issues:** upgrade pip first with `python -m pip install --upgrade pip`.
- **Port already in use:** make sure nothing else is running on port 8050.
