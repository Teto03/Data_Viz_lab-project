# Ricostruire il virtual environment (venv)

Questa cartella è parte di un repository GitHub. Il virtual environment non dovrebbe essere tracciato nel repository; conserva invece `requirements.txt` e ricostruisci il venv localmente quando necessario.

Comandi (Linux) per cancellare e ricreare il `venv` e installare le dipendenze:

```bash
cd /path/to/project  # es. /home/teto/Scrivania/Data_Viz_lab-project/viz_project
rm -rf venv
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Verifiche rapide dopo l'attivazione:

```bash
which python
python --version
python app.py
```

Suggerimenti Git/GitHub:

- Aggiungi `venv/` a `.gitignore` se non è già presente.
- Committa solo `requirements.txt` e file sorgente, non il venv.

Se vuoi, posso aggiungere una regola a `.gitignore` per te.
