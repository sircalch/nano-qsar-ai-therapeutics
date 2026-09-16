# Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22187873.svg)](https://doi.org/10.5281/zenodo.22187873)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/sircalch/nano-qsar-ai-therapeutics/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![AutoDock Vina](https://img.shields.io/badge/Docking-AutoDock%20Vina-orange.svg)](https://github.com/ccsb-scripps/AutoDock-Vina)
[![XAI: SHAP](https://img.shields.io/badge/Explainability-SHAP-purple.svg)](https://github.com/shap/shap)

**Authors**: Andrés Monreal Hernández, Sara Lizbeth Franco Amaya, Carlos Ivanhoe Martínez Osorio
**Affiliation**: Universidad Estatal de Sonora, Hermosillo, Sonora, México

---

## 📌 Abstract

Triple-Negative Breast Cancer (TNBC) remains one of the most aggressive and therapeutically challenging oncological
malignancies due to the clinical absence of estrogen, progesterone, and HER2 receptors. This work presents an
integrated computational framework combining GFN2-xTB tight-binding quantum chemistry (with D4 dispersion), physical
molecular docking (AutoDock Vina v1.2.7), and a leak-free cross-validated explainable QSAR/QSPR surrogate to evaluate
the **pristine** inorganic boron nitride nanocage **B36N36** as a non-carbonaceous drug-loading scaffold for a curated
cohort of anti-TNBC therapeutics.

### Methodological Highlights
- **Macromolecular target**: human Poly(ADP-ribose) Polymerase 1 catalytic domain (PARP1, PDB ID: 4UND, co-crystallized with Olaparib).
- **Curated TNBC drug cohort**: 33 clinical anti-TNBC therapeutics were curated (PARP inhibitors, platinum coordination
  complexes, topoisomerase inhibitors, antimetabolites, and kinase inhibitors). Of these, **30 organic drugs were
  actually modelled** at GFN2-xTB level; the 3 square-planar Pt(II) agents (cisplatin, carboplatin, oxaliplatin) were
  excluded because RDKit/MMFF has no Pt parameters, so a from-SMILES 3D build collapses.
- **Nanocarrier scope**: only the **pristine B36N36 nanocage** was modelled. A carboxyl-functionalized B36N36-COOH
  derivative and a graphene comparison are discussed only as future work in the Conclusions — neither was computed
  or modelled in this study.
- **Quantum conceptual-DFT & HSAB reactivity**: frontier-orbital energies and reactivity indices (chemical hardness
  η, softness S, electrophilicity ω) computed directly from GFN2-xTB output for the isolated 33-drug cohort.
- **Adsorption outcome**: each drug/B36N36 complex was relaxed with GFN2-xTB from four orientations. Of the 30
  modelled drugs, **25 physisorb** on the pristine cage (closest contact 2.2–3.5 Å, ΔE_int,SP = −6 to −31 kcal/mol)
  and a **minority of 5 chemisorb**, forming a covalent B–O or B–N bond (contact 1.37–1.72 Å, ΔE_int,SP = −43 to
  −186 kcal/mol): SN-38, epirubicin, topotecan, lapatinib and rucaparib.
- **Molecular docking**: AutoDock Vina v1.2.7 against the human PARP1 catalytic domain (PDB ID: 4UND) is reported as
  an **exploratory ranking only** — self-redocking of the co-crystallized ligand reproduced the native pose only to
  **>4 Å heavy-atom RMSD**, so Vina scores are not used as a quantitative affinity endpoint.
- **Explainable Machine Learning (Nano-QSAR/XAI)**: a single **RidgeCV** surrogate (four pre-specified descriptors:
  molecular weight, molar refractivity, E_HOMO, electrophilicity ω) evaluated by **leak-free nested 5×5
  cross-validation** (StandardScaler and Ridge strength fit only on each outer-training split), with SHAP feature
  ranking from an auxiliary ExtraTrees fit (reported qualitatively only) and an OECD Principle 3 applicability
  domain (Williams plot).
- **Headline (honest) result**: the descriptor-based QSPR is **non-predictive for both endpoints** (Q²_CV near zero
  for the physisorption interaction energy and for the docking score); the robust, model-free finding of this
  exploratory study is the **chemisorption/physisorption dichotomy itself** (5/30 chemisorbing minority vs. 25/30
  physisorbing majority).

---

## 🔬 Repository Architecture

```
├── data/
│   ├── processed/                             # Processed datasets and descriptor matrices
│   └── raw/                                   # PDB 4UND receptor and ligand coordinates
├── figures/                                   # High-resolution publication figures (300 DPI)
├── manuscript/
│   ├── Beilstein_Manuscript_Monreal_Hernandez_et_al.docx
│   └── submission_ready/                      # Formatted submission package & cover letters
├── results/
│   ├── docking/                               # Vina binding scores, residue contacts & PyMOL sessions
│   ├── models/                                # QSAR benchmark summaries and metrics
│   └── xai/                                   # SHAP feature importance rankings
├── src/
│   ├── descriptors/                           # CDFT & molecular descriptor computation
│   ├── docking/                               # Docking execution & 3D interaction analysis
│   ├── ml_models/                             # QSAR regression & applicability domain scripts
│   ├── quantum/                               # Quantum HSAB & conceptual DFT engine
│   └── visualization/                         # Manuscript & 3D figure rendering pipelines
├── run_entire_study.py                        # Master execution workflow
└── README.md
```

---

## ⚙️ Quickstart & Execution

```bash
git clone https://github.com/sircalch/nano-qsar-ai-therapeutics.git
cd nano-qsar-ai-therapeutics

# Create virtual environment & install requirements
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Execute end-to-end reproducible pipeline
python run_entire_study.py
```

---

## 🗓️ v2.0.0 (2026-09-10)

- **Adsorption recomputed with relaxed complexes**: of 30 modelled organic
  drugs, 25 physisorb and 5 chemisorb on the pristine B36N36 cage (covalent
  B-O/B-N); the three square-planar Pt(II) agents fall outside the GFN2-xTB +
  RDKit build.
- **Docking made reproducible**: `run_real_vina_docking.py` docks the exact
  30-drug master cohort against human PARP1 (PDB 4UND) with a fixed seed and
  writes `vina_4UND_kcal_mol` straight into `dataset_tnbc_bn_pristine.csv`.
  Self-redocking of the co-crystallized ligand does not reproduce the native
  pose within 4 Å, so docking scores are reported only as an exploratory
  ranking.
- Neither descriptor-based QSPR endpoint (RidgeCV, leak-free nested 5x5 CV) is
  predictive (Q2_CV near zero for both the Vina docking score and the
  physisorption interaction energy); the model-free chemisorption/
  physisorption outcome is the robust result of this exploratory study.
- `run_entire_study.py` verified end-to-end; every manuscript statistic is
  computed from the pipeline, none from an empirical formula.

---

## 📜 Citation

```bibtex
@article{MonrealHernandez2026_TNBC_NanoQSAR,
  title={Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages},
  author={Monreal Hern{\'a}ndez, Andr{\'e}s and Franco Amaya, Sara Lizbeth and Mart{\'i}nez Osorio, Carlos Ivanhoe},
  journal={Beilstein Journal of Nanotechnology / Submitted},
  year={2026},
  version={2.0.0},
  doi={10.5281/zenodo.22187873},
  url={https://github.com/sircalch/nano-qsar-ai-therapeutics}
}
```

## 📄 License
Released under the [MIT License](LICENSE).
