"""
make_figures.py - every figure of the TNBC / B36N36 manuscript, drawn from the
pipeline outputs at Springer print size (see style.py).

usage: python src/figures/make_figures.py [fig ...]      (default: all)
writes figures/FigN.{pdf,png,tif}; 3D renders are cached in figures/_renders
"""
import json
import sys
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import figkit as K  # noqa: E402
import render3d as R  # noqa: E402
import style as S  # noqa: E402

BASE = HERE.parents[1]
FIG = BASE / "figures"
REN = FIG / "_renders"
POSES = BASE / "results" / "docking" / "real_poses"
CALC = BASE / "calculations"

FAMILY = {"PARP inhibitor": S.GROUPS[0], "Cytotoxic agent": S.GROUPS[1],
          "Kinase / pathway inhibitor": S.GROUPS[2]}
CYTO = {"Taxane", "Microtubule Inhibitor", "Anthracycline", "Topoisomerase I Inhibitor",
        "Topoisomerase II Inhibitor", "Platinum Agent"}


def family(cls):
    return "PARP inhibitor" if cls == "PARP Inhibitor" else "Cytotoxic agent" if cls in CYTO \
        else "Kinase / pathway inhibitor"


def data():
    m = pd.read_csv(BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv")
    m = m[m.adsorption_mode.isin(["chemisorption", "physisorption"])].copy()
    integ = pd.read_csv(BASE / "data" / "processed" / "adsorption_integrity.csv")
    m = m.merge(integ, on="name", how="left")
    m["family"] = m.drug_class.map(family)
    m["color"] = m.family.map(FAMILY)
    d = {"m": m}
    d["redock"] = pd.read_csv(BASE / "data" / "processed" / "redocking_validation.csv")
    d["contacts"] = pd.read_csv(BASE / "results" / "docking" / "residue_contacts.csv")
    d["cage"] = json.loads((CALC / "tnbc" / "B36N36_energy.json").read_text())
    q = BASE / "results" / "qspr"
    for tag in ("vina", "dEint"):
        d[f"q_{tag}"] = json.loads((q / f"{tag}_summary.json").read_text())
        d[f"oof_{tag}"] = pd.read_csv(q / f"{tag}_oof.csv")
        d[f"perm_{tag}"] = pd.read_csv(q / f"{tag}_y_scrambling.csv")
    return d


def render(name, fn, *a, **kw):
    REN.mkdir(parents=True, exist_ok=True)
    png, meta = REN / f"{name}.png", REN / f"{name}.json"
    if not png.exists():
        out = fn(*a, out_png=str(png), **kw)
        meta.write_text(json.dumps(out if isinstance(out, dict) else {}))
        S.autocrop(png)
    return png, json.loads(meta.read_text()) if meta.exists() else {}


def family_legend(fig, y=0.0):
    K.legend_row(fig, [("dot", c, f) for f, c in FAMILY.items()], y=y, fontsize=6.2)


def complex_path(name):
    return CALC / "tnbc_recompute" / name.replace(" ", "_").replace("-", "_") / "complex_opt.xyz"


# ------------------------------------------------------------------ Fig. 1
def pocket_render():
    x, s = REN / "redock_xtal.pdb", REN / "redock_smiles.pdb"
    REN.mkdir(parents=True, exist_ok=True)
    R.first_model_pdb(str(POSES / "2YQ_redock_out.pdbqt"), str(x))
    R.first_model_pdb(str(POSES / "2YQ_smiles_out.pdbqt"), str(s))
    return render("parp1_pocket", R.pocket_closeup, str(BASE / "data" / "raw" / "4UND.pdb"),
                  [{"sel": "resn 2YQ", "color": (0.70, 0.72, 0.75), "radius": 0.30, "name": "xtal"},
                   {"path": str(x), "color": (0.91, 0.55, 0.16), "radius": 0.16, "name": "rdx"},
                   {"path": str(s), "color": (0.20, 0.62, 0.60), "radius": 0.16, "name": "rds"}],
                  size=(1600, 1300), slab=24, zoom=2.5)


def fig1(d):
    """Workflow."""
    m = d["m"]
    cage, _ = render("cage", R.molecule, str(CALC / "tnbc" / "B36N36_optimized.xyz"), tilt=15,
                     size=(1100, 1100), orient_on_carrier=False)
    pocket, _ = pocket_render()
    olap, _ = render("olaparib_complex_side", R.molecule, str(complex_path("Olaparib")), tilt=0, size=(1300, 1100),
                     orient_on_carrier=False, buffer=1.0)          # principal axis = cage-drug axis: contact visible
    mol2d = REN / "olaparib_2d.png"
    if not mol2d.exists():
        from rdkit import Chem
        from rdkit.Chem import Draw
        Draw.MolToFile(Chem.MolFromSmiles(m.set_index("name").loc["Olaparib", "smiles"]), str(mol2d),
                       size=(700, 480))
        S.autocrop(mol2d)
    mini = REN / "qspr_mini.png"
    o = d["oof_vina"]
    fm, am = plt.subplots(figsize=(1.2, 1.2))
    lo, hi = min(o.iloc[:, 5].min(), o.oof_pred.min()), max(o.iloc[:, 5].max(), o.oof_pred.max())
    am.plot([lo, hi], [lo, hi], color=S.MUTED, lw=0.8, ls=(0, (3, 2)))
    am.scatter(o[d["q_vina"]["target"]], o.oof_pred, s=9, color=S.DOCK, edgecolor="white", lw=0.3)
    am.set_xticks([]); am.set_yticks([]); am.set_xlabel("observed", fontsize=6); am.set_ylabel("predicted", fontsize=6)
    fm.savefig(mini, dpi=400, bbox_inches="tight"); plt.close(fm)
    rd = d["redock"].set_index("control")
    nchem = int((m.adsorption_mode == "chemisorption").sum())
    stages = [
        ("Drug set", [f"{len(m)} anti-TNBC drugs", "3 families", "from PubChem"]),
        ("PARP1 docking", ["PDB 4UND", "Vina 1.2.7",
                           f"redock {rd.rmsd_heavy_atom_A.min():.1f}–{rd.rmsd_heavy_atom_A.max():.1f} Å"]),
        ("B$_{36}$N$_{36}$ cage", ["BN fullerene", "108 B–N bonds", "GFN2-xTB"]),
        ("Adsorption", ["4 poses per drug", "Δ$E_{int}$, Δ$E_{ads}$", "bond check"]),
        ("QSPR", ["4 descriptors, ridge", "nested 5×5 CV", "Y-scrambling, AD"]),
    ]
    fig = plt.figure(figsize=(S.DOUBLE, 58 * S.MM))
    K.workflow(fig, stages, ("Outcome", [f"{len(m) - nchem} physisorbed", f"{nchem} chemisorbed",
                                         f"Vina $Q^2_{{CV}}$ = {d['q_vina']['Q2_CV']:.2f}",
                                         f"Δ$E_{{int}}$ $Q^2_{{CV}}$ = {d['q_dEint']['Q2_CV']:.2f}"]),
               images={0: mol2d, 1: pocket, 2: cage, 3: olap, 4: mini}, accent=S.DOCK)
    S.save(fig, FIG, "Fig1")


# ------------------------------------------------------------------ Fig. 2
def fig2(d):
    """Frontier orbitals of the drugs against the cage, and eta vs omega."""
    m = d["m"].sort_values("Gap_eV").reset_index(drop=True)
    cage = d["cage"]
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 74 * S.MM),
                            gridspec_kw=dict(width_ratios=[1.7, 1], wspace=0.32))
    fig.subplots_adjust(top=0.86)
    ax = axs[0]
    x = np.arange(len(m))
    ax.vlines(x, m.E_HOMO_eV, m.E_LUMO_eV, color=m.color, lw=2.2, alpha=0.9)
    ax.scatter(x, m.E_HOMO_eV, s=7, color=m.color, zorder=3)
    ax.scatter(x, m.E_LUMO_eV, s=7, color=m.color, zorder=3, marker="s")
    homo_c, lumo_c = cage.get("HOMO_eV"), cage.get("LUMO_eV")
    if homo_c is not None:
        ax.axhspan(homo_c, lumo_c, color=S.PANEL_BG, zorder=0)
        ax.axhline(homo_c, color=S.MUTED, lw=0.7, ls=(0, (4, 2)))
        ax.axhline(lumo_c, color=S.MUTED, lw=0.7, ls=(0, (4, 2)))
        ax.text(len(m) - 0.3, lumo_c, " cage" + chr(10) + " LUMO", ha="left", va="center", fontsize=6, color=S.MUTED, clip_on=False)
        ax.text(len(m) - 0.3, homo_c, " cage" + chr(10) + " HOMO", ha="left", va="center", fontsize=6, color=S.MUTED, clip_on=False)
        ax.set_xlim(-0.7, len(m) - 0.3)
    ax.set_xticks(x)
    ax.set_xticklabels(m.name, rotation=90, fontsize=5.4)
    ax.set_ylabel("Orbital energy (eV)")
    ax.tick_params(axis="x", length=0)
    K.light_grid(ax, "y")
    S.panel(ax, "a", x=-0.07)
    ax = axs[1]
    ax.scatter(m.Eta_eV, m.Omega_eV, c=m.color, s=20, edgecolor="white", lw=0.4, zorder=3)
    ext = pd.concat([m.nlargest(2, "Omega_eV"), m.nsmallest(2, "Eta_eV"), m.nlargest(1, "Eta_eV")]).drop_duplicates("name")
    K.label_points(ax, ext.Eta_eV.values, ext.Omega_eV.values, ext.name.values, fontsize=5.6)
    ax.set_xlabel("Chemical hardness η (eV)")
    ax.set_ylabel("Electrophilicity ω (eV)")
    K.light_grid(ax)
    S.panel(ax, "b", x=-0.22)
    family_legend(fig, y=0.97)
    S.save(fig, FIG, "Fig2")


