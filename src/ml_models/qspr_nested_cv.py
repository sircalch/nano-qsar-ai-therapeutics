"""
qspr_nested_cv.py - QSPR surrogates for the two TNBC endpoints
(protocol: qspr_core.py).

  descriptors (fixed before any fit, as in the study design): MolWt, MolMR
      (RDKit, PubChem structure), E_HOMO and omega (GFN2-xTB, relaxed drug)
  endpoint 'vina'  : AutoDock Vina score on PARP1 (PDB 4UND), 30 organic drugs
  endpoint 'dEint' : GFN2-xTB dE_int on B36N36, drugs whose own bonding was
                     unchanged by adsorption

Outputs in results/qspr/: {vina,dEint}_{summary.json, oof.csv, y_scrambling.csv}
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qspr_core  # noqa: E402

BASE = Path(__file__).resolve().parents[2]
FEATURES = ["MolWt", "MolMR", "E_HOMO_eV", "Omega_eV"]


def main():
    m = pd.read_csv(BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv")
    m = m[m.adsorption_mode.isin(["chemisorption", "physisorption"])]
    integ = pd.read_csv(BASE / "data" / "processed" / "adsorption_integrity.csv")[["name", "drug_intact"]]
    m = m.merge(integ, on="name")
    out = BASE / "results" / "qspr"
    s1 = qspr_core.run(m.dropna(subset=["vina_4UND_kcal_mol"]).reset_index(drop=True), FEATURES,
                       "vina_4UND_kcal_mol", out, "vina")
    s2 = qspr_core.run(m[m.drug_intact].reset_index(drop=True), FEATURES, "delta_Eint_SP_kcal_mol", out, "dEint")
    for tag, s in (("vina", s1), ("dEint", s2)):
        print(f"{tag}: n={s['n']} Q2_CV={s['Q2_CV']:.3f} RMSE={s['RMSE']:.2f} "
              f"p_perm={s['Y_scrambling']['p']:.3f} AD {s['AD']['n_inside']}/{s['n']}")


if __name__ == "__main__":
    main()
