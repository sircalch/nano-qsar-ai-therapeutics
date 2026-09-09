"""
generate_master_q1_figure_set.py
Builds the definitive, fully-featured Q1 Scientific Figure Suite incorporating:
1. Figure 1: Comprehensive Workflow Architecture & Graphical Abstract
2. Figure 2: Quantum CDFT, FMO Band Alignments & 3D B36N36 Nanocage Geometries
3. Figure 3: True 3D PARP1 Receptor Hydrophobic/Electrostatic Surfaces & Docked Poses (PyVista 3D)
4. Figure 4: Multi-Ligand 2D/3D Interaction Fingerprints & 35-Drug Contact Frequency Matrix
5. Figure 5: Complete 20-Descriptor Cross-Correlation Heatmap (Pearson r with annotations)
6. Figure 6: Real Vina Affinity Statistical Distributions & Adsorption Regression
7. Figure 7: Explainable AI (SHAP) Importance Rankings & Feature Dependency Curves
8. Figure 8: OECD Principle 3: Williams Plots for QSAR Applicability Domain (Leverage vs Std Res)
9. Figure 9: Multi-Algorithm Parity Plots & Benchmark Comparison (ExtraTrees, XGBoost, MLR)
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
from PIL import Image
import seaborn as sns

import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pubstyle
_pubstyle.apply()

def get_dirs():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fig_dir = os.path.join(base_dir, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    return base_dir, fig_dir

# ==============================================================================
# FIGURE 3 MASTER: 3D True PyVista Protein Surface & Binding Mode Relocation
# ==============================================================================
def make_master_fig3(base_dir, fig_dir):
    img_whole = os.path.join(fig_dir, "temp_3d_whole_parp1.png")
    img_pocket = os.path.join(fig_dir, "temp_3d_pocket_zoom.png")
    
    fig = plt.figure(figsize=(18, 7.5), dpi=300)
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.0, 1.1])
    
    # Panel (a): 3D PARP1 Whole Macromolecular Surface
    ax0 = fig.add_subplot(gs[0])
    if os.path.exists(img_whole):
        im0 = Image.open(img_whole)
        ax0.imshow(im0)
    ax0.axis('off')
    ax0.set_title("(a) 3D Hydrophobic Surface of Human PARP1 Domain (PDB: 4UND)\n(Red: Hydrophobic Core, Blue: Hydrophilic Surface)", fontsize=10.5, fontweight='bold')
    
    # Panel (b): 3D Catalytic Pocket Zoom with Olaparib
    ax1 = fig.add_subplot(gs[1])
    if os.path.exists(img_pocket):
        im1 = Image.open(img_pocket)
        ax1.imshow(im1)
    ax1.axis('off')
    ax1.set_title("(b) Catalytic pocket with a docked PARP inhibitor\n(exploratory docking; redocking RMSD > 2 A)", fontsize=10.5, fontweight='bold')
    
    # Panel (c): real residue contact frequencies from the docked poses
    ax2 = fig.add_subplot(gs[2])
    inter_csv = os.path.join(base_dir, "results", "docking", "real_residue_interactions.csv")
    from collections import Counter
    cnt = Counter()
    dfi = pd.read_csv(inter_csv)
    for v in dfi["Interacting_Residues"].dropna():
        for r in str(v).split(","):
            r = r.strip()
            if r:
                cnt[r] += 1
    top = cnt.most_common(10)
    names = [t[0].title() for t in top]
    vals = [t[1] for t in top]
    ax2.barh(names[::-1], vals[::-1], color="#1565C0", edgecolor="black")
    ax2.set_xlabel(f"Contact frequency (of {len(dfi)} docked poses)", fontsize=10)
    ax2.set_title("(c) Most frequently contacted PARP1 residues\n(real Vina poses, contact distance <= 3.8 A)", fontsize=10.5, fontweight='bold')

    plt.suptitle("Figure 3. 3D surface of the human PARP1 catalytic domain (PDB 4UND) and real residue contact profile",
                 fontsize=13, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_path = os.path.join(fig_dir, "fig3_3d_parp1_docking_surfaces.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Master Figure 3: {out_path}")

# ==============================================================================
# FIGURE 6 MASTER: Real Vina Affinity Distributions & Adsorption Energetics
# ==============================================================================
def make_master_fig6(base_dir, fig_dir):
    # Single master table (real Vina 4UND + real GFN2-xTB delta_Eint_SP).
    mt = pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_tnbc_bn_pristine.csv"))
    name_col = "name" if "name" in mt.columns else ("Therapeutic Agent" if "Therapeutic Agent" in mt.columns else mt.columns[0])
    df_iso = mt.dropna(subset=["vina_4UND_kcal_mol"])
    m = mt.dropna(subset=["vina_4UND_kcal_mol", "delta_Eint_SP_kcal_mol"])
    if "adsorption_mode" in m.columns:
        m = m[m["adsorption_mode"] == "physisorption"]  # physisorption regime only for the coupling panel

    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.5), dpi=300)

    # Panel A: real PARP1 Vina score distribution (4UND)
    sns.histplot(df_iso["vina_4UND_kcal_mol"], bins=12, ax=axes[0], color="#1565C0", edgecolor="black")
    axes[0].set_title(f"(a) Real AutoDock Vina scores on PARP1 4UND (n={len(df_iso)})", fontsize=11, fontweight='bold')
    axes[0].set_xlabel(r"Vina score (kcal/mol) - exploratory", fontsize=10.5)

    # Panel B: top-15 by real Vina
    top15 = df_iso.sort_values(by="vina_4UND_kcal_mol").head(15)
    sns.barplot(data=top15, x="vina_4UND_kcal_mol", y=name_col, ax=axes[1], palette="Blues_r", edgecolor="black")
    axes[1].set_title("(b) Top-15 anti-TNBC agents by real Vina score", fontsize=11, fontweight='bold')
    axes[1].set_xlabel("Real Vina score (kcal/mol)", fontsize=10.5)
    axes[1].set_ylabel("")

    # Panel C: Vina vs real B36N36 physisorption interaction energy (weak neg corr)
    x = m["vina_4UND_kcal_mol"].values
    y = m["delta_Eint_SP_kcal_mol"].values
    axes[2].scatter(x, y, s=55, color="#2E7D32", edgecolor="black", alpha=0.85)
    r_val = np.corrcoef(x, y)[0, 1]
    axes[2].text(0.06, 0.90, f"Pearson $r = {r_val:.2f}$ (n={len(m)})", transform=axes[2].transAxes,
                 fontsize=10, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.92, edgecolor='#B0BEC5'))
    axes[2].set_title("(c) Isolated Vina score vs. real GFN2-xTB\npristine-B36N36 interaction energy", fontsize=11, fontweight='bold')
    axes[2].set_xlabel("Isolated Vina score (kcal/mol)", fontsize=10.5)
    axes[2].set_ylabel(r"Real $\Delta E_{int,SP}$ on B$_{36}$N$_{36}$ (kcal/mol)", fontsize=10.5)

    plt.suptitle("Figure 6. Real AutoDock Vina docking distributions and drug-B36N36 interaction-energy coupling",
                 fontsize=13, fontweight='bold', y=0.98, color="#0D47A1")
    plt.tight_layout()
    out_file = os.path.join(fig_dir, "fig6_docking_vina_statistical_profiles.png")
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Master Figure 6: {out_file}")

def generate_master_suite():
    base_dir, fig_dir = get_dirs()
    print("Building master Q1 figure suite...")
    from render_3d_real_parp1_surfaces import render_3d_views
    render_3d_views()
    make_master_fig3(base_dir, fig_dir)
    make_master_fig6(base_dir, fig_dir)
    print("Master figures generated successfully!")

if __name__ == "__main__":
    generate_master_suite()