# ------------------------------------------------------------------ Fig. 3
def fig3(d):
    """PARP1 docking validation and pocket contacts."""
    png, meta = pocket_render()
    rd = d["redock"].set_index("control")
    ct = d["contacts"]
    n = ct.name.nunique()
    freq = ct.groupby("residue").name.nunique().sort_values(ascending=False).head(14)
    polar = ct[ct.polar].groupby("residue").name.nunique().reindex(freq.index).fillna(0)
    fig = plt.figure(figsize=(S.DOUBLE, 78 * S.MM))
    gs = GridSpec(1, 2, width_ratios=[1.35, 1], wspace=0.28, left=0.01, right=0.99, top=0.95, bottom=0.14)
    ax = fig.add_subplot(gs[0])
    ax.imshow(mpimg.imread(png))
    ax.set_axis_off()
    S.panel(ax, "a", x=0.02, y=0.97)
    K.legend_row(fig, [("line", "#b3b8bf", "crystal talazoparib (PDB 4UND)"),
                       ("line", "#e88c29", f"redock, crystal conf. ({rd.loc['self-redock, crystal conformation', 'rmsd_heavy_atom_A']:.2f} Å)"),
                       ("line", "#339e99", f"production protocol ({rd.loc['production protocol, from SMILES', 'rmsd_heavy_atom_A']:.2f} Å)")],
                   y=0.0, fontsize=6)
    ax2 = fig.add_subplot(gs[1])
    y = np.arange(len(freq))[::-1]
    ax2.barh(y, freq.values / n * 100, color=S.DOCK, alpha=0.25, height=0.7, label="any contact")
    ax2.barh(y, polar.values / n * 100, color=S.DOCK, height=0.7, label="polar contact")
    ax2.set_yticks(y)
    ax2.set_yticklabels(freq.index, fontsize=6.2)
    ax2.set_xlabel(f"Drugs in contact (% of {n})")
    ax2.set_xlim(0, 100)
    ax2.tick_params(axis="y", length=0)
    K.light_grid(ax2, "x")
    ax2.legend(loc="lower right", frameon=False)
    S.panel(ax2, "b", x=-0.22)
    S.save(fig, FIG, "Fig3")


