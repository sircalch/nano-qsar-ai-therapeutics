"""
compute_oecd_applicability_domain.py
Computes the OECD Principle 3: Domain of Applicability (Williams Plot) for all QSAR models.
Calculates leverage values (h_i), critical threshold (h* = 3(p+1)/n), and standardized residuals.
Generates the Williams Plot figure for rigorous Q1 validation.

Standardized residuals are the real out-of-fold residuals from the leak-free
nested 5x5 Ridge CV (same model/descriptors as
make_fig7_parity_benchmark in generate_all_q1_figures.py) -- previously this
was `np.random.normal(0, 0.85/0.95, ...)`, completely disconnected from any
actual model fit. Leverage was already real (hat matrix on real descriptors);
only the residual axis was fabricated.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import KFold, cross_val_predict

def compute_williams_plot():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    splits_dir = os.path.join(base_dir, "data", "splits")
    fig_dir = os.path.join(base_dir, "figures")

    desc_cols = ["MW", "LogP", "Polarizability_alpha", "Electrophilicity_omega"]
    alpha_grid = np.array([0.001, 0.01, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0])

    systems = [
        ("Isolated_Drugs", "(a) Isolated Drugs", "#1565C0"),
        ("Drug_B36N36_Pristine", r"(b) Drug + $B_{36}N_{36}$ Pristine", "#2E7D32"),
        ("Drug_B36N36_COOH", r"(c) Drug + $B_{36}N_{36}\text{-COOH}$", "#C62828")
    ]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), dpi=300)

    for idx, (sys_id, title, col) in enumerate(systems):
        train_df = pd.read_csv(os.path.join(splits_dir, f"{sys_id}_train.csv"))
        val_df = pd.read_csv(os.path.join(splits_dir, f"{sys_id}_validation.csv"))
        df_full = pd.concat([train_df, val_df], ignore_index=True)

        X = df_full[desc_cols].values
        y = df_full["Docking_Score_kcal_mol"].values
        n, p = X.shape
        h_star = 3.0 * (p + 1.0) / n

        # Real hat-matrix leverage on the standardized descriptor space
        X_scaled = StandardScaler().fit_transform(X)
        H = X_scaled @ np.linalg.pinv(X_scaled.T @ X_scaled) @ X_scaled.T
        leverages = np.diag(H)

        # Real out-of-fold residuals from the same leak-free nested 5x5 Ridge CV
        # reported in Figure 7 / Table 2
        outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
        inner_cv = KFold(n_splits=5, shuffle=True, random_state=42)
        pipe = Pipeline([("scaler", StandardScaler()), ("ridge", RidgeCV(alphas=alpha_grid, cv=inner_cv))])
        y_pred = cross_val_predict(pipe, X, y, cv=outer_cv)
        residuals = y - y_pred
        std_residuals = residuals / np.std(residuals)

        ax = axes[idx]
        ax.scatter(leverages, std_residuals, color=col, alpha=0.85, s=70, edgecolors='k', label=f'Out-of-Fold (n={n})')

        # Warning limit lines
        ax.axhline(3.0, color='r', linestyle='--', lw=1.5, label=r'$\pm 3\sigma$ Outlier Boundary')
        ax.axhline(-3.0, color='r', linestyle='--', lw=1.5)
        ax.axhline(0.0, color='gray', linestyle='-', lw=0.8, alpha=0.6)
        ax.axvline(h_star, color='purple', linestyle=':', lw=2.0, label=f'Warning Limit ($h^* = {h_star:.2f}$)')

        inside = int(np.sum((leverages <= h_star) & (np.abs(std_residuals) <= 3.0)))
        ax.set_title(f"{title} -- {inside}/{n} inside AD", fontsize=11.5, fontweight='bold')
        ax.set_xlabel("Hat Leverage ($h_i$)", fontsize=10.5)
        ax.set_ylabel(r"OOF Standardized Residuals ($\delta_i$)", fontsize=10.5)
        ax.set_ylim([-4.0, 4.0])
        ax.legend(loc='lower left', fontsize=8.5, framealpha=0.9)

    plt.suptitle("Figure 8. OECD Principle 3: Williams Plots for Defining the QSAR Applicability Domain (Leak-Free Nested CV)",
                 fontsize=12.5, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_path = os.path.join(fig_dir, "fig8_williams_applicability_domain.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated OECD Williams Plot: {out_path}")

if __name__ == "__main__":
    compute_williams_plot()
