# Anti-TNBC drugs on a B₃₆N₃₆ cage and in PARP1

Code and data for *"Physisorption and dative-bond chemisorption of anti-TNBC drugs on a B₃₆N₃₆
fullerene-like cage: validated PARP1 docking, GFN2-xTB adsorption and QSPR analysis"*
(A. Monreal Hernández).

`python run_entire_study.py` regenerates every number, table and figure from the raw inputs.

## Pipeline

| Step | Script | Output |
|---|---|---|
| Compound identities from PubChem (InChIKey check) | `src/descriptors/fix_structures_from_pubchem.py` | `data/processed/structure_audit_pubchem.csv` |
| Valid B₃₆N₃₆ cage (octahedral GP(1,1), 108 B–N bonds), relaxed, no imaginary frequencies | `src/quantum/build_b36n36_cage.py` | `calculations/tnbc/B36N36_*` |
| GFN2-xTB adsorption, 4 relaxed orientations per drug | `recompute_tnbc_adsorption.py` | `calculations/tnbc_recompute/<drug>/` |
| PARP1 docking (PDB 4UND chain A, PDBFixer + Meeko, Vina 1.2.7, ring-conformer ensemble), two redocking controls | `src/docking/run_vina_docking.py` | `results/docking/`, `data/processed/redocking_validation.csv` |
| Dataset assembly; bond-integrity check and adsorption regime | `recompute_tnbc_adsorption.py --commit-datasets`, `src/quantum/integrity_check.py` | `data/processed/dataset_tnbc_bn_pristine.csv`, `adsorption_integrity.csv` |
| Residue contacts | `src/docking/contacts.py` | `results/docking/residue_contacts.csv` |
| QSPR (ridge, nested 5×5 CV, Y-scrambling, applicability domain) | `src/ml_models/qspr_nested_cv.py` | `results/qspr/` |
| Figures (Springer size, PDF + 600 dpi PNG/TIFF) | `src/figures/make_figures.py` | `figures/Fig1–7` |
| Manuscript and SI (Word) | `src/manuscript/build_manuscript.py`, `build_si.py` | `manuscript/submission/` |

## Requirements

Python 3.12 with RDKit, pandas, scikit-learn, matplotlib, adjustText, python-docx, Meeko, PDBFixer/OpenMM;
xtb 6.7.1 (GFN2-xTB); AutoDock Vina 1.2.7 (`src/docking/vina.exe`); open-source PyMOL (separate
environment, path in `src/figures/render3d.py`) for the molecular renders.

## History

A 2026-09-22 audit replaced 24 of 33 compound structures that did not match PubChem, an invalid cage
(random B/N labelling with B–B and N–N bonds) and a docking box that sat between the two PARP1 chains.
All results were recomputed; superseded files are kept outside the repository.

MIT licence.
