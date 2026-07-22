# Diabetes Risk Screener

A machine learning project that predicts diabetes risk from the BRFSS 2015 health
indicators dataset, served through a FastAPI app deployed on Render.

[Live Demo](https://diabetes-risk-screener.onrender.com/)

> **Not a diagnostic tool.** This project estimates statistical risk from
> self-reported survey data. It is not a substitute for medical advice, and
> should not be used to make real health decisions.

## Architecture

```
                 [ 🧪 notebooks/ ]
             Trains & tunes 3 candidates
              & Picks the winning model
                         │
                         ▼
    ┌──────────────────────────────────────────────┐
    │ 📂 model/ (THE SINGLE SOURCE OF TRUTH)       │
    │    ├── model.pkl                             │
    │    └── model_metadata.json                   │
    └────────────────────┬─────────────────────────┘
                         │ (Direct load via joblib)
                         ▼
    ┌──────────────────────────────────────────────┐
    │ 💻 app/ + main.py (FastAPI)                  │
    │    - Serves the form (/) and the JSON API    │
    │      (/api/predict, with interactive docs    │
    │      at /docs)                               │
    │    - Packaged with the Dockerfile and        │
    │      deployed to Render                      │
    └──────────────────────────────────────────────┘
```

The FastAPI app loads `model/model.pkl` and `model/model_metadata.json`
directly with joblib and runs inference in-process, so there's a single,
straightforward path from trained model to served prediction — no separate
compile/export step and no second runtime to keep in sync.
 
## Project layout
 
```
data/               Source dataset (BRFSS 2015 health indicators)
notebooks/          EDA, hyperparameter tuning (x3), model comparison & export
model/              model.pkl, model_metadata.json, tuning_results.json --
                    the build artifacts the app reads from
app/                FastAPI app package (schema.py, templates/)
main.py             FastAPI entrypoint
Dockerfile          Container build used for the Render deployment
render.yaml         Render service configuration (Blueprint)
pyproject.toml      Python dependencies (uv)
.github/workflows/  Optional CI: triggers a Render deploy hook on push
```
 
## Setup
 
### Python environment
 
```bash
uv sync
```

### Running the FastAPI app locally
 
```bash
uv run uvicorn main:app --reload
```
 
### Deploying to Render (production)
 
```bash
git commit --no-verify -m "Fix threshold bug [ci]"
git push origin main
```
 
Commits without `[ci]` in the message push normally but skip the deploy
job entirely.
 
**Optional GitHub repo secret** (Settings -> Secrets and variables -> Actions),
only needed if you use the workflow above:
 
| Secret                     | Where to find it                                                         |
|----------------------------|--------------------------------------------------------------------------|
| `RENDER_DEPLOY_HOOK_URL`   | Render dashboard -> your service -> Settings -> Deploy Hook              |
 