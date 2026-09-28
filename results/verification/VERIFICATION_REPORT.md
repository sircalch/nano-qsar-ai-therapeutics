# Independent verification of the TNBC / B36N36 manuscript (2026-09-28)

Each check recomputes the reported values from the raw outputs with code that does
not reuse the pipeline's logic (`src/verification/`, plus the inline checks recorded
below). The only exception is the extraction of the crystal ligand from 4UND.

| What | How | Result |
|---|---|---|
| Final poses | SHA-256 of complex_opt.xyz vs result.json | 30/30 unchanged |
| Adsorption energies (30 complexes) | xtb 6.7.1 GFN2 single points re-run: complex, frozen cage, frozen drug, relaxed drug | identical (max 8e-12 Eh); ΔE_int and ΔE_ads identical in 30/30 |
| Regime, drug integrity, closest contact | bond analysis re-implemented | 30/30, 30/30, 30/30 |
| Cage in every complex | bond census with the four-ring diagonal rule; energy of the frozen cage | 108 B–N bonds in 30/30, no B–B/N–N bond; 0.04–31.63 kcal/mol above the relaxed cage (text: 0.0–31.6) |
| Dative bonds | types and lengths from the complex geometries | 8 B–O and 5 B–N, 1.43–1.74 Å (text identical); doxorubicin also forms a covalent C–N bond (1.48 Å) |
| Frontier orbitals | table vs xtb results; comparison with the cage | all LUMOs below the cage LUMO; HOMOs below the cage HOMO for exatecan, olaparib, paclitaxel, SN-38, talazoparib (text identical) |
| Docking scores | best REMARK VINA RESULT of each pose file | 30/30 |
| Redocking controls | RMSD recomputed with RDKit | 0.507 and 1.267 Å, identical |
| Identity of the 30 modelled drugs | InChIKey from SMILES vs PubChem record of the CID | 30/30 (the three Pt agents are not modelled, as the text states) |
| QSPR | full nested CV and 1,000 permutations re-run (outputs rewritten 2026-09-28) | identical to the reported results (no change in any file) |
| References | DOI/title against Crossref; relevance read sentence by sentence | 0 problems |

## Found and corrected during the reread (2026-09-27)
- "A single conformer of talazoparib docks 6.7 Å away" had no supporting file. The control
  (`src/docking/single_conformer_control.py`) gives 1.27 Å, so the sentence was removed.

## Open before submission
- The rebuilt code and data are on the local branch `rebuild-2026-09` only. The
  availability statement is true only after that branch is pushed (with the author's approval).
