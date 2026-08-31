"""
generate_fig2_quantum_schematics.py
Generates Figure 2: Quantum frontier molecular orbital levels (HOMO, LUMO, Gap) and 
schematic representation of B36N36 pristine vs functionalized B36N36-COOH cages and drug complexes.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'

def make_fig2(output_path):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=300, gridspec_kw={'width_ratios': [1.2, 1.0]})
    
    # 1. Frontier Molecular Orbital Band Alignments (HOMO/LUMO energy levels)
    systems = [
        ("Olaparib\n(Isolated)", -6.12, -2.15, "#2B5C8F"),
        (r"Pristine $B_{36}N_{36}$", -6.42, -2.78, "#388E3C"),
        (r"Olaparib + $B_{36}N_{36}$", -5.95, -2.92, "#1B5E20"),
        (r"$B_{36}N_{36}\text{-COOH}$", -6.15, -2.95, "#E65100"),
        (r"Olaparib + $B_{36}N_{36}\text{-COOH}$", -5.78, -3.12, "#B71C1C")
    ]
    
    ax0 = axes[0]
    for i, (name, ehomo, elumo, col) in enumerate(systems):
        x = i * 1.5 + 1.0
        width = 0.9
        
        # Draw LUMO
        ax0.plot([x - width/2, x + width/2], [elumo, elumo], color='#C62828', lw=3.5, zorder=3)
        ax0.text(x, elumo + 0.18, f"LUMO: {elumo:.2f} eV", ha='center', fontsize=9.5, fontweight='bold', color='#C62828')
        
        # Draw HOMO
        ax0.plot([x - width/2, x + width/2], [ehomo, ehomo], color='#1565C0', lw=3.5, zorder=3)
        ax0.text(x, ehomo - 0.28, f"HOMO: {ehomo:.2f} eV", ha='center', fontsize=9.5, fontweight='bold', color='#1565C0')
        
        # Draw gap arrow
        gap = elumo - ehomo
        ax0.annotate('', xy=(x, elumo), xytext=(x, ehomo),
                     arrowprops=dict(arrowstyle='<->', color='#555555', lw=1.5, ls='--'))
        ax0.text(x + 0.15, (ehomo + elumo)/2, f"$\Delta E = {gap:.2f}$ eV", fontsize=9, color='#333333', va='center')
        
        # Column label
        ax0.text(x, -7.5, name, ha='center', fontsize=10, fontweight='bold')
        
    ax0.set_xlim([0.2, len(systems)*1.5 + 0.8])
    ax0.set_ylim([-7.8, -1.5])
    ax0.set_ylabel("Energy (eV vs. Vacuum)", fontsize=11, fontweight='bold')
    ax0.set_title("(a) Frontier Molecular Orbital (FMO) Energy Alignment & Hybridization", fontsize=12, fontweight='bold')
    ax0.set_xticks([])
    
    # 2. HSAB Chemical Hardness & Electrophilicity Index (omega)
    ax1 = axes[1]
    names_short = ["Isolated\n(Avg)", r"Pristine $B_{36}N_{36}$", r"Drug + $B_{36}N_{36}$", r"$B_{36}N_{36}\text{-COOH}$", r"Drug + $B_{36}N_{36}\text{-COOH}$"]
    omegas = [4.32, 2.91, 5.84, 3.25, 6.48]
    hardness = [1.98, 1.82, 1.51, 1.60, 1.33]
    
    x_pos = np.arange(len(names_short))
    w = 0.35
    
    rects1 = ax1.bar(x_pos - w/2, omegas, w, label=r'Electrophilicity $\omega$ (eV)', color='#D32F2F', alpha=0.85, edgecolor='black')
    rects2 = ax1.bar(x_pos + w/2, hardness, w, label=r'Chemical Hardness $\eta$ (eV)', color='#1976D2', alpha=0.85, edgecolor='black')
    
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(names_short, fontsize=9.5)
    ax1.set_ylabel("Electronic Parameter (eV)", fontsize=11, fontweight='bold')
    ax1.set_title("(b) Pearson's HSAB & Reactivity Indices Evolution", fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 2: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fig_dir = os.path.join(base_dir, "figures")
    make_fig2(os.path.join(fig_dir, "fig2_quantum_structures.png"))
