"""
build_si.py - Supporting Information (Word) for the TNBC / B36N36 study,
generated from the pipeline outputs.

writes manuscript/submission/Supporting_Information_TNBC_B36N36.docx
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docx_kit as k  # noqa: E402
from build_manuscript import AFFIL, AUTHOR, EMAIL, TITLE, load  # noqa: E402

BASE = HERE.parents[1]
OUT = BASE / "manuscript" / "submission"


def num(x, nd=2):
    return "–" if pd.isna(x) else f"{x:.{nd}f}".replace("-", "−")


def main():
    d = load()
    doc = k.new_document()
    k.si_header(doc, TITLE, "Journal of Molecular Modeling", AUTHOR, AFFIL, EMAIL)

    a = d["audit"]
    rows = [[r.name, str(r.pubchem_cid), r.pubchem_formula,
             "yes" if r.old_matched_pubchem else "**corrected**"] for r in a.itertuples()]
    k.table(doc, ("S1", "Compound identity. Every structure was taken from PubChem by name and checked by "
                        "InChIKey; the last column states whether the structure used in an earlier version "
                        "of this dataset already matched PubChem."),
            ["Compound", "PubChem CID", "Formula", "Earlier structure correct"], rows, align="lllc", font=8)

    rd = d["redock"].reset_index()
    rows = [[r.control, num(r.affinity_kcal_mol), num(r.rmsd_heavy_atom_A), r.docking_status.split(" ")[0]]
            for r in rd.itertuples()]
    k.table(doc, ("S2", "Redocking controls for talazoparib (ligand 2YQ) in PARP1 chain A (PDB 4UND). RMSD: "
                        "symmetry-corrected heavy-atom RMSD to the crystal pose, no re-alignment."),
            ["Control", "Vina (kcal mol^{−1})", "RMSD (Å)", "Status"], rows, align="lccc")

    m = d["m"].sort_values("delta_Eint_SP_kcal_mol")
    rows = [[r.name, r.family, num(r.vina_4UND_kcal_mol), num(r.delta_Eint_SP_kcal_mol, 1),
             num(r.delta_Eads_kcal_mol, 1), num(r.min_contact_A), r.adsorption_mode,
             "yes" if r.drug_intact else "no"] for r in m.itertuples()]
    k.table(doc, ("S3", "Per-drug results. Vina score on PARP1 (PDB 4UND); GFN2-xTB interaction and adsorption "
                        "energies on B_{36}N_{36} (kcal mol^{−1}); closest drug–cage heavy-atom contact (Å); "
                        "adsorption regime; whether the drug kept its own bonding in the complex."),
            ["Drug", "Family", "Vina", "Δ*E*_{int}", "Δ*E*_{ads}", "Contact", "Regime", "Intact"],
            rows, align="llcccclc", font=7.5)

    rows = []
    for tag, label in (("vina", "Vina score, PARP1"), ("dEint", "Δ*E*_{int}, B_{36}N_{36}")):
        q = d[f"q_{tag}"]
        rows.append([label, str(q["n"]), num(q["Q2_CV"]), num(q["RMSE"]), num(q["MAE"]),
                     num(q["Y_scrambling"]["mean_Q2"]), f"{q['Y_scrambling']['p']:.3f}",
                     f"{q['AD']['n_inside']}/{q['n']}", f"{q['alpha_final']:.3g}"])
    k.table(doc, ("S4", "QSPR models (ridge; descriptors MolWt, MolMR, *E*_{HOMO}, ω). Nested 5×5 "
                        "cross-validation; Y-scrambling with 1,000 permutations through the same nested "
                        "procedure; applicability domain by leverage (*h*^{*} = 3(*p*+1)/*n*) and ±3 "
                        "standardised residuals."),
            ["Endpoint", "*n*", "*Q*^{2}_{CV}", "RMSE", "MAE", "*Q*^{2} perm. (mean)", "*p*", "Inside AD",
             "Ridge α"], rows, align="lcccccccc", font=8)
    for tag in ("vina", "dEint"):
        q = d[f"q_{tag}"]
        k.para(doc, f"Standardised ridge coefficients ({tag}): " +
               ", ".join(f"{f} {v:+.3f}" for f, v in q["coef_std"].items()) +
               f". Per-fold *Q*^{{2}}: " + ", ".join(f"{x:.2f}" for x in q["Q2_folds"]) + ".", size=10)
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "Supporting_Information_TNBC_B36N36.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
