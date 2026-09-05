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

SECOND CORRECTION: the fix above still read data/splits/Drug_B36N36_{Pristine,
COOH}_*.csv, whose Docking_Score_kcal_mol was ITSELF fabricated by
sync_real_data_and_train.py (empirical RDKit-descriptor formula, never a real
docking/quantum calculation -- see generate_all_q1_figures.py). Now uses
dataset_isolated_drugs.csv (real Vina) and dataset_tnbc_bn_pristine.csv (real
GFN2-xTB delta_Eint_SP_kcal_mol, all 33 compounds); the B36N36-COOH panel is
omitted since no real structural/quantum data exists for it.
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
    proc_dir = os.path.join(base_dir, "data", "processed")
    fig_dir = os.path.join(base_dir, "figures")

    alpha_grid = np.array([0.001, 0.01, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0])

    systems = [
        ("(a) Isolated Drugs", os.path.join(proc_dir, "dataset_isolated_drugs.csv"),
         ["MW", "LogP", "Polarizability_alpha", "Electrophilicity_omega"], "Docking_Score_kcal_mol", "#1565C0"),
        (r"(b) Drug + $B_{36}N_{36}$ Pristine (real xTB)", os.path.join(proc_dir, "dataset_tnbc_bn_pristine.csv"),
         ["MolWt", "MolMR", "E_HOMO_eV", "Omega_eV"], "delta_Eint_SP_kcal_mol", "#2E7D32"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5), dpi=300)

    for idx, (title, f_path, desc_cols, target_col, col) in enumerate(systems):
        if not os.path.exists(f_path):
            continue
        df_full = pd.read_csv(f_path).dropna(subset=desc_cols + [target_col])

        X = df_full[desc_cols].values
        y = df_full[target_col].values
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
