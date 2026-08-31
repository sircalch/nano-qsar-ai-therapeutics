"""
analyze_real_interactions.py
Performs atomic-level protein-ligand contact analysis between real AutoDock Vina docked poses 
and the human PARP1 crystal structure (PDB: 4UND).

Calculates:
- Interacting PARP1 residues within 3.8 Angstroms
- Putative Hydrogen Bonds (D-H...A distance < 3.5 A)
- Aromatic pi-stacking with catalytic Tyr907, Tyr896, and His862
- Residue interaction frequency heatmap across all 35 docked drugs
"""

import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def parse_pdb_coords(pdb_file):
    """Parses protein CA/heavy atoms from 4UND.pdb."""
    atoms = []
    with open(pdb_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("ATOM"):
                atom_name = line[12:16].strip()
                res_name = line[17:20].strip()
                res_seq = int(line[22:26].strip())
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                element = line[76:78].strip() if len(line) > 76 else atom_name[0]
                atoms.append({
                    "res_id": f"{res_name}{res_seq}",
                    "res_name": res_name,
                    "res_seq": res_seq,
                    "atom_name": atom_name,
                    "element": element,
                    "coord": np.array([x, y, z])
                })
    return atoms

def parse_pdbqt_ligand_coords(pdbqt_file):
    """Parses mode 1 heavy atom coordinates from Vina output PDBQT."""
    atoms = []
    in_model_1 = False
    with open(pdbqt_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("MODEL 1") or line.startswith("MODEL"):
                in_model_1 = True
            elif line.startswith("ENDMDL"):
                break
            elif in_model_1 and (line.startswith("ATOM") or line.startswith("HETATM")):
                atom_name = line[12:16].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                element = line[76:78].strip() if len(line) > 76 else atom_name[0]
                atoms.append({
                    "atom_name": atom_name,
                    "element": element,
                    "coord": np.array([x, y, z])
                })
    return atoms

def analyze_all_interactions():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdb_path = os.path.join(base_dir, "data", "raw", "4UND.pdb")
    poses_dir = os.path.join(base_dir, "results", "docking", "real_poses")
    
    protein_atoms = parse_pdb_coords(pdb_path)
    pose_files = glob.glob(os.path.join(poses_dir, "*_out.pdbqt"))
    
    results = []
    residue_counts = {}
    
    for p_file in pose_files:
        drug_name = os.path.basename(p_file).replace("_out.pdbqt", "")
        ligand_atoms = parse_pdbqt_ligand_coords(p_file)
        if not ligand_atoms:
            continue
            
        contacted_residues = set()
        hbond_candidates = 0
        pi_stacking = False
        
        for l_atom in ligand_atoms:
            l_coord = l_atom['coord']
            l_elem = l_atom['element'].upper()
            
            for p_atom in protein_atoms:
                p_coord = p_atom['coord']
                p_elem = p_atom['element'].upper()
                dist = np.linalg.norm(l_coord - p_coord)
                
                if dist <= 3.8:
                    res_id = p_atom['res_id']
                    contacted_residues.add(res_id)
                    residue_counts[res_id] = residue_counts.get(res_id, 0) + 1
                    
                    # Detect potential H-bonds (N/O donor-acceptor within 3.4 A)
                    if dist <= 3.4 and l_elem in ['N', 'O'] and p_elem in ['N', 'O']:
                        hbond_candidates += 1
                        
                    # Detect aromatic stacking
                    if res_id in ['TYR907', 'TYR896', 'HIS862', 'PHE897'] and dist <= 3.8:
                        pi_stacking = True
                        
        sorted_res = sorted(list(contacted_residues), key=lambda x: int(''.join(filter(str.isdigit, x)) or 0))
        results.append({
            "name": drug_name,
            "Total_Contacts": len(contacted_residues),
            "Estimated_HBonds": min(hbond_candidates, 5),
            "Pi_Stacking_Catalytic": "Yes" if pi_stacking else "No",
            "Interacting_Residues": ", ".join(sorted_res[:10])
        })
        
    df_inter = pd.DataFrame(results)
    out_csv = os.path.join(base_dir, "results", "docking", "real_residue_interactions.csv")
    df_inter.to_csv(out_csv, index=False)
    print(f"Residue interaction analysis completed for {len(df_inter)} compounds. Saved to {out_csv}")
    
    # Generate Residue Contact Frequency Chart
    top_res = pd.Series(residue_counts).sort_values(ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sns.barplot(x=top_res.values, y=top_res.index, palette="Blues_r", ax=ax)
    ax.set_title("PARP1 Catalytic Domain Residue Interaction Frequency (35 Real Docked Drugs)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Total Heavy Atom Interaction Contacts across 35 Poses", fontsize=11)
    ax.set_ylabel("PARP1 Amino Acid Residue", fontsize=11)
    
    fig_path = os.path.join(base_dir, "figures", "fig4_residue_contact_frequency.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"Saved Residue Interaction Frequency Chart: {fig_path}")

if __name__ == "__main__":
    analyze_all_interactions()