# ------------------------------------------------------------------ Fig. 4
def fig4(d):
    """Docking scores by drug, and docking vs adsorption."""
    m = d["m"]
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 92 * S.MM),
                            gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.35))
    K.ranked_dots(axs[0], m.name.values, m.vina_4UND_kcal_mol.values, m.color.values,
                  "Vina score (kcal mol$^{-1}$)", highlight={"Olaparib", "Talazoparib"})
    S.panel(axs[0], "a", x=-0.38)
    ax = axs[1]
    chem = m.adsorption_mode == "chemisorption"
    ax.scatter(m.vina_4UND_kcal_mol[~chem], -m.delta_Eint_SP_kcal_mol[~chem], c=m.color[~chem], s=22,
               edgecolor="white", lw=0.4, zorder=3)
    ax.scatter(m.vina_4UND_kcal_mol[chem], -m.delta_Eint_SP_kcal_mol[chem], facecolor="white",
               edgecolor=m.color[chem], s=22, lw=1.1, zorder=3)
    from scipy.stats import spearmanr
    rho, p = spearmanr(m.vina_4UND_kcal_mol, m.delta_Eint_SP_kcal_mol)
    K.stat_box(ax, [f"Spearman ρ = {rho:.2f} (p = {p:.2f})", "open: chemisorbed"], loc="upper right")
    ax.set_yscale("log")
    K.log_ticks(ax)
    ax.set_xlabel("Vina score, PARP1 (kcal mol$^{-1}$)")
    ax.set_ylabel("−Δ$E_{int}$, B$_{36}$N$_{36}$ (kcal mol$^{-1}$)")
    K.light_grid(ax)
    S.panel(ax, "b", x=-0.2)
    fig.subplots_adjust(bottom=0.16)
    family_legend(fig, y=0.0)
    S.save(fig, FIG, "Fig4")


