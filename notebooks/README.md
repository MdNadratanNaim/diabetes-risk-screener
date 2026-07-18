> ### The Metric Selection Framework

| Task Type | Dataset Condition | Recommended Metric | Optuna Direction | Strategic Reason |
| --- | --- | --- | --- | --- |
| **Binary Classification** | Balanced classes (e.g., 50/50 split of targets) | **Accuracy** or **Log Loss** | `maximize` / `minimize` | Simple and accurate when data is even. Log Loss penalizes confident wrong answers heavily. |
| **Binary Classification** | Heavily imbalanced classes (e.g., 99% valid, 1% fraud) | **F1-Score** or **PR-AUC** | `maximize` | Focuses strictly on the minority class so your model doesn't just guess the majority class every time. |
| **Binary Classification** | Mild imbalance, overall probability ranking matters | **ROC-AUC** | `maximize` | Measures how well the model separates the two classes across all possible decision thresholds. |
| **Multi-Class Classification** | Multiple classes with unequal group sizes | **Macro F1-Score** | `maximize` | Calculates the F1-score for each individual class and averages them, treating all classes with equal importance. |
| **Regression** | Standard target distribution, large mistakes are costly | **RMSE** | `minimize` | Root Mean Squared Error squares the differences, penalizing large misses drastically. |
| **Regression** | Target data has noisy, extreme outliers you want to ignore | **MAE** | `minimize` | Mean Absolute Error treats all errors linearly, meaning single extreme spikes won't warp your tuning. |
| **Regression** | Target scales vary widely (e.g., predicting prices from $10 to $10,000) | **MAPE** | `minimize` | Mean Absolute Percentage Error tracks the error *relative* to the actual size of the item. |

---

> ### Correlation rules

                     Continuous        Ordinal          Binary             Nominal
                ┌─────────────────┬─────────────────┬────────────────┬────────────────────────┐
     Continuous │    Pearson      │    Spearman     │ Point-Biserial │    ANOVA (R² / η²)     │
                ├─────────────────┼─────────────────┼────────────────┼────────────────────────┤
        Ordinal │    Spearman     │    Spearman     │    Spearman    │  Freeman's Theta / ε²  │
                ├─────────────────┼─────────────────┼────────────────┼────────────────────────┤
         Binary │ Point-Biserial  │    Spearman     │   Cramér's V   │ Cramér's V / Phi [2*2] │
                ├─────────────────┼─────────────────┼────────────────┼────────────────────────┤
        Nominal │ ANOVA (R²/Eta²) │ Freeman's Theta │   Cramér's V   │ Cramér's V / Theil's U │
                └─────────────────┴─────────────────┴────────────────┴────────────────────────┘




