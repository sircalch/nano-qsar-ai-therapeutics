"""
fix_structures_from_pubchem.py
==============================
Replaces every SMILES of the master dataset with the PubChem isomeric SMILES
of the same compound name, and records the identity check.

Why: a 2026-09-22 audit (InChIKey skeleton block vs PubChem) found that 24 of
the 33 SMILES in dataset_tnbc_bn_pristine.csv encoded a different molecule
(wrong formula or connectivity), e.g. talazoparib written as a CF3 analogue
without its triazole. Every descriptor, docking score and adsorption energy of
those rows belonged to another compound.

Outputs
  data/processed/structure_audit_pubchem.csv   (old vs new SMILES, formulae, CID)
  data/processed/dataset_tnbc_bn_pristine.csv  (smiles, formal_charge, MolWt, MolMR
                                                updated; computed columns blanked
                                                so nothing stale survives)
  data/raw/tnbc_drug_library.csv               (smiles updated)
"""
import sys
import time
import urllib.parse
from pathlib import Path

import pandas as pd
import requests
from rdkit import Chem, RDLogger
from rdkit.Chem import Crippen, Descriptors
from rdkit.Chem.rdMolDescriptors import CalcMolFormula

RDLogger.DisableLog("rdApp.*")
BASE = Path(__file__).resolve().parents[2]
MASTER = BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv"
LIBRARY = BASE / "data" / "raw" / "tnbc_drug_library.csv"
AUDIT = BASE / "data" / "processed" / "structure_audit_pubchem.csv"
ALIAS = {"SN-38": "7-ethyl-10-hydroxycamptothecin"}
COMPUTED = ["E_HOMO_eV", "E_LUMO_eV", "Gap_eV", "Eta_eV", "Mu_eV", "Omega_eV", "E_drug_Eh",
            "vina_4UND_kcal_mol", "delta_Eint_SP_kcal_mol", "min_contact_A",
            "delta_Eads_kcal_mol", "adsorption_mode"]


def pubchem(name):
    q = urllib.parse.quote(ALIAS.get(name, name))
    url = (f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{q}/property/"
           "SMILES,IsomericSMILES,MolecularFormula,InChIKey/JSON")
    for k in range(8):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                p = r.json()["PropertyTable"]["Properties"][0]
                p["smiles"] = p.get("SMILES") or p.get("IsomericSMILES")
                return p
        except requests.RequestException:
            pass
        time.sleep(2 + 3 * k)
    sys.exit(f"PubChem lookup failed for {name}")


def main():
    df = pd.read_csv(MASTER)
    audit = []
    for i, r in df.iterrows():
        p = pubchem(r["name"])
        old = Chem.MolFromSmiles(r["smiles"])
        new = Chem.MolFromSmiles(p["smiles"])
        audit.append({
            "name": r["name"], "pubchem_cid": p["CID"],
            "old_smiles": r["smiles"], "old_formula": CalcMolFormula(old) if old else "",
            "new_smiles": p["smiles"], "pubchem_formula": p["MolecularFormula"],
            "old_matched_pubchem": bool(old) and Chem.MolToInchiKey(old)[:14] == p["InChIKey"][:14],
            "pubchem_inchikey": p["InChIKey"]})
        df.at[i, "smiles"] = p["smiles"]
        df.at[i, "formal_charge"] = Chem.GetFormalCharge(new)
        df.at[i, "MolWt"] = round(Descriptors.MolWt(new), 2)
        df.at[i, "MolMR"] = round(Crippen.MolMR(new), 3)
        time.sleep(0.3)
    for c in COMPUTED:
        if c in df.columns:
            df[c] = None
    pd.DataFrame(audit).to_csv(AUDIT, index=False)
    df.to_csv(MASTER, index=False)
    if LIBRARY.exists():
        lib = pd.read_csv(LIBRARY)
        m = dict(zip(df["name"], df["smiles"]))
        lib["smiles"] = lib["name"].map(m).fillna(lib["smiles"])
        lib.to_csv(LIBRARY, index=False)
    a = pd.DataFrame(audit)
    print(f"{(~a.old_matched_pubchem).sum()}/{len(a)} SMILES replaced (did not match PubChem)")


if __name__ == "__main__":
    main()