# ------------------------------------------------------------------ Fig. 5
def fig5(d):
    """Cage and representative complexes."""
    m = d["m"]
    intact = m[m.drug_intact == True]  # noqa: E712
    phys = intact[intact.adsorption_mode == "physisorption"].nsmallest(1, "delta_Eint_SP_kcal_mol").name.iloc[0]
    chem = intact[intact.adsorption_mode == "chemisorption"].nsmallest(1, "delta_Eint_SP_kcal_mol").name.iloc[0]
    cage, _ = render("cage", R.molecule, str(CALC / "tnbc" / "B36N36_optimized.xyz"), tilt=15,
                     size=(1100, 1100), orient_on_carrier=False)
    items = [(cage, "B$_{36}$N$_{36}$ (GP(1,1), 108 B–N)", f"HOMO–LUMO gap {d['cage']['HOMO_LUMO_gap_eV']:.2f} eV")]
    for nm in ("Olaparib", phys, chem):
        png, _ = render(f"cplx_{nm}_side", R.molecule, str(complex_path(nm)), tilt=0, size=(1300, 1100),
                        orient_on_carrier=False, buffer=1.0)      # principal axis = cage-drug axis
        r = m.set_index("name").loc[nm]
        items.append((png, f"{nm} ({r.adsorption_mode})", f"Δ$E_{{int}}$ = {r.delta_Eint_SP_kcal_mol:.1f} kcal mol$^{{-1}}$"))
    items = items[:1] + [it for i, it in enumerate(items[1:]) if it[1] not in [x[1] for x in items[1:i + 1]]]
    fig, axs = plt.subplots(1, len(items), figsize=(S.DOUBLE, 60 * S.MM), gridspec_kw=dict(wspace=0.05))
    for ax, (png, t, sub), l in zip(axs, items, "abcd"):
        K.render_panel(ax, png, title=t, sub=sub)
        S.panel(ax, l, x=0.02, y=1.02)
    S.save(fig, FIG, "Fig5")


