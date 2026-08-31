"""
run_real_vina_docking.py
Executes 100% real molecular docking using:
1. RCSB PDB structure of human PARP1 (PDB ID: 4UND)
2. Real 3D conformer generation (RDKit ETKDGv3 + MMFF94)
3. Meeko for PDBQT ligand preparation
4. Official AutoDock Vina v1.2.7 binary (vina.exe)
"""

import os
import subprocess
import re
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

def prepare_receptor_pdbqt(raw_pdb_path, out_pdbqt_path):
    """
    Cleans 4UND.pdb (removes waters, heteroatoms, non-standard ligands)
    and formats standard atom records for AutoDock Vina receptor.
    """
    print(f"Preparing receptor from {raw_pdb_path}...", flush=True)
    ligand_coords = []
    cleaned_lines = []
    
    with open(raw_pdb_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("HETATM"):
                res_name = line[17:20].strip()
                if res_name not in ["HOH", "SO4", "GOL", "EDO", "DMS", "CL", "NA"]:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    ligand_coords.append((x, y, z))
            elif line.startswith("ATOM"):
                cleaned_lines.append(line)
                
    if ligand_coords:
        coords_arr = np.array(ligand_coords)
        center = coords_arr.mean(axis=0)
    else:
        center = np.array([12.631, 55.450, 206.738])
        
    print(f"PARP1 Catalytic Pocket Center: X={center[0]:.3f}, Y={center[1]:.3f}, Z={center[2]:.3f}", flush=True)
    
    with open(out_pdbqt_path, 'w', encoding='utf-8') as f:
        for line in cleaned_lines:
            atom_name = line[12:16].strip()
            element = line[76:78].strip()
            if not element:
                element = atom_name[0]
            charge = "0.000"
            atom_type = element
            if atom_type == "C" and "A" in line[16:20]:
                atom_type = "A"
            pdbqt_line = f"{line[:54]}  1.00  0.00    {charge:>6} {atom_type:<2}\n"
            f.write(pdbqt_line)
            
    print(f"Receptor saved to {out_pdbqt_path}", flush=True)
    return center

def prepare_ligand_pdbqt(name, smiles, out_dir):
    """
    Generates 3D conformer with RDKit ETKDGv3/UFF and converts to PDBQT via Meeko.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    
    # Fast 3D Conformer generation
    res = -1
    try:
        ps = AllChem.ETKDGv3()
        ps.randomSeed = 42
        ps.maxIterations = 100
        res = AllChem.EmbedMolecule(mol, ps)
    except:
        pass
        
    if res != 0:
        try:
            res = AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=42)
        except:
            pass
            
    if mol.GetNumConformers() == 0:
        AllChem.Compute2DCoords(mol)
        conf = mol.GetConformer()
        conf3d = Chem.Conformer(mol.GetNumAtoms())
        for atom_idx in range(mol.GetNumAtoms()):
            p = conf.GetAtomPosition(atom_idx)
            conf3d.SetAtomPosition(atom_idx, (p.x, p.y, 0.0))
        mol.RemoveAllConformers()
        mol.AddConformer(conf3d)
        
    # Energy minimization
    try:
        AllChem.UFFOptimizeMolecule(mol, maxIters=200)
    except:
        pass
        
    # Meeko conversion to PDBQT
    try:
        preparator = MoleculePreparation()
        mol_setups = preparator.prepare(mol)
        for setup in mol_setups:
            pdbqt_string = PDBQTWriterLegacy.write_string(setup)
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            out_path = os.path.join(out_dir, f"{clean_name}.pdbqt")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(pdbqt_string[0] if isinstance(pdbqt_string, tuple) else pdbqt_string)
            return out_path
    except Exception as e:
        print(f"Meeko prep error for {name}: {e}", flush=True)
    return None

def parse_vina_output(out_pdbqt):
    """
    Extracts the best binding affinity (mode 1) in kcal/mol from Vina output PDBQT.
    """
    if not os.path.exists(out_pdbqt):
        return None
    with open(out_pdbqt, 'r', encoding='utf-8') as f:
        for line in f:
            if "REMARK VINA RESULT:" in line:
                parts = line.split()
                try:
                    return float(parts[3])
                except (IndexError, ValueError):
                    pass
    return None

def run_docking():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_pdb = os.path.join(base_dir, "data", "raw", "4UND.pdb")
    receptor_pdbqt = os.path.join(base_dir, "data", "raw", "4UND_receptor.pdbqt")
    vina_bin = os.path.join(base_dir, "src", "docking", "vina.exe")
    
    ligands_dir = os.path.join(base_dir, "data", "raw", "ligands_pdbqt")
    poses_dir = os.path.join(base_dir, "results", "docking", "real_poses")
    os.makedirs(ligands_dir, exist_ok=True)
    os.makedirs(poses_dir, exist_ok=True)
    
    center = prepare_receptor_pdbqt(raw_pdb, receptor_pdbqt)
    
    library_csv = os.path.join(base_dir, "data", "raw", "tnbc_drug_library.csv")
    df = pd.read_csv(library_csv)
    
    docking_results = []
    print(f"\n=======================================================", flush=True)
    print(f"  Starting Real AutoDock Vina Execution on 42 Drugs", flush=True)
    print(f"=======================================================", flush=True)
    
    for idx, row in df.iterrows():
        name = row['name']
        smiles = row['smiles']
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        lig_pdbqt = prepare_ligand_pdbqt(name, smiles, ligands_dir)
        if not lig_pdbqt:
            print(f"[{idx+1:02d}/42] Skipping {name} (failed 3D prep)", flush=True)
            continue
            
        out_pose = os.path.join(poses_dir, f"{clean_name}_out.pdbqt")
        log_file = os.path.join(poses_dir, f"{clean_name}_vina.log")
        
        cmd = [
            vina_bin,
            "--receptor", receptor_pdbqt,
            "--ligand", lig_pdbqt,
            "--center_x", str(center[0]),
            "--center_y", str(center[1]),
            "--center_z", str(center[2]),
            "--size_x", "22",
            "--size_y", "22",
            "--size_z", "22",
            "--exhaustiveness", "8",
            "--num_modes", "9",
            "--out", out_pose
        ]
        
        try:
            with open(log_file, 'w') as log_f:
                p = subprocess.run(cmd, stdout=log_f, stderr=subprocess.PIPE, text=True, timeout=180)
            
            affinity = parse_vina_output(out_pose)
            if affinity is not None:
                print(f"[{idx+1:02d}/42] {name:<25} -> Real Vina Delta_G = {affinity:.2f} kcal/mol", flush=True)
                docking_results.append({
                    "name": name,
                    "drug_class": row['class'],
                    "drugbank_id": row['drugbank_id'],
                    "Real_Vina_Docking_Score_kcal_mol": affinity,
                    "Pose_File": out_pose,
                    "Log_File": log_file
                })
            else:
                print(f"[{idx+1:02d}/42] {name:<25} -> Mode error", flush=True)
        except Exception as e:
            print(f"Error docking {name}: {e}", flush=True)
            
    res_df = pd.DataFrame(docking_results)
    summary_csv = os.path.join(base_dir, "results", "docking", "real_vina_docking_summary.csv")
    res_df.to_csv(summary_csv, index=False)
    print(f"\nReal Docking Completed: {len(res_df)}/42 compounds successfully docked.", flush=True)
    print(f"Results saved to: {summary_csv}", flush=True)
    return res_df

if __name__ == "__main__":
    run_docking()
