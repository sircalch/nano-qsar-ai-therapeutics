# Supporting Information: Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages

**Andrés Monreal Hernández$^{1,*}$, Sara Lizbeth Franco Amaya$^{2}$, Carlos Ivanhoe Martínez Osorio$^{3}$**

$^{1}$ Universidad Estatal de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0009-1207-8597](https://orcid.org/0009-0009-1207-8597)  
$^{2}$ Doctorado en Nanotecnología, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0005-0272-0241](https://orcid.org/0009-0005-0272-0241)  
$^{3}$ Doctorado en Ciencia de Materiales, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0003-7872-4965](https://orcid.org/0009-0003-7872-4965)  
$^*$ Corresponding Author Email: `andres.monreal@ues.mx`

---

## Table of Contents
- **Table S1.** Curated Library of 42 Anti-TNBC Therapeutic Agents and Computed Constitutional Descriptors.
- **Table S2.** Quantum Chemical and Conceptual DFT (CDFT) Reactivity Parameters for Isolated and BN-Complexed Drugs.
- **Table S3.** Molecular Docking Scores (kcal/mol), Hydrogen Bonds, and Residue Interaction Profiles against PARP1.
- **Table S4.** Five-Fold Cross-Validation Metrics across Machine Learning and MLR Models.
- **Table S5.** External Validation Set Observed vs. Predicted Docking Scores.

---

### Table S1. Curated Library of 42 Anti-TNBC Therapeutic Agents
*(Sample excerpt of representative entries across structural classes)*

| Drug Name | Class | DrugBank ID | MW (g/mol) | LogP | LogS | PSA (Å$^2$) | HBA | HBD | RBC | NOR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Olaparib** | PARP Inhibitor | DB00140 | 434.46 | 1.87 | -3.85 | 60.16 | 4 | 1 | 4 | 5 |
| **Talazoparib** | PARP Inhibitor | DB11760 | 380.35 | 2.45 | -4.10 | 66.88 | 4 | 2 | 2 | 4 |
| **Rucaparib** | PARP Inhibitor | DB12331 | 323.36 | 2.21 | -3.65 | 50.16 | 3 | 2 | 4 | 4 |
| **Niraparib** | PARP Inhibitor | DB12340 | 320.40 | 2.85 | -3.90 | 58.12 | 3 | 2 | 3 | 3 |
| **Cisplatin** | Platinum Agent | DB00515 | 300.05 | -2.10 | -1.80 | 52.00 | 2 | 2 | 0 | 0 |
| **Carboplatin** | Platinum Agent | DB00958 | 371.25 | -1.60 | -2.10 | 78.50 | 4 | 2 | 0 | 2 |
| **Doxorubicin** | Anthracycline | DB00997 | 543.52 | 1.27 | -3.42 | 206.07 | 12 | 6 | 5 | 5 |
| **Epirubicin** | Anthracycline | DB00445 | 543.52 | 1.27 | -3.42 | 206.07 | 12 | 6 | 5 | 5 |
| **Topotecan** | Topo I Inhibitor | DB01030 | 421.45 | 1.15 | -3.18 | 97.43 | 6 | 2 | 3 | 5 |
| **Gemcitabine** | Antimetabolite | DB00441 | 263.20 | -1.40 | -1.95 | 110.83 | 6 | 4 | 2 | 2 |
| **Paclitaxel** | Taxane | DB01204 | 853.91 | 3.96 | -5.85 | 221.29 | 14 | 4 | 14 | 7 |
| **Docetaxel** | Taxane | DB01248 | 807.88 | 3.20 | -5.40 | 227.32 | 14 | 5 | 13 | 7 |
| **Lapatinib** | Kinase Inhibitor | DB01259 | 581.06 | 5.12 | -6.20 | 113.85 | 7 | 2 | 10 | 5 |
| **Palbociclib** | CDK4/6 Inhibitor | DB09073 | 447.53 | 2.70 | -4.05 | 87.65 | 7 | 2 | 4 | 4 |
| **SN-38** | ADC Payload | DB05482 | 392.40 | 2.10 | -3.75 | 94.45 | 5 | 2 | 2 | 5 |
| **MMAE** | ADC Payload | DB06161 | 717.98 | 2.80 | -4.95 | 185.40 | 9 | 4 | 20 | 2 |

---

### Table S2. Conceptual DFT (CDFT) Electronic Reactivity Parameters

| System | Mean $E_{HOMO}$ (eV) | Mean $E_{LUMO}$ (eV) | Mean $\Delta E_g$ (eV) | Mean $\eta$ (eV) | Mean $\omega$ (eV) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Isolated Drugs** | $-5.88 \pm 0.32$ | $-2.35 \pm 0.38$ | $3.53 \pm 0.45$ | $1.76 \pm 0.22$ | $4.85 \pm 0.85$ |
| **Drug + $B_{36}N_{36}$ Pristine** | $-5.92 \pm 0.21$ | $-2.98 \pm 0.18$ | $2.94 \pm 0.25$ | $1.47 \pm 0.12$ | $6.75 \pm 0.72$ |
| **Drug + $B_{36}N_{36}\text{-COOH}$** | $-5.75 \pm 0.20$ | $-3.15 \pm 0.19$ | $2.60 \pm 0.22$ | $1.30 \pm 0.11$ | $7.65 \pm 0.68$ |

---

### Table S3. Molecular Docking Summary against PARP1

| System | Mean Docking Score (kcal/mol) | Score Range (kcal/mol) | Mean H-Bonds | Primary Receptor Binding Zone |
| :--- | :---: | :---: | :---: | :--- |
| **Isolated Drugs** | $-10.14 \pm 1.25$ | $-12.50$ to $-7.16$ | $2.6 \pm 1.4$ | Inner Catalytic Pocket (Gly863, Tyr907, Glu988) |
| **Drug + $B_{36}N_{36}$ Pristine** | $-13.45 \pm 1.18$ | $-15.20$ to $-9.62$ | $1.1 \pm 0.8$ | Outer Regulatory Cleft (Tyr896, Phe897, Leu877) |
| **Drug + $B_{36}N_{36}\text{-COOH}$** | $-14.01 \pm 0.95$ | $-14.60$ to $-10.35$ | $3.4 \pm 1.1$ | Polar Surface Grooves (Lys703, Arg878, Lys903) |

---

### Table S4. Five-Fold Cross-Validation Model Metrics

| System | Algorithm | CV Mean MAPE (%) | CV MAPE Std (%) | Test MAPE (%) | Test $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Isolated Drugs** | ExtraTrees | 5.82% | $\pm 0.94\%$ | 4.33% | 0.8659 |
| | MLR | 8.42% | $\pm 1.35\%$ | 11.26% | 0.2752 |
| **Drug + $B_{36}N_{36}$ Pristine** | ExtraTrees | 5.48% | $\pm 0.88\%$ | 4.54% | 0.8321 |
| | MLR | 7.89% | $\pm 1.20\%$ | 10.52% | -0.0491 |
| **Drug + $B_{36}N_{36}\text{-COOH}$** | ExtraTrees | 4.12% | $\pm 0.76\%$ | 3.14% | 0.8130 |
| | MLR | 5.92% | $\pm 0.95\%$ | 7.06% | 0.1866 |

---

### Table S5. External Validation Set (20% Split, $N=8$)

| Compound | System | Observed Score (kcal/mol) | ExtraTrees Pred (kcal/mol) | MLR Pred (kcal/mol) | Residual (ET) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Talazoparib** | Isolated | -12.45 | -12.18 | -11.90 | +0.27 |
| **Topotecan** | Isolated | -9.85 | -9.62 | -9.20 | +0.23 |
| **Docetaxel** | Isolated | -10.90 | -11.15 | -10.45 | -0.25 |
| **Capivasertib** | Isolated | -9.50 | -9.32 | -9.80 | +0.18 |
| **Talazoparib** | + $B_{36}N_{36}$ | -15.10 | -14.75 | -14.20 | +0.35 |
| **Topotecan** | + $B_{36}N_{36}$ | -13.20 | -12.95 | -12.50 | +0.25 |
| **Talazoparib** | + $B_{36}N_{36}\text{-COOH}$ | -14.60 | -14.38 | -14.15 | +0.22 |
| **Topotecan** | + $B_{36}N_{36}\text{-COOH}$ | -13.90 | -13.65 | -13.40 | +0.25 |
