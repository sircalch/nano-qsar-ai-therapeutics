"""
integrity_check.py - did adsorption change the drug's own bonding?

For every relaxed drug/B36N36 complex, the drug's internal bond graph (1.15 x
sum of covalent radii) is compared with that of the separately relaxed drug:
bonds broken or formed inside the drug flag proton transfer, tautomerisation
or decomposition, which makes dE_int a reaction energy rather than an
adsorption energy. Carrier-drug bonds (chemisorption) are reported separately.

writes data/processed/adsorption_integrity.csv
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[2]
WORK = BASE / "calculations" / "tnbc_recompute"
COV = {"H": 0.31, "B": 0.84, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "P": 1.07, "S": 1.05,
       "Cl": 1.02, "Br": 1.20, "I": 1.39}


def read_xyz(p):
    L = Path(p).read_text().splitlines()
    n = int(L[0])
    return ([l.split()[0] for l in L[2:2 + n]],
            np.array([[float(v) for v in l.split()[1:4]] for l in L[2:2 + n]]))


def bonds(el, X, idx_a, idx_b=None, scale=1.15):
    out = set()
    idx_b = idx_a if idx_b is None else idx_b
    for i in idx_a:
        for j in idx_b:
            if (idx_b is idx_a and j <= i) or i == j:
                continue
            if np.linalg.norm(X[i] - X[j]) < scale * (COV[el[i]] + COV[el[j]]):
                out.add((min(i, j), max(i, j)))
    return out


def main():
    rows = []
    for res in sorted(WORK.glob("*/result.json")):
        r = json.loads(res.read_text())
        if r.get("status") != "OK":
            continue
        wd = res.parent
        de, Xd = read_xyz(wd / "drug_opt.xyz")
        ec, Xc = read_xyz(wd / "complex_opt.xyz")
        nd = len(de)
        drug = list(range(nd))
        cage = list(range(nd, len(ec)))
        before, after = bonds(de, Xd, drug), bonds(ec, Xc, drug)
        inter = bonds(ec, Xc, drug, cage)
        fmt = lambda s, el: ";".join(sorted(f"{el[i]}{i}-{el[j]}{j}" for i, j in s))
        rows.append({"name": r["name"], "drug_intact": before == after,
                     "drug_bonds_broken": fmt(before - after, de), "drug_bonds_formed": fmt(after - before, ec),
                     "n_drug_cage_bonds": len(inter),
                     "drug_cage_bonds": ";".join(sorted(f"{ec[i]}{i}-{ec[j]}{j}" for i, j in inter))})
    df = pd.DataFrame(rows)
    df.to_csv(BASE / "data" / "processed" / "adsorption_integrity.csv", index=False)
    # adsorption regime = presence of a drug-cage bond (same rule as the other studies),
    # replacing the earlier closest-contact < 1.9 A rule
    master = BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv"
    m = pd.read_csv(master)
    m["adsorption_mode"] = m["adsorption_mode"].astype(object)
    nb = df.set_index("name").n_drug_cage_bonds
    ok = m.name.isin(nb.index)
    m.loc[ok, "adsorption_mode"] = m.loc[ok, "name"].map(lambda n: "chemisorption" if nb[n] else "physisorption")
    m.to_csv(master, index=False)
    print(df[["name", "drug_intact", "n_drug_cage_bonds", "drug_bonds_broken", "drug_bonds_formed"]].to_string())


if __name__ == "__main__":
    main()
