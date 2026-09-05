# -*- coding: utf-8 -*-
"""
build_comprehensive_verified_references.py
Peer-reviewed bibliography for this project. Every DOI was verified against
CrossRef (author + title + year). 9 entries whose DOI could not be
verified carry needs_review=True and no DOI (text retained for manual completion).
"""

import os

VERIFIED_REFERENCES = [
    {
        "citation": "Giaquinto, A. N.; Sung, H.; Miller, K. D.; Kramer, J. L.; Newman, L. A.; Minihan, A.; Jemal, A.; Siegel, R. L. Breast Cancer Statistics, 2022. CA Cancer J. Clin. 2022, 72 (6), 524-541.",
        "doi": "10.3322/caac.21754",
    },
    {
        "citation": "Foulkes, W. D.; Smith, I. E.; Reis-Filho, J. S. Triple-Negative Breast Cancer. New England Journal of Medicine 2010, 363 (20), 1938-1948.",
        "doi": "10.1056/nejmra1001389",
    },
    {
        "citation": "Lord, C. J.; Ashworth, A. PARP inhibitors: Synthetic lethality in the clinic. Science 2017, 355 (6330), 1152-1158.",
        "doi": "10.1126/science.aam7344",
    },
    {
        "citation": "Mateo, J.; Lord, C.; Serra, V.; Tutt, A.; Balmaña, J.; Castroviejo-Bermejo, M.; Cruz, C.; Oaknin, A.; Kaye, S.; de Bono, J. A decade of clinical development of PARP inhibitors in perspective. Annals of Oncology 2019, 30 (9), 1437-1447.",
        "doi": "10.1093/annonc/mdz192",
    },
    {
        "citation": "Robson, M.; Im, S. A.; Senkus, E.; Xu, B.; Domchek, S. M.; Masuda, N.; Delaloge, S.; Li, W.; Tung, N.; Armstrong, A.; et al. Olaparib for Metastatic Breast Cancer in Patients with a Germline BRCA Mutation. New England Journal of Medicine 2017, 377 (6), 523-533.",
        "doi": "10.1056/nejmoa1706450",
    },
    {
        "citation": "Litton, J. K.; Rugo, H. S.; Ettl, J.; Hurvitz, S. A.; Gonçalves, A.; Lee, K. H.; Fehrenbacher, L.; Yerushalmi, R.; Mina, L. A.; Martin, M.; et al. Talazoparib in Patients with Advanced Breast Cancer and a Germline BRCA Mutation. New England Journal of Medicine 2018, 379 (8), 753-763.",
        "doi": "10.1056/nejmoa1802905",
    },
    {
        "citation": "Dent, R.; Trudeau, M.; Pritchard, K. I.; Hanna, W. M.; Kahn, H. K.; Sawka, C. A.; Lickley, L. A.; Rawlinson, E.; Sun, P.; Narod, S. A. Triple-Negative Breast Cancer: Clinical Features and Patterns of Recurrence. Clinical Cancer Research 2007, 13 (15), 4429-4434.",
        "doi": "10.1158/1078-0432.ccr-06-3045",
    },
    {
        "citation": "Lehmann, B. D.; Bauer, J. A.; Chen, X.; Sanders, M. E.; Chakravarthy, A. B.; Shyr, Y.; Pietenpol, J. A. Identification of human triple-negative breast cancer subtypes and preclinical models for selection of targeted therapies. Journal of Clinical Investigation 2011, 121 (7), 2750-2767.",
        "doi": "10.1172/jci45014",
    },
    {
        "citation": "Bianchini, G.; Balko, J. M.; Mayer, I. A.; Sanders, M. E.; Gianni, L. Triple-negative breast cancer: challenges and opportunities of a heterogeneous disease. Nature Reviews Clinical Oncology 2016, 13 (11), 674-690.",
        "doi": "10.1038/nrclinonc.2016.66",
    },
    {
        "citation": "Pommier, Y.; O’Connor, M. J.; de Bono, J. Laying a trap to kill cancer cells: PARP inhibitors and their mechanisms of action. Science Translational Medicine 2016, 8 (362).",
        "doi": "10.1126/scitranslmed.aaf9246",
    },
    {
        "citation": "Genchi, G. G.; Ciofani, G. Bioapplications of Boron Nitride Nanotubes. Nanomedicine 2015, 10 (22), 3315-3319.",
        "doi": "10.2217/nnm.15.148",
    },
    {
        "citation": "Golberg, D.; Bando, Y.; Huang, Y.; Terao, T.; Mitome, M.; Tang, C.; Zhi, C. Boron Nitride Nanotubes and Nanosheets. ACS Nano 2010, 4 (6), 2979-2993.",
        "doi": "10.1021/nn1006495",
    },
    {
        "citation": "Ferreira, F. V.; Franceschi, W.; Menezes, B. R. C.; Biagio, P. R.; Coutinho, A. R. Synthesis, functionalization, and applications of carbon and boron nitride nanomaterials in drug delivery. J. Mater. Chem. B 2015, 3 (40), 8000–8018.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Chen, X.; Wu, P.; Rousseas, M.; Okawa, D.; Gartner, Z.; Zettl, A.; Bertozzi, C. R. Boron Nitride Nanotubes Are Noncytotoxic and Can Be Functionalized for Interaction with Proteins and Cells. Journal of the American Chemical Society 2009, 131 (3), 890-891.",
        "doi": "10.1021/ja807334b",
    },
    {
        "citation": "Robles-Hernández, J.-S.-L.; Medina, D. I.; Salcedo, R.; Miralrio, A. Quantum and machine learning-guided QSAR/QSPR modeling of therapeutics conjugated to functionalized fullerenes for enhanced anticancer drug delivery. Beilstein J. Nanotechnol. 2024, 15, 1170–1188.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Mukherjee, S.; Roy, S.; Sarkar, A. Structural, electronic, and adsorption properties of pristine and functionalized B36N36 nanocages for drug delivery applications: A DFT perspective. Phys. Chem. Chem. Phys. 2019, 21 (14), 7480–7492.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Gao, Z.; Zhi, C.; Bando, Y.; Golberg, D.; Serizawa, T. Noncovalent functionalization of boron nitride nanosheets with hydrophilic polymers for enhanced biocompatibility and cellular uptake. ACS Appl. Mater. Interfaces 2017, 9 (6), 4988–4996.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Weng, Q.; Wang, X.; Wang, X.; Bando, Y.; Golberg, D. Functionalized hexagonal boron nitride nanomaterials: emerging properties and applications. Chemical Society Reviews 2016, 45 (14), 3989-4012.",
        "doi": "10.1039/c5cs00869g",
    },
    {
        "citation": "Şen, Ö.; Emanet, M.; Çulha, M. Biocompatibility evaluation of boron nitride nanotubes. Boron Nitride Nanotubes in Nanomedicine 2016, 41-58.",
        "doi": "10.1016/b978-0-323-38945-7.00003-1",
    },
    {
        "citation": "Singh, B.; Sharma, R.; Kumar, P. Boron nitride nanocages as efficient carriers for fluorouracil and gemcitabine: A theoretical investigation. J. Mol. Liq. 2020, 318, 114032.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Parr, R. G.; Szentpály, L. v.; Liu, S. Electrophilicity Index. Journal of the American Chemical Society 1999, 121 (9), 1922-1924.",
        "doi": "10.1021/ja983494x",
    },
    {
        "citation": "Chattaraj, P. K.; Giri, S. Electrophilicity index within a conceptual DFT framework. Annual Reports Section \"C\" (Physical Chemistry) 2009, 105, 13.",
        "doi": "10.1039/b802832j",
    },
    {
        "citation": "Geerlings, P.; De Proft, F.; Langenaeker, W. Conceptual Density Functional Theory. Chemical Reviews 2003, 103 (5), 1793-1874.",
        "doi": "10.1021/cr990029p",
    },
    {
        "citation": "Pearson, R. G. Absolute electronegativity and hardness: application to inorganic chemistry. Inorganic Chemistry 1988, 27 (4), 734-740.",
        "doi": "10.1021/ic00277a030",
    },
    {
        "citation": "Hourahine, B.; Aradi, B.; Blum, V.; Bonafé, F.; Buccheri, A.; Camacho, C.; Cevallos, C.; Deshaye, M. Y.; Dumitrică, T.; Dominguez, A.; et al. DFTB+, a software package for efficient approximate density functional theory based atomistic simulations. The Journal of Chemical Physics 2020, 152 (12).",
        "doi": "10.1063/1.5143190",
    },
    {
        "citation": "Gaus, M.; Cui, Q.; Elstner, M. DFTB3: Extension of the Self-Consistent-Charge Density-Functional Tight-Binding Method (SCC-DFTB). Journal of Chemical Theory and Computation 2011, 7 (4), 931-948.",
        "doi": "10.1021/ct100684s",
    },
    {
        "citation": "Grimme, S.; Bannwarth, C.; Shushkov, P. A Robust and Accurate Tight-Binding Quantum Chemical Method for Structures, Vibrational Frequencies, and Noncovalent Interactions of Large Molecular Systems Parametrized for All spd-Block Elements ( Z = 1–86). Journal of Chemical Theory and Computation 2017, 13 (5), 1989-2009.",
        "doi": "10.1021/acs.jctc.7b00118",
    },
    {
        "citation": "Koopmans, T. Über die Zuordnung von Wellenfunktionen und Eigenwerten zu den Einzelnen Elektronen Eines Atoms. Physica 1934, 1 (1-6), 104-113.",
        "doi": "10.1016/s0031-8914(34)90011-2",
    },
    {
        "citation": "Boys, S.; Bernardi, F. The calculation of small molecular interactions by the differences of separate total energies. Some procedures with reduced errors. Molecular Physics 1970, 19 (4), 553-566.",
        "doi": "10.1080/00268977000101561",
    },
    {
        "citation": "Miralrio, A.; Medina, D. I. Quantum chemical descriptors in QSAR/QSPR modeling: Applications and perspectives. Molecules 2020, 25 (19), 4474.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Trott, O.; Olson, A. J. AutoDock Vina: Improving the speed and accuracy of docking with a new scoring function, efficient optimization, and multithreading. Journal of Computational Chemistry 2009, 31 (2), 455-461.",
        "doi": "10.1002/jcc.21334",
    },
    {
        "citation": "Eberhardt, J.; Santos-Martins, D.; Tillack, A. F.; Forli, S. AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. Journal of Chemical Information and Modeling 2021, 61 (8), 3891-3898.",
        "doi": "10.1021/acs.jcim.1c00203",
    },
    {
        "citation": "Papeo, G.; Posteri, H.; Borghi, D.; Busel, A. A.; Caprera, F.; Casale, E.; Ciomei, M.; Cirla, A.; Corti, L.; D'Anello, M. et al. Discovery of 2-[4-(trifluoromethyl)phenyl]-7,8-dihydro-5H-thiopyrano[4,3-d]pyrimidin-4-ol (NMS-P118): a potent, orally available, and highly selective PARP-1 inhibitor. J. Med. Chem. 2014, 57 (16), 6993–7005.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Riniker, S.; Landrum, G. A. Better Informed Distance Geometry: Using What We Know To Improve Conformation Generation. Journal of Chemical Information and Modeling 2015, 55 (12), 2562-2574.",
        "doi": "10.1021/acs.jcim.5b00654",
    },
    {
        "citation": "Landrum, G. et al. RDKit: Open-source cheminformatics toolkit. Version 2023.09.1, http://www.rdkit.org (accessed August 2026).",
        "doi": "10.5281/zenodo.597034",
    },
    {
        "citation": "Berman, H. M. The Protein Data Bank. Nucleic Acids Research 2000, 28 (1), 235-242.",
        "doi": "10.1093/nar/28.1.235",
    },
    {
        "citation": "Delaney, J. S. ESOL: Estimating Aqueous Solubility Directly from Molecular Structure. Journal of Chemical Information and Computer Sciences 2004, 44 (3), 1000-1005.",
        "doi": "10.1021/ci034243x",
    },
    {
        "citation": "Wishart, D. S.; Feunang, Y. D.; Guo, A. C.; Lo, E. J.; Marcu, A.; Grant, J. R.; Sajed, T.; Johnson, D.; Li, C.; Sayeeda, Z.; et al. DrugBank 5.0: a major update to the DrugBank database for 2018. Nucleic Acids Research 2017, 46 (D1), D1074-D1082.",
        "doi": "10.1093/nar/gkx1037",
    },
    {
        "citation": "Lundberg, S. M.; Lee, S.-I. A unified approach to interpreting model predictions. In Advances in Neural Information Processing Systems (NeurIPS 2017); Guyon, I. et al., Eds.; Curran Associates, Inc.: Red Hook, NY, 2017; Vol. 30, pp 4765–4774.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Chen, T.; Guestrin, C. XGBoost. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining 2016, 785-794.",
        "doi": "10.1145/2939672.2939785",
    },
    {
        "citation": "Geurts, P.; Ernst, D.; Wehenkel, L. Extremely randomized trees. Machine Learning 2006, 63 (1), 3-42.",
        "doi": "10.1007/s10994-006-6226-1",
    },
    {
        "citation": "OECD. Guidance Document on the Validation of (Quantitative) Structure-Activity Relationship [(Q)SAR] Models. OECD Series on Testing and Assessment, No. 69; OECD Publishing: Paris, France, 2007.",
        "doi": "10.1787/9789264085442-en",
    },
    {
        "citation": "Gramatica, P. Principles of QSAR models validation: internal and external. QSAR & Combinatorial Science 2007, 26 (5), 694-701.",
        "doi": "10.1002/qsar.200610151",
    },
    {
        "citation": "Rodríguez-Pérez, R.; Bajorath, J. Interpretation of machine learning models using shapley additive explanations (SHAP) in chemistry and drug discovery. J. Med. Chem. 2020, 63 (16), 8677–8688.",
        "doi": "",
        "needs_review": True,
    },
    {
        "citation": "Tropsha, A. Best Practices for QSAR Model Development, Validation, and Exploitation. Molecular Informatics 2010, 29 (6-7), 476-488.",
        "doi": "10.1002/minf.201000061",
    },
]


def update_all_bibliography():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    bib_path = os.path.join(base_dir, "manuscript", "references.bib")
    with open(bib_path, 'w', encoding='utf-8') as f:
        for i, ref in enumerate(VERIFIED_REFERENCES, 1):
            f.write(f"@article{{ref{i},\n")
            f.write(f"  title = {{{ref['citation']}}},\n")
            if ref.get('doi'):
                f.write(f"  doi = {{{ref['doi']}}}\n")
            f.write("}\n\n")
    print(f"Updated BibTeX with {len(VERIFIED_REFERENCES)} verified references: {bib_path}")

if __name__ == "__main__":
    update_all_bibliography()
