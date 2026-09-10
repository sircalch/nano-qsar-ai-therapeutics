# Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Loading on 2D Nanomaterials

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

Triple-negative breast cancer (TNBC) lacks estrogen (ER), progesterone (PR), and HER2 receptor expression, presenting aggressive metastatic phenotypes, profound clonal heterogeneity, and poor overall prognosis. Targeted delivery via **two-dimensional (2D) inorganic nanocarriers** (such as hexagonal Boron Nitride, $B_{36}N_{36}$, and functionalized graphene) offers high drug payloads and tunable release profiles. In this work, we present an end-to-end multi-scale computational framework integrating:

### Methodological Highlights:
- **Macromolecular Target**: High-resolution crystallographic structure of human Poly(ADP-ribose) Polymerase 1 (PARP1 catalytic domain, PDB ID: 4UND co-crystallized with Olaparib).
- **Curated TNBC Drug Cohort**: 40 clinical therapeutics spanning PARP inhibitors, platinum coordination complexes, topoisomerase inhibitors, antimetabolites, and antibody-drug conjugate (ADC) payloads.
- **Quantum Conceptual DFT & HSAB Theory**: Hard and Soft Acids and Bases (HSAB) descriptors ($\eta, S, \mu, \omega, \Delta N_{\text{max}}$) evaluating electronic charge transfer and adsorption on pristine and carboxyl-functionalized $B_{36}N_{36}\text{-COOH}$ and graphene nanosheets.
- **Explainable Machine Learning (Nano-QSAR / XAI)**: Multi-model regression (Random Forest, Gradient Boosting, Extra Trees, Ridge, SVR) with nested cross-validation and OECD Principle 3 applicability domain (Williams plot).
- **Global & Local SHAP Interpretability**: Quantifying feature contributions of polar surface area (PSA), frontier orbital eigenvalues, and molecular polarizability to non-covalent adsorption stabilization.

---

## 🔬 Repository Architecture

```
├── data/
│   ├── processed/                             # Processed datasets and descriptor matrices
│   └── raw/                                   # PDB 4UND receptor and 40 ligand PDBQT coordinates
├── figures/                                   # High-resolution publication figures (300 DPI)
├── manuscript/
│   ├── Beilstein_Manuscript_Monreal_Hernandez_et_al.docx
│   └── submission_ready/                      # Formatted submission package & cover letter
├── results/
│   ├── docking/                               # Real Vina binding scores, residue contacts & PyMOL sessions
│   ├── models/                                # QSAR benchmark summaries and metrics
│   └── xai/                                   # SHAP feature importance rankings across nanocarriers
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
  drugs, 25 physisorb and 5 chemisorb on B36N36 (covalent B-O/B-N); the three
  square-planar Pt(II) agents fall outside the GFN2-xTB + RDKit build.
- **Docking made reproducible**: `run_real_vina_docking.py` docks the exact
  30-drug master cohort against human PARP1 (PDB 4UND) with a fixed seed and
  writes `vina_4UND_kcal_mol` straight into `dataset_tnbc_bn_pristine.csv`.
- Neither descriptor QSPR endpoint is predictive (Vina Q2_CV = -0.33,
  physisorption 0.00); the model-free chemisorption/physisorption outcome is the
  robust result.
- `run_entire_study.py` verified end-to-end (10/10 steps); every manuscript
  statistic is computed from the pipeline, none from an empirical formula.

---

## 📜 Citation

```bibtex
@article{MonrealHernandez2026_TNBC_NanoQSAR,
  title={Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Loading on 2D Nanomaterials},
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
