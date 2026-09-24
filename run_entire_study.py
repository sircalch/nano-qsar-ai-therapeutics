"""
run_entire_study.py
Reproduces every number, table and figure of the TNBC / B36N36 article from the
raw inputs (PubChem structures, PDB 4UND).

Steps (each resumable; the quantum and docking steps take hours on a desktop):
  1. compound identities from PubChem (InChIKey check)
  2. valid B36N36 cage: build, relax, confirm minimum
  3. GFN2-xTB adsorption of the 30 organic drugs (+ isolated-drug descriptors)
  4. docking: receptor preparation, two redocking controls, 30 drugs
  5. dataset assembly, complex-integrity check and adsorption regime
  6. residue contacts, QSPR, figures, manuscript, supporting information
"""
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
PY = sys.executable
NAMES = "data/processed/docked_drugs.csv"

STEPS = [
    ("Compound identities (PubChem)", ["src/descriptors/fix_structures_from_pubchem.py"]),
    ("B36N36 cage", ["src/quantum/build_b36n36_cage.py"]),
    ("GFN2-xTB adsorption", ["recompute_tnbc_adsorption.py"]),
    ("AutoDock Vina docking (PDB 4UND)", ["src/docking/run_vina_docking.py"]),
    ("Dataset assembly", ["recompute_tnbc_adsorption.py", "--commit-datasets"]),
    ("Complex integrity and regime", ["src/quantum/integrity_check.py"]),
    ("Residue contacts", ["src/docking/contacts.py", "data/raw/4UND_A_H.pdb", "results/docking/real_poses",
                          NAMES, "results/docking/residue_contacts.csv"]),
    ("QSPR", ["src/ml_models/qspr_nested_cv.py"]),
    ("Figures", ["src/figures/make_figures.py"]),
    ("Manuscript", ["src/manuscript/build_manuscript.py"]),
    ("Supporting information", ["src/manuscript/build_si.py"]),
]


def main():
    for i, (title, cmd) in enumerate(STEPS, 1):
        print(f"\n{'=' * 70}\n  [{i}/{len(STEPS)}] {title}\n{'=' * 70}", flush=True)
        if cmd[0].endswith("contacts.py"):
            import pandas as pd
            d = pd.read_csv(BASE / "data/processed/dataset_tnbc_bn_pristine.csv")
            d[d.vina_4UND_kcal_mol.notna()][["name"]].to_csv(BASE / NAMES, index=False)
        t0 = time.time()
        if subprocess.run([PY, *cmd], cwd=BASE).returncode:
            sys.exit(f"step failed: {title}")
        print(f"  done in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