# ------------------------------------------------------------------ Fig. 6
def fig6(d):
    """Adsorption landscape and energies by family."""
    m = d["m"]
    fig, axs = plt.subplots(1, 2, figsize=(S.DOUBLE, 72 * S.MM),
                            gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.3))
    chem = (m.adsorption_mode == "chemisorption").values
    K.landscape(axs[0], m.min_contact_A.values, m.delta_Eint_SP_kcal_mol.values, chem, names=m.name.values,
                max_labels=6)
    bad = m[m.drug_intact == False]  # noqa: E712
    if len(bad):
        axs[0].scatter(bad.min_contact_A, -bad.delta_Eint_SP_kcal_mol, marker="x", color=S.INK, s=18, lw=0.8,
                       zorder=5)
    S.panel(axs[0], "a", x=-0.14)
    fams = list(FAMILY)
    K.group_strip(axs[1], m.family.values, -m.delta_Eint_SP_kcal_mol.values, [FAMILY[f] for f in fams],
                  "−Δ$E_{int}$ (kcal mol$^{-1}$)", order=fams)
    axs[1].set_yscale("log")
    K.log_ticks(axs[1])
    axs[1].set_xticklabels(["PARP", "Cytotoxic", "Kinase /\npathway"])
    S.panel(axs[1], "b", x=-0.22)
    S.save(fig, FIG, "Fig6")


# ------------------------------------------------------------------ Fig. 7
def fig7(d):
    """QSPR for both endpoints."""
    fig, axs = plt.subplots(2, 3, figsize=(S.DOUBLE, 108 * S.MM),
                            gridspec_kw=dict(wspace=0.5, hspace=0.55, width_ratios=[1, 1, 0.9]))
    for row, (tag, col, name, xl) in enumerate((("vina", S.DOCK, "Vina score", "Vina score"),
                                                ("dEint", S.ADS, "Δ$E_{int}$", "GFN2-xTB Δ$E_{int}$"))):
        q, oof, perm = d[f"q_{tag}"], d[f"oof_{tag}"], d[f"perm_{tag}"]
        target = q["target"]
        K.parity(axs[row, 0], oof[target].values, oof.oof_pred.values, col,
                 stats_lines=[f"{name}", f"$n$ = {q['n']}, $Q^2_{{CV}}$ = {q['Q2_CV']:.2f}",
                              f"RMSE = {q['RMSE']:.1f}"], names=oof.name.values, label_extremes=2, xlabel=xl)
        K.williams(axs[row, 1], oof.leverage.values, oof.std_residual.values, q["AD"]["h_star"], col,
                   names=oof.name.values)
        K.scrambling(axs[row, 2], perm.Q2_perm.values, q["Q2_CV"], col)
    fig.canvas.draw()
    for row, letters in ((0, "abc"), (1, "def")):
        top = max(ax.get_position().y1 for ax in axs[row])
        for ax, l in zip(axs[row], letters):
            fig.text(ax.get_position().x0 - 0.03, top + 0.03, l, fontsize=9, fontweight="bold", va="bottom")
    S.save(fig, FIG, "Fig7")


FIGS = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6, "7": fig7}

if __name__ == "__main__":
    S.apply()
    d = data()
    for key in (sys.argv[1:] or FIGS):
        FIGS[key](d)
        print(f"Fig{key} done")
