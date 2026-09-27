"""
single_conformer_control.py - why the ring-conformer ensemble is needed.

Talazoparib rebuilt from SMILES is docked with only its lowest-energy ETKDG/MMFF
conformer (Vina keeps rings rigid) instead of the ensemble of the production
protocol; everything else is identical. Writes
results/docking/single_conformer_control.csv (score and RMSD of the top pose to the
crystal pose).

usage: python src/docking/single_conformer_control.py
"""
import sys
from pathlib import Path

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_vina_docking as D  # noqa: E402


def main():
    pdb = D.RAW / "4UND.pdb"
    center = D.box_center(pdb)
    receptor = D.RAW / f"4UND_{D.CHAIN}_receptor.pdbqt"
    smiles = pd.read_csv(D.PROC / "dataset_tnbc_bn_pristine.csv").set_index("name").loc["Talazoparib", "smiles"]
    ref = Chem.MolFromPDBBlock(D.crystal_ligand_block(pdb), removeHs=True)
    ref = AllChem.AssignBondOrdersFromTemplate(Chem.MolFromSmiles(smiles), ref)
    out_dir = D.POSES / "single_conformer"
    out_dir.mkdir(parents=True, exist_ok=True)
    lig = D.ligand_pdbqts("2YQ_single", smiles, out_dir, n_max=1)[0]
    score = D.run_vina(receptor, lig, center, out_dir / "2YQ_single_out.pdbqt", out_dir / "2YQ_single_vina.log")
    rmsd = D._rmsd_to_crystal(out_dir / "2YQ_single_out.pdbqt", ref)
    row = {"control": "from SMILES, lowest-energy conformer only", "affinity_kcal_mol": score,
           "rmsd_heavy_atom_A": round(rmsd, 3), "pose_file": "results/docking/real_poses/single_conformer/2YQ_single_out.pdbqt"}
    out = D.BASE / "results" / "docking" / "single_conformer_control.csv"
    pd.DataFrame([row]).to_csv(out, index=False)
    print(row)


if __name__ == "__main__":
    main()
