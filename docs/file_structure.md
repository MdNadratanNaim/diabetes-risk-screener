```text
diabetes-risk-screener/
├── data/
│   └── diabetes_binary_health_indicators_BRFSS2015.csv
├── notebooks/
│   ├── Data Analysis.ipynb
│   ├── LogisticRegression_Hyperparameter_Tuning.ipynb
│   ├── Model_Comparison_and_Deployment.ipynb
│   ├── RandomForest_Hyperparameter_Tuning.ipynb
│   ├── README.md
│   └── XGBoost_Hyperparameter_Tuning.ipynb
├── model/
│   ├── model_metadata.json
│   ├── model.pkl
│   └── tuning_results.json
├── app/                        # FastAPI app
│   ├── main.py
│   ├── schema.py
│   └── templates/
│       ├── favicon.ico
│       ├── favicon.svg
│       └── index.html
├── Dockerfile
├── pyproject.toml
├── README.md
├── uv.lock
├── .python-version
├── .dockerignore
└── .gitignore
```
