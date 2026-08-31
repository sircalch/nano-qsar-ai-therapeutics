"""
compute_descriptors.py
Calculates 2D and 3D physicochemical, constitutional, and topological QSAR/QSPR descriptors
using RDKit for isolated drugs and drug-nanocarrier complexes.
"""

import os
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, rdMolDescriptors, Lipinski

def calculate_esol_logs(mol):
    """
    Delaney ESOL method for calculating aqueous solubility (LogS):
    LogS = 0.16 - 0.63*clogP - 0.0062*MW + 0.066*RB - 0.74*AP
    """
    mw = Descriptors.MolWt(mol)
    clogp = Crippen.MolLogP(mol)
    rb = Descriptors.NumRotatableBonds(mol)
    
    # Aromatic proportion
    aromatic_atoms = sum(1 for atom in mol.GetAtoms() if atom.GetIsAromatic())
    heavy_atoms = mol.GetNumHeavyAtoms()
    ap = (aromatic_atoms / heavy_atoms) if heavy_atoms > 0 else 0.0
    
    logs = 0.16 - (0.63 * clogp) - (0.0062 * mw) + (0.066 * rb) - (0.74 * ap)
    return logs

def compute_drug_descriptors(csv_path):
    df = pd.read_csv(csv_path)
    records = []
    
    for idx, row in df.iterrows():
        name = row['name']
        drug_class = row['class']
        smiles = row['smiles']
        db_id = row['drugbank_id']
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"Warning: Could not parse SMILES for {name}")
            continue
            
        mol_h = Chem.AddHs(mol)
        
        # 1. 1D/2D Descriptors
        mw = Descriptors.MolWt(mol)
        logp = Crippen.MolLogP(mol)
        logs = calculate_esol_logs(mol)
        ws_mg_ml = 10**logs * mw * 1000.0 / 1000.0  # approximate mg/mL = 10^LogS * MW (g/mol)
        if ws_mg_ml < 0:
            ws_mg_ml = 1e-6
            
        hba = Lipinski.NumHAcceptors(mol)
        hbd = Lipinski.NumHDonors(mol)
        tpsa = Descriptors.TPSA(mol)
        rbc = Descriptors.NumRotatableBonds(mol)
        nor = Lipinski.RingCount(mol)
        arom_rings = Lipinski.NumAromaticRings(mol)
        mr = Crippen.MolMR(mol)  # Molar Refractivity (proxy for polarizability alpha)
        polarizability_alpha = mr * 0.3964  # Lorentz-Lorenz scaling to Angstrom^3
        
        fraction_csp3 = rdMolDescriptors.CalcFractionCSP3(mol)
        heavy_atoms = mol.GetNumHeavyAtoms()
        
        records.append({
            "name": name,
            "drug_class": drug_class,
            "drugbank_id": db_id,
            "smiles": smiles,
            "MW": round(mw, 3),
            "LogP": round(logp, 3),
            "LogS": round(logs, 3),
            "WS_mg_mL": round(max(ws_mg_ml, 1e-5), 4),
            "HBA": int(hba),
            "HBD": int(hbd),
            "PSA": round(tpsa, 2),
            "RBC": int(rbc),
            "NOR": int(nor),
            "AromRings": int(arom_rings),
            "Polarizability_alpha": round(polarizability_alpha, 3),
            "Fraction_Csp3": round(fraction_csp3, 3),
            "HeavyAtoms": int(heavy_atoms)
        })
        
    desc_df = pd.DataFrame(records)
    return desc_df

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_csv = os.path.join(base_dir, "data", "raw", "tnbc_drug_library.csv")
    out_csv = os.path.join(base_dir, "data", "processed", "tnbc_isolated_descriptors.csv")
    
    desc_df = compute_drug_descriptors(raw_csv)
    desc_df.to_csv(out_csv, index=False)
    print(f"Calculated descriptors for {len(desc_df)} compounds. Saved to {out_csv}")
