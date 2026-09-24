"""
run_vina_docking.py
===================
AutoDock Vina docking of the 30 organic anti-TNBC drugs into the nicotinamide
(catalytic) pocket of human PARP1, PDB 4UND chain A.

Protocol
  receptor : 4UND chain A only; waters, ions and the co-crystallised
             talazoparib (2YQ) removed; missing atoms + hydrogens at pH 7.4
             added with PDBFixer; AutoDock atom types / Gasteiger charges
             assigned with Meeko (mk_prepare_receptor).
  box      : 22 x 22 x 22 A centred on the heavy-atom centroid of 2YQ in
             chain A (the ligand of the chain being docked into).
  ligands  : PubChem SMILES -> RDKit ETKDGv3 + MMFF, Meeko PDBQT. Vina keeps
             rings rigid, so up to 5 distinct ring conformers are docked per
             drug and the best score is kept.
  search   : Vina 1.2.7, exhaustiveness 16, 9 modes, seed 42.
  controls : (1) self-redocking of 2YQ from its crystal conformation;
             (2) 2YQ rebuilt from SMILES through the production protocol.
             Symmetry-aware heavy-atom RMSD of the top pose vs. the crystal
             pose (RDKit CalcRMS, no re-alignment).

Earlier versions centred the box on the mean of the 2YQ copies of BOTH
chains, which put it at the A/B interface ~23 A from either pocket; that run
is superseded.

Outputs
  data/raw/4UND_A_receptor.pdbqt, data/raw/4UND_A_H.pdb
  results/docking/real_poses/<drug>_out.pdbqt, <drug>_vina.log
  results/docking/real_vina_docking_summary.csv
  data/processed/redocking_validation.csv
  data/processed/dataset_tnbc_bn_pristine.csv  (vina_4UND_kcal_mol column)
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
POSES = BASE / "results" / "docking" / "real_poses"
LIGS = RAW / "ligands_pdbqt"
VINA = BASE / "src" / "docking" / "vina.exe"
MK_REC = "mk_prepare_receptor"

CHAIN = "A"
BOX = 22.0
EXHAUSTIVENESS = 16
SEED = 42
N_CONF = 5
PT = {"Cisplatin", "Carboplatin", "Oxaliplatin"}


def slug(name):
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


# ------------------------------------------------------------------ receptor
def crystal_ligand_block(pdb, resn="2YQ", chain=CHAIN):
    """HETATM + CONECT records of one ligand copy (CONECT is needed: proximity
    bonding alone misses a ring bond of 2YQ)."""
    lines = open(pdb, encoding="utf-8").readlines()
    het = [l for l in lines if l.startswith("HETATM") and l[17:20] == resn and l[21] == chain]
    ids = {l[6:11].strip() for l in het}
    con = [l for l in lines if l.startswith("CONECT") and l[6:11].strip() in ids]
    return "".join(het + con) + "END\n"


def box_center(pdb):
    blk = crystal_ligand_block(pdb)
    xyz = np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])]
                    for l in blk.splitlines() if l.startswith("HETATM")
                    and l[76:78].strip() != "H"])
    return xyz.mean(0)


def prepare_receptor(pdb):
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile

    fixer = PDBFixer(filename=str(pdb))
    fixer.removeChains([c.index for c in fixer.topology.chains() if c.id != CHAIN])
    fixer.removeHeterogens(keepWater=False)
    fixer.findMissingResidues()
    fixer.missingResidues = {}          # do not model unresolved loops
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(7.4)
    rec_h = RAW / f"4UND_{CHAIN}_H.pdb"
    with open(rec_h, "w") as fh:
        PDBFile.writeFile(fixer.topology, fixer.positions, fh, keepIds=True)
    base = RAW / f"4UND_{CHAIN}_receptor"
    p = subprocess.run([MK_REC, "--read_pdb", str(rec_h), "-o", str(base), "-p",
                        "--default_altloc", "A"], capture_output=True, text=True)
    pdbqt = Path(str(base) + ".pdbqt")
    if not pdbqt.exists():
        sys.exit(f"mk_prepare_receptor failed:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return rec_h, pdbqt


# ------------------------------------------------------------------- ligands
def _ring_rms(mol, i, j, ring_atoms):
    return rdMolAlign.AlignMol(Chem.Mol(mol), Chem.Mol(mol), prbCid=i, refCid=j,
                               atomMap=[(a, a) for a in ring_atoms])


def ligand_pdbqts(name, smiles, out_dir, n_max=None):
    """PDBQT inputs for docking. Vina keeps rings rigid, so for molecules with
    non-aromatic rings an ensemble of up to n_max ring conformers (ETKDGv3 +
    MMFF, kept when ring-atom RMSD > 0.25 A to all kept ones, lowest energy
    first) is docked and the best-scoring pose is retained."""
    from meeko import MoleculePreparation, PDBQTWriterLegacy

    n_max = n_max or N_CONF
    mol = Chem.MolFromSmiles(smiles)
    mol = max(Chem.GetMolFrags(mol, asMols=True), key=lambda m: m.GetNumHeavyAtoms())
    mol = Chem.AddHs(mol)
    ps = AllChem.ETKDGv3()
    ps.randomSeed = SEED
    cids = list(AllChem.EmbedMultipleConfs(mol, numConfs=30, params=ps))
    if not cids:
        ps.useRandomCoords = True
        cids = list(AllChem.EmbedMultipleConfs(mol, numConfs=30, params=ps))
    if not cids:
        raise RuntimeError(f"embedding failed for {name}")
    energies = [e for _, e in AllChem.MMFFOptimizeMoleculeConfs(mol, maxIters=2000)]
    ring_atoms = sorted({a for ring in mol.GetRingInfo().AtomRings() for a in ring
                         if not mol.GetAtomWithIdx(a).GetIsAromatic()})
    order = sorted(cids, key=lambda c: energies[c])
    keep = [order[0]]
    if ring_atoms:
        for c in order[1:]:
            if len(keep) >= n_max:
                break
            if all(_ring_rms(mol, c, k, ring_atoms) > 0.25 for k in keep):
                keep.append(c)
    outs = []
    for k, cid in enumerate(keep):
        m = Chem.Mol(mol)
        conf = Chem.Conformer(mol.GetConformer(cid))
        m.RemoveAllConformers()
        m.AddConformer(conf, assignId=True)
        txt, ok, err = PDBQTWriterLegacy.write_string(MoleculePreparation().prepare(m)[0])
        if not ok:
            raise RuntimeError(f"meeko failed for {name}: {err}")
        out = out_dir / f"{slug(name)}_c{k}.pdbqt"
        out.write_text(txt)
        outs.append(out)
    return outs


def dock_ensemble(receptor, ligands, center, stem):
    """Dock every conformer input; keep the best-scoring run as <stem>_out.pdbqt."""
    best = None
    for k, lig in enumerate(ligands):
        s = run_vina(receptor, lig, center, POSES / f"{stem}_c{k}_out.pdbqt",
                     POSES / f"{stem}_c{k}_vina.log")
        if best is None or s < best[0]:
            best = (s, k)
    s, k = best
    shutil.copy(POSES / f"{stem}_c{k}_out.pdbqt", POSES / f"{stem}_out.pdbqt")
    shutil.copy(POSES / f"{stem}_c{k}_vina.log", POSES / f"{stem}_vina.log")
    for j in range(len(ligands)):
        for suf in ("_out.pdbqt", "_vina.log"):
            (POSES / f"{stem}_c{j}{suf}").unlink()
    return s, len(ligands)


def run_vina(receptor, ligand, center, out_pose, log):
    cmd = [str(VINA), "--receptor", str(receptor), "--ligand", str(ligand),
           "--center_x", f"{center[0]:.3f}", "--center_y", f"{center[1]:.3f}",
           "--center_z", f"{center[2]:.3f}", "--size_x", str(BOX), "--size_y", str(BOX),
           "--size_z", str(BOX), "--exhaustiveness", str(EXHAUSTIVENESS),
           "--num_modes", "9", "--seed", str(SEED), "--cpu", "4", "--out", str(out_pose)]
    with open(log, "w") as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, check=True, timeout=3600)
    for line in open(out_pose):
        if line.startswith("REMARK VINA RESULT:"):
            return float(line.split()[3])
    raise RuntimeError(f"no score in {out_pose}")


# ------------------------------------------------------------------ redocking
def _rmsd_to_crystal(pose_pdbqt, ref):
    from meeko import PDBQTMolecule, RDKitMolCreate
    docked = RDKitMolCreate.from_pdbqt_mol(
        PDBQTMolecule.from_file(str(pose_pdbqt), skip_typing=True))[0]
    return rdMolAlign.CalcRMS(Chem.RemoveHs(docked), ref)  # symmetry-aware, no re-alignment


def redock(pdb, receptor, center, smiles):
    """Control 1: self-redocking of the crystal ligand from its crystal
    conformation (H added; Vina randomises position and torsions).
    Control 2: the same ligand rebuilt from SMILES through the production
    conformer-ensemble protocol."""
    from meeko import MoleculePreparation, PDBQTWriterLegacy

    ref = Chem.MolFromPDBBlock(crystal_ligand_block(pdb), removeHs=True)
    ref = AllChem.AssignBondOrdersFromTemplate(Chem.MolFromSmiles(smiles), ref)
    txt, ok, err = PDBQTWriterLegacy.write_string(
        MoleculePreparation().prepare(Chem.AddHs(ref, addCoords=True))[0])
    xtal = POSES / "2YQ_xtal_input.pdbqt"
    xtal.write_text(txt)
    s1 = run_vina(receptor, xtal, center, POSES / "2YQ_redock_out.pdbqt",
                  POSES / "2YQ_redock_vina.log")
    r1 = _rmsd_to_crystal(POSES / "2YQ_redock_out.pdbqt", ref)
    s2, _ = dock_ensemble(receptor, ligand_pdbqts("2YQ_smiles", smiles, POSES), center, "2YQ_smiles")
    r2 = _rmsd_to_crystal(POSES / "2YQ_smiles_out.pdbqt", ref)
    return (s1, r1), (s2, r2), ref.GetNumAtoms()


def _dock_one(args):
    name, smiles, receptor, center = args
    stem = slug(name)
    out = POSES / f"{stem}_out.pdbqt"
    if out.exists() and not list(POSES.glob(f"{stem}_c*_out.pdbqt")):
        score = next(float(l.split()[3]) for l in open(out) if l.startswith("REMARK VINA RESULT:"))
        n_conf = len(list(LIGS.glob(f"{stem}_c*.pdbqt")))
        return name, score, n_conf
    s, n_conf = dock_ensemble(receptor, ligand_pdbqts(name, smiles, LIGS), center, stem)
    return name, s, n_conf


def main(workers=4):
    """Resumable: controls are skipped when already on disk, and drugs whose
    final pose exists are read back instead of re-docked. Drugs run in
    parallel (each Vina run uses 4 threads)."""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    POSES.mkdir(parents=True, exist_ok=True)
    LIGS.mkdir(parents=True, exist_ok=True)
    pdb = RAW / "4UND.pdb"
    center = box_center(pdb)
    receptor = RAW / f"4UND_{CHAIN}_receptor.pdbqt"
    if not receptor.exists():
        _, receptor = prepare_receptor(pdb)
    print(f"receptor {receptor.name}; box centre {np.round(center, 3)} (2YQ, chain {CHAIN})", flush=True)

    master = PROC / "dataset_tnbc_bn_pristine.csv"
    df = pd.read_csv(master)
    if not (PROC / "redocking_validation.csv").exists() or not (POSES / "2YQ_smiles_out.pdbqt").exists():
        tala = df.set_index("name").loc["Talazoparib", "smiles"]
        (s1, r1), (s2, r2), nha = redock(pdb, receptor, center, tala)
        ctrl = []
        for mode, sc, r, pose in (("self-redock, crystal conformation", s1, r1, "2YQ_redock_out.pdbqt"),
                                  ("production protocol, from SMILES", s2, r2, "2YQ_smiles_out.pdbqt")):
            ctrl.append({"pdb_id": "4UND", "chain": CHAIN,
                         "target_desc": "Human PARP1 catalytic domain (X-ray)", "resolution_A": 2.2,
                         "probe_ligand": "Talazoparib (2YQ)", "control": mode, "affinity_kcal_mol": sc,
                         "n_heavy_atoms": nha, "rmsd_heavy_atom_A": round(r, 3),
                         "docking_status": "PASSED (RMSD <= 2.0 A)" if r <= 2.0 else "FAILED (RMSD > 2.0 A)",
                         "mapping_method": "RDKit CalcRMS (symmetry-aware, no re-alignment)",
                         "pose_file": f"results/docking/real_poses/{pose}"})
            print(f"redocking 2YQ [{mode}]: {sc:.2f} kcal/mol, RMSD {r:.2f} A", flush=True)
        pd.DataFrame(ctrl).to_csv(PROC / "redocking_validation.csv", index=False)

    todo = df[~df["name"].isin(PT)]
    scores = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(_dock_one, (r.name, r.smiles, receptor, center)) for r in todo.itertuples()]
        for k, f in enumerate(as_completed(futs), 1):
            name, s, n_conf = f.result()
            scores[name] = (s, n_conf)
            print(f"[{k:02d}/{len(todo)}] {name:<14} {s:7.3f} kcal/mol  ({n_conf} conformer(s))", flush=True)

    rows = [{"name": r.name, "drug_class": r.drug_class, "drugbank_id": r.drugbank_id,
             "Real_Vina_Docking_Score_kcal_mol": scores[r.name][0], "n_ring_conformers": scores[r.name][1],
             "Pose_File": f"results/docking/real_poses/{slug(r.name)}_out.pdbqt",
             "Log_File": f"results/docking/real_poses/{slug(r.name)}_vina.log"} for r in todo.itertuples()]
    res = pd.DataFrame(rows)
    res.to_csv(BASE / "results" / "docking" / "real_vina_docking_summary.csv", index=False)
    df = pd.read_csv(master)      # re-read: other steps may have written it meanwhile
    df["vina_4UND_kcal_mol"] = df["name"].map(dict(zip(res["name"], res["Real_Vina_Docking_Score_kcal_mol"])))
    df.to_csv(master, index=False)
    print(f"updated {master.name}: {df['vina_4UND_kcal_mol'].notna().sum()} scores", flush=True)


if __name__ == "__main__":
    main()
