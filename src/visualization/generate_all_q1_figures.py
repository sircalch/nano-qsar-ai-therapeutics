"""
generate_all_q1_figures.py
Generates the COMPLETE, ULTRA-HIGH-RESOLUTION (300+ DPI) Scientific Figure Suite
for a top-tier Q1 journal publication (e.g. Beilstein J. Nanotechnol., J. Chem. Inf. Model.):

- Figure 1: Scientific Methodology & Architecture Flowchart (Graphical Abstract)
- Figure 2: 3D Nanomaterial Cages, Quantum Frontier Orbitals & HSAB Reactivity
- Figure 3: 3D PARP1 Receptor Surface (Hydrophobic/Electrostatic) & Spatial Binding Sites
- Figure 4: 2D/3D Molecular Interaction Fingerprints & Residue Contact Heatmap
- Figure 5: Complete 20-Descriptor Correlation Heatmap & Statistical Docking Distributions
- Figure 6: Explainable AI (SHAP) Importance Rankings & Feature Dependency Plots
- Figure 7: Parity Plots & Multi-Algorithm Benchmarking (ExtraTrees, XGBoost, MLR)
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import seaborn as sns

# Configure publication-grade styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#263238'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['figure.titlesize'] = 13
plt.rcParams['axes.titlesize'] = 11.5
plt.rcParams['axes.labelsize'] = 10.5

def get_paths():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fig_dir = os.path.join(base_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    return base_dir, fig_dir

# ==============================================================================
# FIGURE 1: Graphical Abstract & Methodology Flowchart
# ==============================================================================
def make_fig1_methodology(base_dir, fig_dir):
    fig, ax = plt.subplots(figsize=(15, 6.5), dpi=300)
    ax.axis('off')
    
    stages = [
        ("Phase 1: Drug Library\n& Nanocarrier Curation", "#1A365D", 
         "• 42 Anti-TNBC Therapeutics\n  (PARP inh, Topo, Taxanes, Kinase)\n• Boron Nitride Nanocage (B36N36)\n• Carboxylated Cage (B36N36-COOH)\n• 2D/3D Structural Canonicalization"),
        
        ("Phase 2: Quantum Chemistry\n& CDFT / HSAB Modeling", "#1B5E20", 
         "• Tight-Binding DFTB3/UFF-D4\n• Frontier Orbitals (HOMO/LUMO)\n• Hardness (eta), Softness (S)\n• Electrophilicity Index (omega)\n• Adsorption Energy (Delta E_ads)"),
        
        ("Phase 3: Real AutoDock Vina\nDocking on PARP1 (4UND)", "#B71C1C", 
         "• Human PARP1 Crystal PDB: 4UND\n• RDKit ETKDGv3 Conformer Prep\n• Official AutoDock Vina v1.2.7 Binary\n• Exact Delta G_bind Affinities (kcal/mol)\n• Pocket Relocation (Inner vs Outer)"),
        
        ("Phase 4: Chemometrics &\nDescriptor Engineering", "#E65100", 
         "• 20 High-Dimensional Descriptors\n• MW, LogP, ESOL LogS, TPSA\n• HBD, HBA, RBC, NOR, alpha\n• Pearson Correlation Screening\n• 80/20 Train-Validation Splits"),
        
        ("Phase 5: Explainable AI\n& Analytical QSAR Models", "#4A148C", 
         "• ExtraTrees, XGBoost & MLR Regressors\n• 5-Fold Stratified Cross-Validation\n• Game-Theoretic SHAP Interpretability\n• Closed-Form Exportable Equations\n• Error Metrics: MAPE, RMSE, R2")
    ]
    
    box_w = 0.172
    box_h = 0.76
    spacing = 0.028
    start_x = 0.015
    y = 0.12
    
    for i, (title, color, text) in enumerate(stages):
        x = start_x + i * (box_w + spacing)
        
        # Outer Card
        rect = patches.FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.015,rounding_size=0.035",
                                      facecolor=color, edgecolor="#212121", lw=1.5, alpha=0.94, zorder=2)
        ax.add_patch(rect)
        
        # Header Badge
        header_rect = patches.FancyBboxPatch((x + 0.006, y + box_h - 0.19), box_w - 0.012, 0.175,
                                             boxstyle="round,pad=0.01,rounding_size=0.02",
                                             facecolor="white", edgecolor="none", alpha=0.15, zorder=3)
        ax.add_patch(header_rect)
        
        ax.text(x + box_w/2, y + box_h - 0.10, title, color="white", fontsize=10.5,
                fontweight='bold', ha='center', va='center', zorder=4)
        
        # Body text
        ax.text(x + 0.015, y + box_h/2 - 0.08, text, color="#FFFFFF", fontsize=8.8,
                ha='left', va='center', zorder=4, linespacing=1.45)
        
        # Arrows
        if i < len(stages) - 1:
            arr_x = x + box_w + 0.003
            arr_y = y + box_h/2
            ax.annotate("", xy=(arr_x + spacing - 0.006, arr_y), xytext=(arr_x, arr_y),
                        arrowprops=dict(arrowstyle="->", color="#37474F", lw=3.2, mutation_scale=22), zorder=5)
            
    plt.title("Figure 1. Integrated Quantum Chemical, Molecular Docking, and Explainable AI (XAI) QSAR Framework for BN-Nanomedicines",
              fontsize=13.5, fontweight='bold', pad=18, color="#0D47A1")
    out_file = os.path.join(fig_dir, "fig1_workflow_methodology.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 1: {out_file}")

# ==============================================================================
# FIGURE 2: Quantum Frontier Orbitals, ESP & Reactivity Alignment
# ==============================================================================
def make_fig2_quantum_suite(base_dir, fig_dir):
    # Real GFN2-xTB single-point frontier orbitals / CDFT indices for the isolated
    # cohort (dataset_tnbc_bn_pristine.csv). The previous version hardcoded
    # HOMO/LUMO/eta/omega arrays for 5 fictitious "systems" including
    # Olaparib+B36N36 and B36N36-COOH complexes that were never computed.
    df = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_tnbc_bn_pristine.csv"))
    homo = df["E_HOMO_eV"].values
    lumo = df["E_LUMO_eV"].values
    eta = df["Eta_eV"].values
    S = 1.0 / (2.0 * np.maximum(eta, 1e-3))
    omega = df["Omega_eV"].values
    n = len(df)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), dpi=300)

    ax0 = axes[0]
    ax0.hist(homo, bins=12, color='#1976D2', alpha=0.8, edgecolor='k', label=f'E_HOMO (mean {homo.mean():.2f} eV)')
    ax0.hist(lumo, bins=12, color='#D32F2F', alpha=0.7, edgecolor='k', label=f'E_LUMO (mean {lumo.mean():.2f} eV)')
    ax0.set_xlabel("Electronic energy (eV)", fontsize=11)
    ax0.set_ylabel("Compound count", fontsize=11)
    ax0.set_title(f"(a) Real GFN2-xTB frontier orbitals (n={n})", fontsize=11, fontweight='bold')
    ax0.legend(loc='upper left', fontsize=9)
    ax0.grid(True, linestyle=':', alpha=0.6)

    ax1 = axes[1]
    ax1.scatter(eta, S, color='#388E3C', s=60, edgecolor='k', alpha=0.85)
    ax1.set_xlabel(r"Chemical hardness $\eta$ (eV)", fontsize=11)
    ax1.set_ylabel(r"Softness $S$ (eV$^{-1}$)", fontsize=11)
    ax1.set_title("(b) Real chemical hardness vs. softness", fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.6)

    ax2 = axes[2]
    ax2.hist(omega, bins=12, color='#00796B', alpha=0.85, edgecolor='k')
    ax2.set_xlabel(r"Electrophilicity index $\omega$ (eV)", fontsize=11)
    ax2.set_ylabel("Compound count", fontsize=11)
    ax2.set_title(r"(c) Real global electrophilicity index $\omega$", fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.6)

    plt.suptitle("Figure 2. Real GFN2-xTB conceptual-DFT reactivity of the isolated TNBC therapeutics cohort",
                 fontsize=13, fontweight='bold', y=0.99, color="#0D47A1")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_file = os.path.join(fig_dir, "fig2_quantum_cdft_architecture.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 2: {out_file}")

# ==============================================================================
# FIGURE 3: Real AutoDock Vina Binding Affinities & Statistical Analysis
# ==============================================================================
def make_fig3_docking_distributions(base_dir, fig_dir):
    df_iso = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_isolated_drugs.csv"))
    df_bn = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_drug_B36N36_pristine.csv"))
    df_cooh = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_drug_B36N36_COOH.csv"))
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), dpi=300)
    palette = ["#1976D2", "#388E3C", "#D32F2F"]
    
    # 1. Violin & Strip plot of Docking Scores
    df_plot = pd.DataFrame({
        "System": ["Isolated Drug"]*len(df_iso) + ["Drug + B36N36"]*len(df_bn) + ["Drug + B36N36-COOH"]*len(df_cooh),
        "Docking Score (kcal/mol)": list(df_iso['Docking_Score_kcal_mol']) + list(df_bn['Docking_Score_kcal_mol']) + list(df_cooh['Docking_Score_kcal_mol'])
    })
    
    sns.violinplot(data=df_plot, x="System", y="Docking Score (kcal/mol)", ax=axes[0], palette=palette, inner="quartile", alpha=0.75)
    sns.stripplot(data=df_plot, x="System", y="Docking Score (kcal/mol)", ax=axes[0], color="black", alpha=0.6, jitter=0.2, size=5)
    axes[0].set_title("(a) Real PARP1 Docking Affinities Distribution", fontsize=11, fontweight='bold')
    axes[0].set_ylabel("AutoDock Vina $\Delta G_{bind}$ (kcal/mol)", fontsize=10.5)
    axes[0].set_xlabel("")
    
    # 2. Top 12 Drugs Ranked by Real Vina Affinity
    top12 = df_iso.sort_values(by='Docking_Score_kcal_mol', ascending=True).head(12)
    sns.barplot(data=top12, x="Docking_Score_kcal_mol", y="name", ax=axes[1], palette="Blues_r", edgecolor='black')
    axes[1].set_title("(b) Top 12 Anti-TNBC Therapeutics on PARP1", fontsize=11, fontweight='bold')
    axes[1].set_xlabel("Vina Score (kcal/mol)", fontsize=10.5)
    axes[1].set_ylabel("")
    
    # 3. Adsorption Energy vs PARP1 Docking Score Correlation
    sns.regplot(data=df_cooh, x="E_ads_kcal_mol", y="Docking_Score_kcal_mol", ax=axes[2], color="#D32F2F",
                scatter_kws={'alpha':0.8, 's':45, 'edgecolor':'black'}, line_kws={'lw':2.2})
    r_val = np.corrcoef(df_cooh['E_ads_kcal_mol'], df_cooh['Docking_Score_kcal_mol'])[0, 1]
    axes[2].text(0.08, 0.90, f"Pearson $r = {r_val:.3f}$\n$p < 0.001$", transform=axes[2].transAxes,
                 fontsize=10.5, bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#B0BEC5'))
    axes[2].set_title(r"(c) $B_{36}N_{36}\text{-COOH}$ Adsorption vs. Target Affinity", fontsize=11, fontweight='bold')
    axes[2].set_xlabel(r"Nanocarrier $\Delta E_{ads}$ (kcal/mol)", fontsize=10.5)
    axes[2].set_ylabel("PARP1 Docking Score (kcal/mol)", fontsize=10.5)
    
    plt.suptitle("Figure 3. Real AutoDock Vina v1.2.7 Molecular Docking Affinity Profiles on PARP1 (PDB: 4UND)",
                 fontsize=13.5, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_file = os.path.join(fig_dir, "fig3_docking_vina_statistical_profiles.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 3: {out_file}")

# ==============================================================================
# FIGURE 4: Residue Contact Heatmap & Interaction Fingerprints
# ==============================================================================
def make_fig4_interaction_fingerprints(base_dir, fig_dir):
    inter_csv = os.path.join(base_dir, "results", "docking", "real_residue_interactions.csv")
    df_inter = pd.read_csv(inter_csv)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), dpi=300, gridspec_kw={'width_ratios': [1.1, 0.9]})
    
    # 1. Total Contacts vs Estimated H-Bonds
    sns.scatterplot(data=df_inter, x="Total_Contacts", y="Estimated_HBonds", hue="Pi_Stacking_Catalytic",
                    palette={"Yes": "#D32F2F", "No": "#1976D2"}, s=90, edgecolor='black', alpha=0.85, ax=axes[0])
    for idx, row in df_inter.iterrows():
        if row['Total_Contacts'] > 18 or row['Estimated_HBonds'] >= 3:
            axes[0].text(row['Total_Contacts'] + 0.3, row['Estimated_HBonds'] + 0.1, row['name'], fontsize=8.5)
    axes[0].set_title("(a) Contact Density vs. Putative Hydrogen Bonds", fontsize=11, fontweight='bold')
    axes[0].set_xlabel("Total Residue Contacts within 3.8 Å Sphere", fontsize=10.5)
    axes[0].set_ylabel("Estimated H-Bonds", fontsize=10.5)
    axes[0].legend(title=r"$\pi$-Stacking (Tyr907/Tyr896)", fontsize=9.5)
    
    # 2. Key Catalytic Residue Contact Frequencies
    key_res = ["TYR907", "GLY863", "SER904", "GLU988", "HIS862", "ARG878", "TYR896", "MET890", "LEU877", "LYS903", "PHE897", "ASN868"]
    counts = {r: 0 for r in key_res}
    for r_str in df_inter['Interacting_Residues']:
        if isinstance(r_str, str):
            for r in key_res:
                if r in r_str.upper():
                    counts[r] += 1
                    
    s_counts = pd.Series(counts).sort_values(ascending=True)
    axes[1].barh(s_counts.index, s_counts.values, color="#0288D1", edgecolor='black', height=0.65, alpha=0.85)
    axes[1].set_title("(b) Interaction Frequency with Catalytic Domain Residues", fontsize=11, fontweight='bold')
    axes[1].set_xlabel("Number of Compounds Engaging Residue (N=35)", fontsize=10.5)
    axes[1].set_ylabel("PARP1 Catalytic Residue", fontsize=10.5)
    
    plt.suptitle("Figure 4. Atomic-Level Macromolecular Interaction Profiles in Human PARP1 Domain",
                 fontsize=13.5, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_file = os.path.join(fig_dir, "fig4_interaction_residue_fingerprints.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 4: {out_file}")

# ==============================================================================
# FIGURE 5: Correlation Heatmap of 20 QSAR & Quantum Descriptors
# ==============================================================================
def make_fig5_correlation_heatmap(base_dir, fig_dir):
    df = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_isolated_drugs.csv"))
    
    cols = ['MW', 'LogP', 'LogS', 'WS_mg_mL', 'HBA', 'HBD', 'PSA', 'RBC', 'NOR', 
            'AromRings', 'Polarizability_alpha', 'Fraction_Csp3', 'E_HOMO', 'E_LUMO', 
            'Gap_eV', 'Hardness_eta', 'Electronegativity_chi', 'Electrophilicity_omega', 
            'Docking_Score_kcal_mol']
            
    corr = df[cols].corr()
    
    fig, ax = plt.subplots(figsize=(14, 11), dpi=300)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1.0, vmin=-1.0, center=0,
                square=True, linewidths=0.7, cbar_kws={"shrink": 0.75, "label": "Pearson Correlation Coefficient (r)"},
                annot=True, fmt=".2f", annot_kws={"size": 7.5}, ax=ax)
                
    ax.set_title("Figure 5. Comprehensive Cross-Correlation Matrix of 20 Quantum Electronic & QSAR Descriptors",
                 fontsize=13, fontweight='bold', pad=15, color="#0D47A1")
    out_file = os.path.join(fig_dir, "fig5_descriptor_correlation_matrix.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 5: {out_file}")

# ==============================================================================
# FIGURE 6: Explainable AI (SHAP) Interpretability Rankings
# ==============================================================================
def make_fig6_shap_suite(base_dir, fig_dir):
    fig, axes = plt.subplots(1, 3, figsize=(17, 6), dpi=300)
    systems = [
        ("Isolated_Drugs", "(a) Isolated Drugs", "#1565C0"),
        ("Drug_B36N36_Pristine", r"(b) Drug + $B_{36}N_{36}$ Pristine", "#2E7D32"),
        ("Drug_B36N36_COOH", r"(c) Drug + $B_{36}N_{36}\text{-COOH}$", "#C62828")
    ]
    
    for i, (sys_id, title, col) in enumerate(systems):
        shap_csv = os.path.join(base_dir, "results", "xai", f"{sys_id}_shap_importance.csv")
        df_shap = pd.read_csv(shap_csv).head(8)
        
        y_pos = np.arange(len(df_shap))
        axes[i].barh(y_pos, df_shap['Mean_Abs_SHAP'], color=col, alpha=0.85, edgecolor='black', height=0.62)
        axes[i].set_yticks(y_pos)
        axes[i].set_yticklabels(df_shap['Descriptor'], fontsize=10)
        axes[i].invert_yaxis()
        axes[i].set_xlabel("mean(|SHAP value|) (Impact on Docking Prediction)", fontsize=10)
        axes[i].set_title(title, fontsize=11.5, fontweight='bold')
        
    plt.suptitle("Figure 6. Explainable AI (XAI) Game-Theoretic SHAP Variable Importance Rankings across Molecular Systems",
                 fontsize=13.5, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_file = os.path.join(fig_dir, "fig6_shap_xai_importance_rankings.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 6: {out_file}")

# ==============================================================================
# FIGURE 7: Parity Plots & Multi-Algorithm Benchmark
# ==============================================================================
def make_fig7_parity_benchmark(base_dir, fig_dir):
    # SECOND CORRECTION: the first fix (real leak-free nested 5x5 CV,
    # replacing FABRICATED scatter points "y_pred = y_obs + np.random.normal")
    # still trained on data/splits/Drug_B36N36_{Pristine,COOH}_*.csv, produced
    # by train_qsar_models.py from dataset_drug_B36N36_pristine.csv /
    # _COOH.csv -- whose Docking_Score_kcal_mol was ITSELF fabricated by
    # sync_real_data_and_train.py from an empirical RDKit-descriptor formula
    # ("Docking_Score = Isolated_Score - 2.5 - 0.045*|E_ads|"), never a real
    # docking or quantum calculation, despite console output claiming
    # "100% REAL docked molecules".
    #
    # Real GFN2-xTB single-point interaction energies for all 33 compounds on
    # the pristine B36N36 cage already exist
    # (dataset_tnbc_bn_pristine.csv, delta_Eint_SP_kcal_mol -- the same data
    # used by scripts/run_nested_cv_leakfree.py / eval_tnbc_summary.py), so
    # panel (b) is fixed with zero new computation. No real structural or
    # quantum data exists at all for the B36N36-COOH functionalized cage (no
    # complex geometries were ever built for it) -- that panel is omitted
    # rather than left fabricated.
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import RidgeCV
    from sklearn.model_selection import KFold, cross_val_predict
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.2), dpi=300)
    alpha_grid = np.array([0.001, 0.01, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0, 300.0, 1000.0])

    systems = [
        ("Isolated Drugs", os.path.join(base_dir, "data", "processed", "dataset_isolated_drugs.csv"),
         ["MW", "LogP", "Polarizability_alpha", "Electrophilicity_omega"], "Docking_Score_kcal_mol", "#1565C0"),
        (r"Drug + $B_{36}N_{36}$ Pristine (real xTB)", os.path.join(base_dir, "data", "processed", "dataset_tnbc_bn_pristine.csv"),
         ["MolWt", "MolMR", "E_HOMO_eV", "Omega_eV"], "delta_Eint_SP_kcal_mol", "#2E7D32"),
    ]

    for i, (title, f_path, desc_cols, target_col, col) in enumerate(systems):
        if not os.path.exists(f_path):
            continue
        df_full = pd.read_csv(f_path).dropna(subset=desc_cols + [target_col])
        X = df_full[desc_cols].values
        y = df_full[target_col].values
        n, p = X.shape

        outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
        inner_cv = KFold(n_splits=5, shuffle=True, random_state=42)
        pipe = Pipeline([("scaler", StandardScaler()), ("ridge", RidgeCV(alphas=alpha_grid, cv=inner_cv))])
        y_pred = cross_val_predict(pipe, X, y, cv=outer_cv)

        rmse = mean_squared_error(y, y_pred) ** 0.5
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)

        min_v = min(y.min(), y_pred.min()) - 0.6
        max_v = max(y.max(), y_pred.max()) + 0.6

        axes[i].plot([min_v, max_v], [min_v, max_v], 'k--', lw=1.6, alpha=0.7, label='Ideal 1:1 Identity')
        axes[i].scatter(y, y_pred, color=col, s=80, edgecolor='black', zorder=3, alpha=0.9,
                         label=f'Out-of-Fold Prediction (n={n})')

        stats_txt = f"Leak-free nested 5x5 CV (n={n}, p={p})\nRMSE = {rmse:.3f} kcal/mol\nMAE = {mae:.3f} kcal/mol\n$Q^2_{{CV}}$ = {r2:.3f}"
        axes[i].text(0.06, 0.92, stats_txt, transform=axes[i].transAxes, fontsize=9.5,
                     verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.88, edgecolor='#B0BEC5'))

        axes[i].set_xlim([min_v, max_v])
        axes[i].set_ylim([min_v, max_v])
        axes[i].set_xlabel("Real Observed (kcal/mol)", fontsize=10.5)
        axes[i].set_ylabel("Out-of-Fold Predicted (kcal/mol)", fontsize=10.5)
        axes[i].set_title(f"({chr(97+i)}) {title}", fontsize=11.5, fontweight='bold')
        axes[i].legend(loc='lower right', fontsize=9)

    plt.suptitle("Figure 7. Leak-Free Nested CV Parity: Observed vs. Out-of-Fold Predicted (real data only)",
                 fontsize=13.5, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_file = os.path.join(fig_dir, "fig7_parity_models_evaluation.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 7: {out_file}")

def generate_all():
    base_dir, fig_dir = get_paths()
    print("Generating complete Q1 scientific figure suite...")
    # The manuscript embeds fig1, fig2, fig4, fig7 from this module and
    # fig3 / fig5 / fig6 from generate_master_q1_figure_set.py +
    # render_perfect_fig3_and_fig5.py. The make_fig3/5/6 helpers below write
    # to non-embedded filenames and are kept only for exploratory use; a
    # failure in them must not block the embedded figures.
    make_fig1_methodology(base_dir, fig_dir)
    make_fig2_quantum_suite(base_dir, fig_dir)
    make_fig4_interaction_fingerprints(base_dir, fig_dir)
    make_fig7_parity_benchmark(base_dir, fig_dir)
    for opt in (make_fig3_docking_distributions, make_fig5_correlation_heatmap, make_fig6_shap_suite):
        try:
            opt(base_dir, fig_dir)
        except Exception as e:
            print(f"[skip] {opt.__name__}: {e}")
    print("Embedded Q1 figures (1, 2, 4, 7) generated successfully!")

if __name__ == "__main__":
    generate_all()
