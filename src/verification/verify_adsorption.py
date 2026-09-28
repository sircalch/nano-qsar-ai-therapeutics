"""
verify_adsorption.py - independent re-check of every TNBC / B36N36 adsorption result.

Does not import the pipeline. For each drug it
  1. checks the SHA-256 of the stored final pose against result.json;
  2. re-runs the GFN2-xTB single points of the complex, the carrier and drug frozen at
     the complex geometry, and the relaxed isolated drug, and compares them;
  3. recomputes dE_int and dE_ads (cage reference from calculations/tnbc/B36N36_energy.json);
  4. recomputes drug-cage bonds, drug integrity and closest heavy-atom contact;
  5. checks the cage in the complex: 108 B-N bonds, no B-B / N-N, energy not below the
     relaxed cage;
  6. compares with data/processed/dataset_tnbc_bn_pristine.csv and adsorption_integrity.csv,
     the tables the manuscript reads.
writes results/verification/adsorption_check.csv and prints a summary.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
WORK = BASE / "calculations" / "tnbc_recompute"
XTB = os.environ.get("XTB_EXE", "C:/Users/Andre/mm/xtb/Library/bin/xtb.exe")
HARTREE = 627.509
COV = {"H": 0.31, "B": 0.84, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "P": 1.07, "S": 1.05,
       "Cl": 1.02, "Br": 1.20, "I": 1.39}


def read_xyz(f):
    L = Path(f).read_text().splitlines()
    n = int(L[0].split()[0])
    return [x.split()[0] for x in L[2:2 + n]], np.array([[float(v) for v in x.split()[1:4]] for x in L[2:2 + n]])


def sp(xyz_file, chrg):
    env = dict(os.environ, OMP_NUM_THREADS="2", XTBPATH=str(Path(XTB).parent.parent / "share" / "xtb"))
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / "m.xyz").write_text(Path(xyz_file).read_text())
        out = subprocess.run([XTB, "m.xyz", "--sp", "--gfn", "2", "--chrg", str(chrg), "--uhf", "0"], cwd=td, env=env,
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800).stdout
    m = re.findall(r"TOTAL ENERGY\s+(-?\d+\.\d+)", out)
    return float(m[-1]) if m else float("nan")


def bonded(el, xyz, i, j):
    return np.linalg.norm(xyz[i] - xyz[j]) < 1.15 * (COV[el[i]] + COV[el[j]])


def check(d):
    r = json.loads((d / "result.json").read_text())
    if r.get("status") != "OK":
        return {"name": r["name"], "status": r.get("status")}
    q = r["formal_charge"]
    sha = hashlib.sha256((d / "complex_opt.xyz").read_bytes()).hexdigest()
    el, xyz = read_xyz(d / "complex_opt.xyz")
    nd = r["n_drug"]
    D, C = list(range(nd)), list(range(nd, len(el)))
    ec, ecf, edf, ed = sp(d / "complex_opt.xyz", q), sp(d / "frag_carrier.xyz", 0), sp(d / "frag_drug.xyz", q), sp(d / "drug_opt.xyz", q)
    e_cage = json.loads((BASE / "calculations" / "tnbc" / "B36N36_energy.json").read_text())["E_Eh"]
    hd, hc = [i for i in D if el[i] != "H"], [i for i in C if el[i] != "H"]
    dmin = min(np.linalg.norm(xyz[i] - xyz[j]) for i in hd for j in hc)
    cross = [(i, j) for i in D for j in C if bonded(el, xyz, i, j)]
    del0, x0 = read_xyz(d / "drug_opt.xyz")
    b0 = {(i, j) for i, j in combinations(range(nd), 2) if bonded(del0, x0, i, j)}
    b1 = {(i, j) for i, j in combinations(D, 2) if bonded(el, xyz, i, j)}
    cage_pairs = [(i, j) for i, j in combinations(C, 2) if bonded(el, xyz, i, j)]
    nbn = sum({el[i], el[j]} == {"B", "N"} for i, j in cage_pairs)
    nhomo = [(i, j) for i, j in cage_pairs if el[i] == el[j]]
    # B...B / N...N across a four-membered ring share two neighbours of the other element: not bonds
    nb = {i: {j for a, b in cage_pairs for j in ((b,) if a == i else (a,) if b == i else ())} for i in C}
    true_homo = [(i, j) for i, j in nhomo if len({k for k in nb[i] & nb[j] if el[k] != el[i]}) < 2]
    return {"name": r["name"], "status": "OK", "sha_ok": sha == r["sha256"],
            "dE_int_json": r["delta_Eint_SP_kcal_mol"], "dE_int_recomputed": round((ec - ecf - edf) * HARTREE, 3),
            "dE_ads_json": r["delta_Eads_kcal_mol"], "dE_ads_recomputed": round((ec - e_cage - ed) * HARTREE, 3),
            "max_E_diff_Eh": max(abs(ec - r["E_complex_Eh"]), abs(ecf - r["E_carrier_frozen_Eh"]),
                                 abs(edf - r["E_drug_frozen_Eh"]), abs(ed - r["E_drug_Eh"])),
            "dmin_recomputed": round(dmin, 3), "dmin_json": r["min_contact_A"],
            "chem_recomputed": bool(cross), "intact_recomputed": b0 == b1,
            "cage_BN": nbn, "cage_true_homo_bonds": len(true_homo),
            "cage_dE_kcal": round((ecf - e_cage) * HARTREE, 2)}


def main(workers=4):
    dirs = sorted(d for d in WORK.iterdir() if (d / "result.json").exists())
    with ProcessPoolExecutor(workers) as ex:
        df = pd.DataFrame(list(ex.map(check, dirs)))
    tab = pd.read_csv(BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv")
    integ = pd.read_csv(BASE / "data" / "processed" / "adsorption_integrity.csv")
    m = df.merge(tab[["name", "delta_Eint_SP_kcal_mol", "delta_Eads_kcal_mol", "min_contact_A", "adsorption_mode"]],
                 on="name", how="left").merge(integ[["name", "drug_intact"]], on="name", how="left")
    out = BASE / "results" / "verification"
    out.mkdir(parents=True, exist_ok=True)
    m.to_csv(out / "adsorption_check.csv", index=False)
    ok = m[m.status == "OK"]
    print(f"complexes: {len(ok)} | pose files unchanged (SHA-256): {ok.sha_ok.sum()}")
    print(f"max |E diff| over the 4 single points: {ok.max_E_diff_Eh.max():.2e} Eh")
    print(f"max |dE_int recomputed - json|: {np.abs(ok.dE_int_recomputed - ok.dE_int_json).max():.4f}; "
          f"dE_ads: {np.abs(ok.dE_ads_recomputed - ok.dE_ads_json).max():.4f} kcal/mol")
    print(f"table dE_int = recomputed: {np.isclose(ok.delta_Eint_SP_kcal_mol, ok.dE_int_recomputed, atol=0.01).sum()}; "
          f"dE_ads: {np.isclose(ok.delta_Eads_kcal_mol, ok.dE_ads_recomputed, atol=0.01).sum()}")
    print(f"regime (table vs recomputed): {(ok.adsorption_mode.eq('chemisorption') == ok.chem_recomputed).sum()}; "
          f"integrity: {(ok.drug_intact.astype(bool) == ok.intact_recomputed).sum()}; "
          f"d_min: {(np.abs(ok.dmin_recomputed - ok.min_contact_A) < 0.01).sum()}")
    print(f"cage: 108 B-N in {(ok.cage_BN == 108).sum()} complexes; true B-B/N-N bonds: {ok.cage_true_homo_bonds.sum()}; "
          f"cage energy vs relaxed: {ok.cage_dE_kcal.min():.2f} to {ok.cage_dE_kcal.max():.2f} kcal/mol")


if __name__ == "__main__":
    main(int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4)
