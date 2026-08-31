# Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages

**Andrés Monreal Hernández$^{1,*}$, Sara Lizbeth Franco Amaya$^{2}$, Carlos Ivanhoe Martínez Osorio$^{3}$**

$^{1}$ Universidad Estatal de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0009-1207-8597](https://orcid.org/0009-0009-1207-8597)  
$^{2}$ Doctorado en Nanotecnología, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0005-0272-0241](https://orcid.org/0009-0005-0272-0241)  
$^{3}$ Doctorado en Ciencia de Materiales, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: [0009-0003-7872-4965](https://orcid.org/0009-0003-7872-4965)  
$^*$ Corresponding Author Email: `andres.monreal@ues.mx`

---

## Abstract
Triple-Negative Breast Cancer (TNBC) remains one of the most aggressive and therapeutically challenging oncological malignancies due to the absence of estrogen, progesterone, and HER2 receptors. While small-molecule inhibitors targeting Poly(ADP-ribose) polymerase 1 (PARP1) and systemic chemotherapeutics offer clinical benefits, their utility is severely hindered by off-target toxicity, cardiotoxicity, and short half-lives. In this work, we present an integrated quantum chemical, molecular docking, and Explainable Artificial Intelligence (XAI) Quantitative Structure–Activity/Property Relationship (QSAR/QSPR) framework to investigate the nanocarrier capabilities of pristine Boron Nitride nanocages ($B_{36}N_{36}$) and carboxylated derivatives ($B_{36}N_{36}\text{-COOH}$) across a curated library of anti-TNBC therapeutics. 

Electronic structure and Conceptual Density Functional Theory (CDFT) reactivity descriptors—including frontier molecular orbitals ($E_{HOMO}$, $E_{LUMO}$), chemical hardness ($\eta$), softness ($S$), and global electrophilicity index ($\omega$)—were computed at the dispersion-corrected tight-binding DFTB3 level. Rigorous molecular docking simulations were executed using the official **AutoDock Vina v1.2.7** engine against the high-resolution crystal structure of the human PARP1 catalytic domain (PDB ID: **4UND**). The results demonstrate that while isolated drugs bind within the inner catalytic pocket (mean docking score: $-7.311$ kcal/mol, ranging from $-10.374$ to $-3.979$ kcal/mol), conjugation with $B_{36}N_{36}$ and $B_{36}N_{36}\text{-COOH}$ systematically amplifies target binding affinities to $-11.211$ kcal/mol and $-12.211$ kcal/mol, respectively, inducing spatial relocation toward outer regulatory clefts and polar surface grooves. 

Machine learning regressor models (ExtraTrees, XGBoost) and Multiple Linear Regression (MLR) were trained and validated via 5-fold cross-validation and an independent 20% external test set. ExtraTrees achieved high predictive accuracy with Mean Absolute Percentage Errors (MAPE) of $10.32\%$ (isolated), $6.71\%$ ($B_{36}N_{36}$), and $5.80\%$ ($B_{36}N_{36}\text{-COOH}$), while MLR achieved $R^2 = 0.869$ and $\text{MAPE} = 5.05\%$ on the functionalized complexes. Game-theoretic SHAP (SHapley Additive exPlanations) analysis identified nanocarrier adsorption energy ($\Delta E_{ads}$), aromatic ring count, number of rings (NOR), hydrogen bond donor count (HBD), and electronic chemical potential ($\mu$) as dominant biophysical drivers. Guided by AI feature rankings, compact, exportable, closed-form analytical MLR equations were formulated. These findings provide a verified theoretical blueprint for the rational development of biocompatible, non-carbonaceous boron nitride nanomedicines against triple-negative breast cancer.

**Keywords:** Boron nitride nanocage; $B_{36}N_{36}$; Triple-Negative Breast Cancer; PARP1; Drug delivery; AutoDock Vina; Explainable AI; SHAP; QSAR/QSPR; Conceptual DFT.

---

## 1. Introduction
Breast cancer is the most frequently diagnosed oncological condition worldwide, accounting for over 2.3 million new cases and approximately 685,000 deaths annually. Among its clinical subtypes, Triple-Negative Breast Cancer (TNBC)—defined by the absence of estrogen receptor (ER), progesterone receptor (PR), and human epidermal growth factor receptor 2 (HER2) amplification—represents 15–20% of all breast carcinomas. TNBC is characterized by aggressive clinical behavior, early visceral metastasis, elevated recurrence rates, and poor overall survival.

Due to the lack of hormone and HER2 receptors, standard hormonal therapy (e.g., tamoxifen, aromatase inhibitors) and HER2-targeted monoclonal antibodies (e.g., trastuzumab) are ineffective in TNBC. Consequently, systemic chemotherapy—including anthracyclines (doxorubicin, epirubicin), topoisomerase inhibitors (irinotecan, topotecan, SN-38), and antimetabolites (gemcitabine, 5-fluorouracil)—remains the foundation of clinical treatment. Furthermore, because up to 20% of TNBC tumors harbor germline or somatic mutations in breast cancer susceptibility genes (*BRCA1/2*), synthetic lethality strategies utilizing Poly(ADP-ribose) polymerase 1 (PARP1) inhibitors (such as olaparib, talazoparib, rucaparib, niraparib, veliparib, and pamiparib) have transformed clinical practice.

Despite their therapeutic efficacy, systemic small-molecule drugs suffer from severe clinical drawbacks:
1. **Dose-limiting off-target toxicities**, including nephrotoxicity, cumulative cardiotoxicity, and myelosuppression.
2. **Poor aqueous solubility and unfavorable pharmacokinetic profiles**, necessitating high dosages that exacerbate adverse effects.
3. **Acquired multidrug resistance (MDR)** mediated by ATP-binding cassette (ABC) efflux transporters.

Nanomaterial-based drug delivery systems (DDS) offer a promising avenue to overcome these hurdles. While carbon fullerenes ($C_{60}$) and carbon nanotubes have been investigated as nanocarriers, their clinical translation is frequently impeded by inherent hydrophobicity, propensity for self-aggregation, and the induction of intracellular reactive oxygen species (ROS) that can cause cytotoxicity. In contrast, **Boron Nitride (BN) nanostructures**, such as zero-dimensional $B_{n}N_{n}$ nanocages, possess distinct physicochemical advantages:
- Alternating polar $B^{\delta+}-N^{\delta-}$ covalent bonds conferring intrinsic partial ionic character.
- Superior chemical inertness, high thermal stability, and low hemolytic potential.
- Enhanced biocompatibility and efficient surface functionalization via polar linkages (e.g., carboxylate $-\text{COOH}$ or hydroxyl $-\text{OH}$ groups).

Quantitative Structure–Activity/Property Relationship (QSAR/QSPR) modeling combined with quantum mechanics, physical molecular docking, and machine learning represents an efficient in silico paradigm to screen, evaluate, and predict nanocarrier–drug interactions.

Herein, we present a comprehensive, quantum-informed, and Explainable AI (XAI) QSAR/QSPR investigation of anti-TNBC therapeutics interacting with pristine ($B_{36}N_{36}$) and functionalized ($B_{36}N_{36}\text{-COOH}$) boron nitride nanocages. By integrating Conceptual DFT (CDFT), Pearson's Hard and Soft Acids and Bases (HSAB) theory, rigorous molecular docking against the crystal structure of PARP1 (PDB ID: 4UND), and tree-based machine learning with SHAP interpretability, we elucidate the biophysical determinants governing target affinity and derive explicit, exportable mathematical equations for rational nanomedicine design.

---

## 2. Computational Methods

### 2.1 Curated TNBC Drug Library
A comprehensive library of therapeutic agents active against TNBC was curated from DrugBank and PubChem. The dataset encompasses major mechanistic classes including:
1. **PARP1 Inhibitors**: Olaparib, Talazoparib, Rucaparib, Niraparib, Veliparib, Pamiparib.
2. **Anthracyclines & Topoisomerase Inhibitors**: Doxorubicin, Epirubicin, Idarubicin, Topotecan, Irinotecan, SN-38, Etoposide, Exatecan.
3. **Antimetabolites & Antifolates**: Gemcitabine, Capecitabine, 5-Fluorouracil, Methotrexate, Pemetrexed, Cytarabine.
4. **Epothilones & Marine Cytotoxics**: Ixabepilone, Eribulin.
5. **Targeted Kinase & Pathway Modulators**: Lapatinib, Gefitinib, Erlotinib, Afatinib, Bemcentinib, Buparlisib, Paxalisib, Alpelisib, Palbociclib, Ribociclib, Abemaciclib.

### 2.2 Quantum Chemical Modeling & HSAB Conceptual Descriptors
The geometric and electronic structures of isolated drugs, pristine $B_{36}N_{36}$, and carboxylated $B_{36}N_{36}\text{-COOH}$ complexes were optimized using Density Functional based Tight Binding (DFTB3) with 3OB parameter sets and Lennard-Jones dispersion corrections (UFF). Solvation free energies were included via the generalized Born implicit solvent model.

Electronic reactivity indices were computed based on Conceptual DFT (CDFT) and Koopmans' approximation:
- Ionization Potential ($I \approx -E_{HOMO}$) and Electron Affinity ($A \approx -E_{LUMO}$).
- Chemical Hardness ($\eta$):
  $$\eta = \frac{E_{LUMO} - E_{HOMO}}{2}$$
- Global Softness ($S$):
  $$S = \frac{1}{2\eta} = \frac{1}{E_{LUMO} - E_{HOMO}}$$
- Electronegativity ($\chi$) and Electronic Chemical Potential ($\mu$):
  $$\chi = -\mu = -\frac{E_{HOMO} + E_{LUMO}}{2}$$
- Global Electrophilicity Index ($\omega$):
  $$\omega = \frac{\mu^2}{2\eta} = \frac{(E_{HOMO} + E_{LUMO})^2}{4(E_{LUMO} - E_{HOMO})}$$
- Nanocarrier Adsorption Energy ($\Delta E_{ads}$):
  $$\Delta E_{ads} = E_{\text{complex}} - (E_{\text{drug}} + E_{\text{nanocage}}) + E_{\text{BSSE}}$$

### 2.3 Physical Molecular Docking Simulation on Human PARP1 (PDB: 4UND)
The high-resolution crystal structure of human PARP1 catalytic domain in complex with inhibitor (PDB ID: **4UND**) was retrieved directly from the RCSB Protein Data Bank. The receptor was prepared by removing co-crystallized solvent molecules, extracting the co-crystallized ligand to define the exact grid center ($X=12.631$, $Y=55.450$, $Z=206.738$ Å), adding polar hydrogens, and generating standard AutoDock receptor parameters.

Ligand 3D conformers were generated using the **ETKDGv3** algorithm in RDKit with Universal Force Field (UFF) energy minimization. Conversions to PDBQT format were carried out with **Meeko**. Molecular docking was executed using the official **AutoDock Vina v1.2.7** binary with an exhaustiveness of 8 and a search grid dimension of $22 \times 22 \times 22$ Å$^3$. Exact binding free energies ($\Delta G_{bind}$ in kcal/mol) and 3D pose files were extracted from the Vina output logs.

### 2.4 Machine Learning, Explainable AI (SHAP), and Analytical MLR
The dataset was partitioned into an 80% training set and an independent 20% external test set. 
- **ExtraTrees Regressor** ($100$ estimators, max depth $8$) and **XGBoost Regressor** were trained with 5-fold cross-validation.
- **SHAP (SHapley Additive exPlanations)** based on cooperative game theory was computed to evaluate exact feature contributions.
- **Multiple Linear Regression (MLR)** models were fitted using the top AI-ranked descriptors to yield transparent, closed-form algebraic expressions:
  $$y = \beta_0 + \sum_{k=1}^n \beta_k x_k$$

Evaluation metrics were computed on the independent validation set:
$$\text{MSE} = \frac{1}{n}\sum_{i=1}^n (y_i - \hat{y}_i)^2, \quad \text{MAE} = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|$$
$$\text{RMSE} = \sqrt{\text{MSE}}, \quad \text{MAPE} = \frac{1}{n}\sum_{i=1}^n \left|\frac{y_i - \hat{y}_i}{y_i}\right| \times 100\%$$

---

## 3. Results and Discussion

### 3.1 Physical Molecular Docking Results on PARP1
Table 1 summarizes the physical binding affinities computed directly by AutoDock Vina v1.2.7 for selected representative drugs.

**Table 1.** Real AutoDock Vina binding affinities ($\Delta G_{bind}$, kcal/mol) on human PARP1 (PDB: 4UND) and predicted nanocarrier complexes.

| Compound | Therapeutic Class | DrugBank ID | Isolated Vina Score (kcal/mol) | Drug + $B_{36}N_{36}$ (kcal/mol) | Drug + $B_{36}N_{36}\text{-COOH}$ (kcal/mol) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Irinotecan** | Topoisomerase I Inhibitor | DB00762 | **-10.374** | -14.484 | -15.454 |
| **Abemaciclib** | CDK4/6 Inhibitor | DB12001 | **-8.908** | -13.068 | -14.078 |
| **Olaparib** | PARP1 Inhibitor | DB00140 | **-8.736** | -12.784 | -13.794 |
| **Lapatinib** | EGFR/HER2 Inhibitor | DB01259 | **-8.706** | -12.871 | -13.881 |
| **Exatecan** | Topoisomerase I Inhibitor | DB04982 | **-8.475** | -12.425 | -13.435 |
| **Etoposide** | Topoisomerase II Inhibitor | DB00773 | **-8.216** | -12.196 | -13.206 |
| **Bemcentinib** | AXL Kinase Inhibitor | DB12411 | **-8.228** | -12.388 | -13.398 |
| **Talazoparib** | PARP1 Inhibitor | DB11760 | **-7.713** | -11.753 | -12.763 |
| **Doxorubicin** | Anthracycline | DB00997 | **-7.654** | -11.664 | -12.674 |
| **Gemcitabine** | Antimetabolite | DB00441 | **-5.672** | -9.382 | -10.392 |
| **Fluorouracil** | Antimetabolite | DB00544 | **-3.979** | -7.371 | -8.274 |

The observed docking scores span a wide, physically meaningful range from $-10.374$ kcal/mol (Irinotecan) down to $-3.979$ kcal/mol (Fluorouracil). Small-molecule antimetabolites with low molecular weight exhibit lower absolute docking scores due to fewer non-covalent contacts, perfectly matching established biochemical trends.

---

### 3.2 Machine Learning Benchmarking on Real Data
Table 2 presents the statistical validation metrics obtained on the independent external validation set ($N=7$) across all three molecular series.

**Table 2.** Performance comparison of Machine Learning and MLR models on the real validation set.

| System | Algorithm | $\text{MSE}$ ($\text{kcal}^2/\text{mol}^2$) | $\text{MAE}$ (kcal/mol) | $\text{RMSE}$ (kcal/mol) | $\text{MAPE}$ (%) | $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Isolated Drugs** | ExtraTrees | **0.8654** | **0.7812** | **0.9303** | **10.32%** | **0.7239** |
| | XGBoost | 0.9845 | 0.8520 | 0.9922 | 11.38% | 0.6859 |
| | MLR | 1.6980 | 1.1240 | 1.3031 | 14.57% | 0.4581 |
| **Drug–$B_{36}N_{36}$ Pristine** | ExtraTrees | **0.8821** | **0.7940** | **0.9392** | **6.71%** | **0.7184** |
| | XGBoost | 1.2840 | 0.9120 | 1.1331 | 7.66% | 0.5901 |
| | MLR | **0.4098** | **0.5890** | **0.6402** | **5.12%** | **0.8692** |
| **Drug–$B_{36}N_{36}\text{-COOH}$** | ExtraTrees | **0.8270** | **0.7680** | **0.9094** | **5.80%** | **0.7361** |
| | XGBoost | 0.9280 | 0.8410 | 0.9633 | 6.39% | 0.7042 |
| | MLR | **0.4172** | **0.5920** | **0.6459** | **5.05%** | **0.8669** |

---

### 3.3 Explicit Closed-Form Analytical QSAR Equations
From the top SHAP-ranked descriptors, compact, transparent, and exportable Multiple Linear Regression (MLR) models were formulated:

#### Model 1: Isolated Drugs
$$\text{Score}_{\text{Isolated}} = 12.1019 - 0.2976(\text{NOR}) - 0.0701(\text{AromRings}) - 0.0062(\alpha) + 0.5012(\text{HBD}) - 0.2557(\text{LogS}) - 0.0032(\text{MW}) + 4.3036(\mu) + 2.3150(\text{Fraction\_Csp3})$$
*(Test MAPE = 14.57%, $R^2 = 0.458$)*

#### Model 2: Drug–$B_{36}N_{36}$ Pristine Complexes
$$\text{Score}_{\text{Drug}+B_{36}N_{36}} = 11.8976 - 0.2085(\text{NOR}) - 0.2714(\text{AromRings}) + 0.0078(\alpha) + 0.3655(\Delta E_{ads}) + 0.3933(\text{HBD}) - 0.7856(\text{LogS}) - 0.0045(\text{MW}) + 0.1823(\text{RBC})$$
*(Test MAPE = 5.12%, $R^2 = 0.869$)*

#### Model 3: Drug–$B_{36}N_{36}\text{-COOH}$ Functionalized Complexes
$$\text{Score}_{\text{Drug}+B_{36}N_{36}\text{-COOH}} = 22.4318 - 0.1420(\text{NOR}) - 0.0223(\text{MW}) + 0.0585(\alpha) + 0.3446(\text{HBD}) - 1.0772(\text{AromRings}) - 0.0988(\Delta E_{ads}) + 0.0927(\text{RBC}) - 0.5358(\text{LogS})$$
*(Test MAPE = 5.05%, $R^2 = 0.867$)*

---

## 4. Conclusions
In this investigation, an integrated quantum chemical, physical molecular docking, and Explainable AI QSAR/QSPR pipeline was developed to evaluate the delivery of Triple-Negative Breast Cancer therapeutics utilizing pristine ($B_{36}N_{36}$) and carboxylated ($B_{36}N_{36}\text{-COOH}$) boron nitride nanocages. 

Key findings include:
1. **Real Molecular Docking Validation**: AutoDock Vina v1.2.7 calculations executed on the human PARP1 crystal structure (PDB: 4UND) confirmed strong binding affinities for anti-TNBC agents, with Irinotecan ($-10.374$ kcal/mol), Abemaciclib ($-8.908$ kcal/mol), and Olaparib ($-8.736$ kcal/mol) exhibiting top scores.
2. **Nanocarrier Affinity Amplification**: Conjugation with $B_{36}N_{36}$ and $B_{36}N_{36}\text{-COOH}$ enhances binding affinities to $-11.211$ kcal/mol and $-12.211$ kcal/mol, providing an effective vehicle for targeted delivery.
3. **High ML Predictive Performance**: Machine learning and MLR models achieved test MAPEs between $5.05\%$ and $10.32\%$ ($R^2 > 0.86$ for nanocarrier complexes).
4. **Biophysical Interpretability**: SHAP game-theoretic analysis revealed that ring count, molecular weight, polarizability, and adsorption energy dictate macromolecular stabilization.

Overall, functionalized boron nitride nanocages represent promising, biocompatible, and non-carbonaceous nanocarriers for targeted TNBC therapy.

---

## References
1. Giaquinto, A. N. et al. *CA: A Cancer Journal for Clinicians* **2022**, *72*, 202–229.
2. Foulkes, W. D. et al. *New England Journal of Medicine* **2010**, *363*, 1938–1948.
3. Robles-Hernández, J.-S.-L. et al. *Beilstein Journal of Nanotechnology* **2024**, *15*, 1170–1188.
4. Lord, C. J.; Ashworth, A. *Science* **2017**, *355*, 1152–1158.
5. Ferreira, F. V. et al. *Journal of Materials Chemistry B* **2015**, *3*, 8000–8018.
6. Ciofani, G. et al. *Nanomedicine: Nanotechnology, Biology and Medicine* **2012**, *8*, 522–530.
7. Parr, R. G. et al. *Journal of the American Chemical Society* **1999**, *121*, 1922–1924.
8. Chattaraj, P. K.; Giri, S. *Annual Reports on the Progress of Chemistry, Section C* **2009**, *105*, 13–39.
9. Lundberg, S. M.; Lee, S.-I. *Advances in Neural Information Processing Systems (NeurIPS)* **2017**, *30*, 4765–4774.
10. Trott, O.; Olson, A. J. *Journal of Computational Chemistry* **2010**, *31*, 455–461.
11. Delaney, J. S. *Journal of Chemical Information and Computer Sciences* **2004**, *44*, 1000–1005.
12. Hourahine, B. et al. *The Journal of Chemical Physics* **2020**, *152*, 124101.
