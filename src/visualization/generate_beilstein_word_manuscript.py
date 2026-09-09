"""
generate_beilstein_word_manuscript.py
Builds the complete, professionally formatted Microsoft Word (.docx) manuscript
and Supplementary Information following the exact editorial guidelines of the 
Beilstein Journal of Nanotechnology (BJNANO) / Elsevier Q1 journals.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_color):
    """Sets background color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding in twips (1/20 of a pt)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    run = h.runs[0]
    run.font.name = 'Arial'
    if level == 1:
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(13, 71, 161) # Deep Blue
    elif level == 2:
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(21, 101, 192)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(38, 50, 56)
    return h

def build_manuscript_word():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fig_dir = os.path.join(base_dir, "figures")
    out_docx = os.path.join(base_dir, "manuscript", "Beilstein_Manuscript_Monreal_Hernandez_et_al.docx")
    
    doc = Document()
    
    # Page setup: Standard A4 with 2.54 cm (1 in) margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Default style font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(33, 33, 33)
    
    # ==============================================================================
    # TITLE & AUTHOR BLOCK
    # ==============================================================================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    run_title = p_title.add_run("Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(17)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(13, 71, 161)
    
    # Authors
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(6)
    
    r1 = p_auth.add_run("Andrés Monreal Hernández")
    r1.font.bold = True
    p_auth.add_run("1,*, ")
    r2 = p_auth.add_run("Sara Lizbeth Franco Amaya")
    r2.font.bold = True
    p_auth.add_run("2, and ")
    r3 = p_auth.add_run("Carlos Ivanhoe Martínez Osorio")
    r3.font.bold = True
    p_auth.add_run("3")
    
    # Affiliations
    p_aff = doc.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_after = Pt(18)
    
    aff_text = (
        "1 Universidad Estatal de Sonora, Hermosillo, Sonora, Mexico. ORCID: 0009-0009-1207-8597\n"
        "2 Doctorado en Nanotecnología, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: 0009-0005-0272-0241\n"
        "3 Doctorado en Ciencia de Materiales, Universidad de Sonora, Hermosillo, Sonora, Mexico. ORCID: 0009-0003-7872-4965\n"
        "* Corresponding author email: andres.monreal@ues.mx"
    )
    r_aff = p_aff.add_run(aff_text)
    r_aff.font.size = Pt(9.5)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(97, 97, 97)
    
    # ==============================================================================
    # ABSTRACT & KEYWORDS
    # ==============================================================================
    p_abs_box = doc.add_paragraph()
    p_abs_box.paragraph_format.space_before = Pt(6)
    p_abs_box.paragraph_format.space_after = Pt(6)
    p_abs_box.paragraph_format.line_spacing = 1.15
    
    r_abshdr = p_abs_box.add_run("Abstract: ")
    r_abshdr.font.bold = True
    r_abshdr.font.name = 'Arial'
    
    abs_body = (
        "Triple-Negative Breast Cancer (TNBC) remains one of the most aggressive and therapeutically challenging "
        "oncological malignancies due to the clinical absence of estrogen, progesterone, and HER2 receptors. While small-molecule "
        "inhibitors targeting Poly(ADP-ribose) polymerase 1 (PARP1) and systemic chemotherapeutics provide essential therapeutic "
        "options, their efficacy is constrained by non-specific tissue distribution, off-target toxicities and rapid clearance [3-5]. "
        "Here we present an integrated computational framework combining GFN2-xTB tight-binding quantum chemistry (with D4 dispersion) "
        "[25,26], physical molecular docking (AutoDock Vina v1.2.7 [31,32]), and a leak-free cross-validated explainable QSAR/QSPR "
        "surrogate, to evaluate the pristine inorganic boron nitride nanocage B36N36 as a non-carbonaceous drug-loading scaffold for "
        "33 anti-TNBC therapeutics. Frontier-orbital energies and conceptual-DFT reactivity indices (chemical hardness eta, softness S, "
        "electrophilicity omega) were read directly from the GFN2-xTB output. Docking against the human PARP1 catalytic domain "
        "(PDB ID: 4UND) is reported as an exploratory ranking only: self-redocking of the co-crystallized ligand reproduced the native "
        "pose only within >4 Å heavy-atom RMSD, so Vina scores (mean -7.22 kcal/mol, range -10.2 to -3.9) are not used as a quantitative "
        "endpoint. Each drug/B36N36 complex was built by offsetting the drug 3.2 Angstrom above the cage and relaxing it with GFN2-xTB "
        "(four orientations). Of the 30 organic drugs that could be modelled (the three square-planar Pt(II) agents fall outside the "
        "GFN2-xTB + RDKit build), 25 PHYSISORB on the pristine cage (closest contact 2.2-3.5 Angstrom, Delta_E_int,SP = -6 to -31 "
        "kcal/mol) and 5 CHEMISORB, forming a covalent B-O or B-N bond (contact 1.37-1.72 Angstrom, Delta_E_int,SP = -43 to -186 "
        "kcal/mol): the camptothecins SN-38 and topotecan, the anthracycline epirubicin, and the kinase inhibitors lapatinib and "
        "rucaparib, each through an accessible phenol, hydroxyl or lactam nucleophile. A descriptor-based QSPR of the physisorption "
        "energy is not predictive (Q2_CV = 0.0, n = 25); the docking-score QSPR reaches only Q2_CV = 0.11. A carboxylated B36N36-COOH "
        "derivative is discussed only as future work. Every value reported is computed from the deposited pipeline; no descriptor or "
        "energy is estimated from an empirical formula."
    )
    r_abs = p_abs_box.add_run(abs_body)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(16)
    r_kwhdr = p_kw.add_run("Keywords: ")
    r_kwhdr.font.bold = True
    r_kwhdr.font.name = 'Arial'
    r_kw = p_kw.add_run("Boron nitride nanocage; B36N36; Triple-Negative Breast Cancer; PARP1; Molecular docking; AutoDock Vina; Explainable AI; SHAP; QSAR/QSPR; Conceptual DFT.")
    r_kw.font.italic = True
    
    # ==============================================================================
    # 1. INTRODUCTION
    # ==============================================================================
    add_heading_styled(doc, "1. Introduction", level=1)
    
    doc.add_paragraph(
        "Breast cancer is the most frequently diagnosed malignant neoplasm in women worldwide, accounting for over 2.3 million "
        "new diagnoses and approximately 685,000 deaths annually [1]. Among its heterogeneous clinical subtypes, Triple-Negative "
        "Breast Cancer (TNBC)—defined immunohistochemically by the lack of estrogen receptor (ER), progesterone receptor (PR), "
        "and absence of human epidermal growth factor receptor 2 (HER2) overexpression—constitutes 15–20% of all breast carcinomas [2]. "
        "TNBC is characterized by aggressive clinical behavior, visceral metastatic tropism (particularly to the lungs, liver, "
        "and central nervous system), high rates of early relapse, and poor post-recurrence survival."
    )
    
    doc.add_paragraph(
        "Because targeted endocrine agents (e.g., tamoxifen, aromatase inhibitors) and anti-HER2 monoclonal antibodies (e.g., trastuzumab) "
        "are therapeutically ineffective in TNBC, systemic cytotoxic chemotherapy remains the cornerstone of standard pharmacological care. "
        "Furthermore, because 15–20% of TNBC tumors harbor deleterious germline or somatic mutations in breast cancer susceptibility "
        "genes (BRCA1/2) that impair homologous recombination DNA repair, synthetic lethality strategies utilizing Poly(ADP-ribose) "
        "polymerase 1 (PARP1) inhibitors (such as olaparib, talazoparib, rucaparib, niraparib, and pamiparib) have gained significant "
        "clinical importance [3,4]. Nevertheless, free small-molecule therapeutics suffer from severe clinical challenges: (i) narrow "
        "therapeutic indices and dose-limiting toxicities (cardiotoxicity, myelosuppression, and nephrotoxicity), (ii) poor aqueous solubility "
        "necessitating toxic surfactant vehicles, and (iii) rapid renal and hepatic clearance [5]."
    )
    
    doc.add_paragraph(
        "Nanomaterial-based drug delivery systems (DDS) offer a compelling nanotechnological strategy to enhance drug stability, "
        "modulate pharmacokinetics, and promote selective tumor accumulation through the enhanced permeability and retention (EPR) effect [6]. "
        "Although carbon-based nanocarriers, such as fullerenes (C60) and carbon nanotubes (CNTs), have been investigated extensively, their "
        "translational utility is frequently impeded by severe hydrophobicity, spontaneous aggregation in physiological media, and intrinsic "
        "pro-oxidant cytotoxicity arising from cellular reactive oxygen species (ROS) induction [7]. In contrast, zero-dimensional Boron "
        "Nitride (BN) nanostructures, such as hollow fullerene-like nanocages (B36N36), present distinct physicochemical and pharmacological "
        "advantages: (i) alternating polar B(δ+)–N(δ-) bonds providing intrinsic ionic character that enhances aqueous dispersion, (ii) exceptional "
        "chemical inertness and thermal stability, (iii) low hemolytic potential and high biocompatibility in mammalian systems, and (iv) facile "
        "covalent functionalization with polar carboxylate (-COOH) or hydroxyl (-OH) moieties [8,9]."
    )
    
    doc.add_paragraph(
        "Quantitative Structure–Activity/Property Relationship (QSAR/QSPR) modeling combined with quantum mechanics, rigorous molecular "
        "docking, and machine learning represents a powerful in silico paradigm to screen, evaluate, and predict nanocarrier–drug interactions. "
        "However, classical QSAR models often operate as opaque 'black boxes' or rely on simplified synthetic proxies. In this investigation, "
        "we present an explainable, quantum-informed QSAR framework for 33 anti-TNBC therapeutics interacting "
        "with the pristine B36N36 nanocage. Physical AutoDock Vina v1.2.7 docking against human PARP1 (PDB ID: 4UND) is used only as an "
        "exploratory affinity ranking (the co-crystallized ligand could not be redocked to within 2 Å), and the surrogate model and its "
        "SHAP-based feature ranking are reported as an honest exploratory baseline. A carboxylated B36N36-COOH derivative is considered "
        "only as future work (Conclusions), and all quantum results refer to the pristine cage."
    )
    
    # EMBED FIGURE 1
    fig1_path = os.path.join(fig_dir, "fig1_workflow_methodology.png")
    if os.path.exists(fig1_path):
        p_fig1 = doc.add_paragraph()
        p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig1.paragraph_format.space_before = Pt(12)
        doc.add_picture(fig1_path, width=Inches(6.2))
        p_cap1 = doc.add_paragraph()
        p_cap1.paragraph_format.space_after = Pt(14)
        r_c1 = p_cap1.add_run("Figure 1. ")
        r_c1.font.bold = True
        r_c1.font.name = 'Arial'
        p_cap1.add_run("Methodological workflow: (1) 33 curated anti-TNBC therapeutics; (2) real GFN2-xTB single-point interaction energies on the pristine B36N36 nanocage; (3) exploratory AutoDock Vina docking against the human PARP1 catalytic domain (PDB ID: 4UND); (4) a leak-free cross-validated explainable QSAR/QSPR surrogate.")
    
    # ==============================================================================
    # 2. COMPUTATIONAL METHODS
    # ==============================================================================
    add_heading_styled(doc, "2. Results and Discussion", level=1)
    
    add_heading_styled(doc, "2.1 Quantum conceptual-DFT reactivity of the isolated therapeutics", level=2)
    doc.add_paragraph(
        "Real GFN2-xTB single points for the 33-compound isolated cohort give a mean E_HOMO of -9.5 eV and mean E_LUMO of -7.5 eV "
        "(mean HOMO-LUMO gap 2.0 eV, mean chemical hardness eta = 1.0 eV), with the anthracyclines and topoisomerase payloads at the "
        "low-hardness / high-electrophilicity end of the distribution (Figure 2). No real complex-level frontier-orbital calculation "
        "exists for the B36N36 cage or the drug-cage complexes, so no complexation-induced gap narrowing is claimed; the interaction "
        "with the cage is characterized instead by the single-point interaction energies of Section 2.2."
    )
    
    # EMBED FIGURE 2
    fig2_path = os.path.join(fig_dir, "fig2_quantum_cdft_architecture.png")
    if os.path.exists(fig2_path):
        p_fig2 = doc.add_paragraph()
        p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig2_path, width=Inches(6.2))
        p_cap2 = doc.add_paragraph()
        p_cap2.paragraph_format.space_after = Pt(14)
        r_c2 = p_cap2.add_run("Figure 2. ")
        r_c2.font.bold = True
        r_c2.font.name = 'Arial'
        p_cap2.add_run("Real GFN2-xTB conceptual-DFT reactivity of the isolated TNBC therapeutics cohort (n=33): (a) HOMO/LUMO frontier-orbital distribution; (b) chemical hardness vs. softness; (c) global electrophilicity index distribution. No complex-level frontier-orbital calculation exists for the B36N36 cage.")
        
    add_heading_styled(doc, "2.2 Physical Molecular Docking on PARP1 and Active Site Relocation", level=2)
    doc.add_paragraph(
        "Table 1 lists, for the 30 organic drugs that could be modelled at GFN2-xTB level, the AutoDock Vina score against human PARP1 "
        "(PDB: 4UND), the relaxed GFN2-xTB interaction energy on the pristine B36N36 cage, the closest drug-cage contact and the resulting "
        "adsorption regime. The three square-planar Pt(II) agents (cisplatin, carboplatin, oxaliplatin) are not included: RDKit/MMFF has "
        "no Pt parameters, so a from-SMILES 3D build collapses and the subsequent GFN2-xTB energy is not meaningful. B36N36 interaction "
        "energy does not track PARP1 affinity: the strongest cage binders are the polyfunctional camptothecins and anthracyclines, which "
        "chemisorb (Section 2.1 / Figure 11), not the highest-scoring PARP inhibitors."
    )

    doc.add_paragraph().add_run("Table 1. AutoDock Vina v1.2.7 scores on human PARP1 (PDB ID: 4UND) and relaxed GFN2-xTB interaction energies on pristine B36N36 for the 30 modelled organic drugs (real data only; 3 Pt(II) agents outside GFN2-xTB+RDKit scope are omitted).").font.bold = True

    import pandas as _pd
    _t1 = _pd.read_csv(os.path.join(base_dir, "data", "processed", "dataset_tnbc_bn_pristine.csv"))
    _t1 = _t1[_t1["adsorption_mode"].isin(["chemisorption", "physisorption"])].copy()
    _t1 = _t1.sort_values("delta_Eint_SP_kcal_mol")
    table1_data = [["Therapeutic Agent", "Class", "DrugBank ID", "PARP1 Vina (kcal/mol)", "ΔE_int,SP (kcal/mol)", "Contact (Å)", "Regime"]]
    for _, _r in _t1.iterrows():
        table1_data.append([
            str(_r["name"]), str(_r.get("drug_class", ""))[:26], str(_r.get("drugbank_id", "")),
            f"{_r['vina_4UND_kcal_mol']:.2f}" if _pd.notna(_r.get("vina_4UND_kcal_mol")) else "-",
            f"{_r['delta_Eint_SP_kcal_mol']:.1f}", f"{_r['min_contact_A']:.2f}",
            "chemisorption" if _r["adsorption_mode"] == "chemisorption" else "physisorption",
        ])

    t1 = doc.add_table(rows=len(table1_data), cols=len(table1_data[0]))
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table1_data):
        for c_idx, val in enumerate(row):
            cell = t1.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 2 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            if r_idx == 0:
                set_cell_background(cell, "0D47A1")
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                p.runs[0].font.name = 'Arial'
                p.runs[0].font.size = Pt(9.5)
            else:
                set_cell_background(cell, "F5F5F5" if r_idx % 2 == 1 else "FFFFFF")
                p.runs[0].font.size = Pt(9.0)
                if c_idx == 0:
                    p.runs[0].font.bold = True
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # EMBED FIGURE 3
    fig3_path = os.path.join(fig_dir, "fig3_3d_parp1_docking_surfaces.png")
    if os.path.exists(fig3_path):
        p_fig3 = doc.add_paragraph()
        p_fig3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig3_path, width=Inches(6.2))
        p_cap3 = doc.add_paragraph()
        p_cap3.paragraph_format.space_after = Pt(14)
        r_c3 = p_cap3.add_run("Figure 3. ")
        r_c3.font.bold = True
        r_c3.font.name = 'Arial'
        p_cap3.add_run("Human PARP1 catalytic domain (PDB ID: 4UND) with a representative docked ligand. The most frequently contacted residues across the 35 poses are Glu688, Arg865, Thr866, Lys684, Thr867, Ser681, His909 and Ser911 (contact distance <= 3.8 A).")
        
    add_heading_styled(doc, "2.3 3D Quantum Geometries and Intermolecular Interactions", level=2)
    doc.add_paragraph(
        "After full GFN2-xTB relaxation, the 30 modelled drug/B36N36 complexes fall into two regimes (Figure 5, Figure 11). "
        "Twenty-five drugs PHYSISORB - they sit 2.2-3.5 Angstrom from the cage with Delta_E_int,SP = -6 to -31 kcal/mol (Olaparib "
        "-17.1, Talazoparib -24.1) - and five CHEMISORB: SN-38 (-186), epirubicin (-54), topotecan (-51), lapatinib (-49) and "
        "rucaparib (-43), each forming a covalent B-O or B-N bond (closest contact 1.37-1.72 Angstrom) through an accessible phenol, "
        "hydroxyl, lactam or indole nucleophile adding across an electron-deficient boron of the cage. The old draft's near-zero "
        "interaction energies (-0.38 to -4.8 kcal/mol) were single points on unrelaxed geometries and are superseded. Figure 5 shows "
        "the optimised carrier (a) and the relaxed Olaparib (b) and Talazoparib (c) physisorption complexes. Pristine B36N36 is "
        "therefore not a purely physisorptive scaffold for the polyfunctional camptothecin / anthracycline chemotype; a passivated or "
        "carboxylated cage that tempers the boron Lewis acidity is discussed only as future work (no real data here)."
    )
    
    # EMBED FIGURE 5
    fig5_path = os.path.join(fig_dir, "fig5_quantum_ground_state_geometries.png")
    if os.path.exists(fig5_path):
        p_fig5 = doc.add_paragraph()
        p_fig5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig5_path, width=Inches(6.2))
        p_cap5 = doc.add_paragraph()
        p_cap5.paragraph_format.space_after = Pt(14)
        r_c5 = p_cap5.add_run("Figure 5. ")
        r_c5.font.bold = True
        r_c5.font.name = 'Arial'
        p_cap5.add_run("Real GFN2-xTB optimised geometries: (a) the pristine B36N36 nanocage; (b) the relaxed Olaparib + B36N36 physisorption complex (ΔE_int,SP = -17.1 kcal/mol, closest contact 3.1 Angstrom); (c) the relaxed Talazoparib + B36N36 physisorption complex (ΔE_int,SP = -24.1 kcal/mol). Boron in pink, nitrogen in blue, carbon in grey. A carboxylated B36N36-COOH cage was not modelled (future work).")
        
    add_heading_styled(doc, "2.4 Statistical Docking Distributions and Residue Interactions", level=2)
    doc.add_paragraph(
        "Residue contact analysis across the 35 docked therapeutics (Figure 4) identifies Glu688, Arg865, Thr866, Lys684, Thr867 and "
        "Ser681 as the most frequently engaged residues within 3.8 Å. The isolated-drug Vina score and the real GFN2-xTB B36N36 "
        "interaction energy are only weakly (and negatively) correlated across the 20-compound overlap (Pearson r = -0.21), i.e. strong "
        "target binders are not systematically the strongest-adsorbing on the cage (Figure 6)."
    )
    
    # EMBED FIGURE 4 & FIGURE 6
    fig4_path = os.path.join(fig_dir, "fig4_interaction_residue_fingerprints.png")
    if os.path.exists(fig4_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig4_path, width=Inches(6.0))
        p_cap4 = doc.add_paragraph()
        p_cap4.paragraph_format.space_after = Pt(12)
        r_c4 = p_cap4.add_run("Figure 4. ")
        r_c4.font.bold = True
        r_c4.font.name = 'Arial'
        p_cap4.add_run("PARP1 interaction profiles from the real docked poses: (a) total residue contacts vs. estimated hydrogen bonds per drug; (b) residue contact-frequency distribution across the 35 docked therapeutics.")
        
    fig6_path = os.path.join(fig_dir, "fig6_docking_vina_statistical_profiles.png")
    if os.path.exists(fig6_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig6_path, width=Inches(6.0))
        p_cap6 = doc.add_paragraph()
        p_cap6.paragraph_format.space_after = Pt(12)
        r_c6 = p_cap6.add_run("Figure 6. ")
        r_c6.font.bold = True
        r_c6.font.name = 'Arial'
        p_cap6.add_run("Docking profiles: (a) distribution of AutoDock Vina scores on PARP1; (b) top-ranked therapeutics by score; (c) isolated-drug Vina score vs. real GFN2-xTB pristine-B36N36 interaction energy across the 20-compound overlap (weak negative correlation).")
        
    add_heading_styled(doc, "2.5 Machine Learning Benchmarking and Explainable AI (SHAP)", level=2)
    doc.add_paragraph(
        "Table 2 summarizes the RidgeCV surrogate (four pre-specified descriptors: MolWt, MolMR, E_HOMO, omega), both endpoints on the "
        "single 30/33-compound master table, evaluated by leak-free nested 5x5 cross-validation (StandardScaler fit on outer-training folds "
        "only; alpha by inner RidgeCV), reported as out-of-fold predictions. The model is non-predictive: Q2_CV = 0.11 for the PARP1 Vina "
        "docking score (n = 30) and Q2_CV = 0.0 for the 25-point physisorption interaction energy. The chemisorbers are excluded from the "
        "physisorption QSPR because covalent bond strength and dispersion are different physics. Descriptor-based prediction of either "
        "quantity on this small, chemically narrow cohort therefore fails; the model-free chemisorption/physisorption outcome (Figure 11) "
        "is the robust result. The exploratory ExtraTrees ranking indicates molecular weight and molar refractivity as leading descriptors "
        "and is reported qualitatively only."
    )

    # TABLE 2
    doc.add_paragraph().add_run("Table 2. Leak-free nested 5x5 cross-validation performance of the Ridge surrogate model on real observed data (out-of-fold predictions).").font.bold = True
    table2_data = [
        ["Endpoint", "Algorithm", "n", "p", "Q2_CV"],
        ["PARP1 Vina docking score (4UND)", "Ridge (nested 5x5 CV)", "30", "4", "0.11"],
        ["B36N36 physisorption interaction energy", "Ridge (nested 5x5 CV)", "25", "4", "0.00"],
    ]
    t2 = doc.add_table(rows=len(table2_data), cols=len(table2_data[0]))
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table2_data):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            cell.text = val
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 1 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            if r_idx == 0:
                set_cell_background(cell, "0D47A1")
                p.runs[0].font.bold = True
                p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
                p.runs[0].font.size = Pt(9.5)
            else:
                set_cell_background(cell, "F5F5F5" if r_idx % 2 == 1 else "FFFFFF")
                p.runs[0].font.size = Pt(9.0)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # EMBED FIGURE 8 & FIGURE 9
    fig8_path = os.path.join(fig_dir, "fig8_williams_applicability_domain.png")
    if os.path.exists(fig8_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig8_path, width=Inches(6.0))
        p_cap8 = doc.add_paragraph()
        p_cap8.paragraph_format.space_after = Pt(12)
        r_c8 = p_cap8.add_run("Figure 8. ")
        r_c8.font.bold = True
        r_c8.font.name = 'Arial'
        p_cap8.add_run("OECD Principle 3 Williams plots for the two real-data endpoints (PARP1 Vina docking, n=30; drug + pristine B36N36 physisorption interaction energy, n=25): out-of-fold standardized residuals vs. hat leverage with +/-3sigma boundaries and the h* warning limit.")
        
    fig9_path = os.path.join(fig_dir, "fig7_parity_models_evaluation.png")
    if os.path.exists(fig9_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig9_path, width=Inches(6.0))
        p_cap9 = doc.add_paragraph()
        p_cap9.paragraph_format.space_after = Pt(12)
        r_c9 = p_cap9.add_run("Figure 9. ")
        r_c9.font.bold = True
        r_c9.font.name = 'Arial'
        p_cap9.add_run("Leak-free nested 5x5 cross-validation parity plots (real observed vs. out-of-fold predicted) for (a) Isolated drugs (real Vina) and (b) Drug + B36N36 Pristine (real GFN2-xTB). No real structural/quantum data exists for Drug + B36N36-COOH, so it is not shown.")

    fig10_path = os.path.join(fig_dir, "fig10_tnbc_charge_density_difference.png")
    if os.path.exists(fig10_path):
        doc.add_paragraph(
            "To visualise the electronic reorganisation on adsorption, the charge-density difference "
            "Delta_rho = rho(complex) - rho(carrier) - rho(drug) was evaluated from the real GFN2-xTB densities of the "
            "Olaparib / B36N36 relaxed complex, all three fragments at the bound geometry on a common grid (Figure 10). "
            "Olaparib is one of the physisorbers (contact 3.1 Angstrom, Delta_E_int,SP = -17.1 kcal/mol): the accumulation (yellow) and "
            "depletion (blue) lobes are confined to the drug carbonyl / amide region facing the cage, with the B36N36 framework "
            "essentially unperturbed - no new bond, in contrast to the chemisorbers of Figure 11. The Delta_rho cube and the script "
            "that regenerates it from the fragment geometries are provided in results/quantum/drho/."
        )
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig10_path, width=Inches(5.4))
        p_cap10 = doc.add_paragraph()
        p_cap10.paragraph_format.space_after = Pt(12)
        r_c10 = p_cap10.add_run("Figure 10. ")
        r_c10.font.bold = True
        r_c10.font.name = 'Arial'
        p_cap10.add_run("Charge-density difference (real GFN2-xTB densities) for the Olaparib / B36N36 nanocage physisorption "
                        "complex. Isovalue +/-0.0008 e bohr^-3; yellow = electron accumulation, blue = electron depletion.")

    fig11_path = os.path.join(fig_dir, "fig11_tnbc_adsorption_landscape.png")
    if os.path.exists(fig11_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig11_path, width=Inches(5.6))
        p_cap11 = doc.add_paragraph()
        p_cap11.paragraph_format.space_after = Pt(12)
        r_c11 = p_cap11.add_run("Figure 11. ")
        r_c11.font.bold = True
        r_c11.font.name = 'Arial'
        p_cap11.add_run("GFN2-xTB adsorption landscape of the 30 modelled anti-TNBC drugs on pristine B36N36 - closest "
                        "drug-cage heavy-atom contact vs Delta_E_int,SP. Two cleanly separated regimes: 5 chemisorbers "
                        "(grey band, covalent B-O/B-N at ~1.5 A, -43 to -186 kcal/mol) and 25 physisorbers (2.2-3.5 A, "
                        "-6 to -31 kcal/mol).")

    add_heading_styled(doc, "2.6 Explicit Analytical QSAR Mathematical Models", level=2)
    doc.add_paragraph(
        "Using the top AI-ranked descriptors on the real observed data, compact, transparent, and exportable Multiple Linear Regression (MLR) "
        "models were formulated. Model 1 is fit on the real isolated-drug Vina docking data. Model 2 is refit here on the real GFN2-xTB "
        "single-point interaction energies for the pristine B36N36 cage (dataset_tnbc_bn_pristine.csv, n=33); the version of this equation in "
        "an earlier draft was fit on a fabricated Docking_Score_kcal_mol and is superseded. No real structural or quantum data exists for the "
        "B36N36-COOH system, so no Model 3 is reported."
    )

    mlr_eqs = [
        ("Model 1 (Isolated Therapeutics, real Vina, n=35):",
         "Score_Isolated = +65.4718 - 0.3772(NOR) + 0.4849(AromRings) + 0.0627(WS) - 0.7022(LogS) + 0.0467(α) - 0.6372(Fraction_Csp3) - 13.6666(χ) + 5.5923(E_LUMO)"),
        ("Model 2 (Drug + B36N36 Pristine, real GFN2-xTB ΔE_int,SP, n=33):",
         "Score_B36N36 = -16.8827 - 0.0044(MolWt) + 0.0014(MolMR) - 1.7479(E_HOMO) - 0.0118(ω)"),
    ]
    for m_title, m_eq in mlr_eqs:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.left_indent = Inches(0.4)
        p_m.paragraph_format.space_after = Pt(4)
        r_mt = p_m.add_run(f"{m_title}\n")
        r_mt.font.bold = True
        r_mt.font.color.rgb = RGBColor(13, 71, 161)
        r_me = p_m.add_run(m_eq)
        r_me.font.name = 'Courier New'
        r_me.font.size = Pt(9.5)
        
    # ==============================================================================
    # 4. CONCLUSIONS
    # ==============================================================================
    add_heading_styled(doc, "3. Conclusions", level=1)
    doc.add_paragraph(
        "We report a quantum-informed, explainable QSAR/QSPR analysis of the pristine inorganic boron nitride nanocage B36N36 as a "
        "candidate loading scaffold for 33 anti-TNBC therapeutics. Key points:"
    )

    concl_points = [
        "1. Exploratory docking: AutoDock Vina scores against the PARP1 catalytic domain (PDB 4UND) range from about -3.9 to -10.2 kcal/mol, but self-redocking of the co-crystallized ligand failed to reproduce the native pose within 2 A, so these scores are used only as a relative ranking and not as a quantitative endpoint.",
        "2. Two adsorption regimes: after full GFN2-xTB relaxation of the 30 modelled complexes, 25 drugs physisorb on pristine B36N36 (Delta_E_int,SP = -6 to -31 kcal/mol, contact 2.2-3.5 A) and 5 - SN-38, epirubicin, topotecan, lapatinib, rucaparib - chemisorb, forming a covalent B-O/B-N bond (-43 to -186 kcal/mol). Pristine B36N36 is therefore not a purely physisorptive scaffold for the polyfunctional camptothecin/anthracycline chemotype. The three Pt(II) agents are outside the GFN2-xTB+RDKit build. A carboxylated B36N36-COOH derivative has no real data here.",
        "3. Honest ML baseline: on the single 30/33-compound master table, the leak-free nested 5x5 cross-validated RidgeCV surrogate is non-predictive - Q2_CV = 0.11 for the PARP1 docking score and 0.0 for the 25-point physisorption energy; the descriptor rankings are qualitative only. The model-free chemisorption/physisorption outcome is the robust result.",
        "4. Applicability domain: Williams-leverage analysis (OECD Principle 3) places the modelled compounds inside the domain for both endpoints; given the near-zero Q2, this is a formality.",
        "5. Outlook: inorganic B36N36 is attractive on solubility and biocompatibility grounds, but for the reactive chemotype adsorption is effectively irreversible; a passivated / functionalised cage and a validated model are left as future work."
    ]
    for cp in concl_points:
        p_cp = doc.add_paragraph()
        p_cp.paragraph_format.left_indent = Inches(0.3)
        p_cp.paragraph_format.space_after = Pt(4)
        p_cp.add_run(cp)
        
    # ------------------------------------------------------------------ back matter
    add_heading_styled(doc, "4. Experimental", level=1)
    
    add_heading_styled(doc, "4.1 Curated Anti-TNBC Therapeutic Library", level=2)
    doc.add_paragraph(
        "A library of anti-TNBC therapeutic agents with established clinical activity or ongoing clinical trials was curated from DrugBank "
        "and PubChem, spanning PARP1 inhibitors (olaparib, talazoparib, rucaparib, niraparib, veliparib, pamiparib), topoisomerase "
        "inhibitors and ADC payloads (irinotecan, SN-38, topotecan, etoposide, exatecan), anthracyclines (doxorubicin, epirubicin, "
        "idarubicin), antimetabolites (gemcitabine, capecitabine, 5-fluorouracil, methotrexate, pemetrexed, cytarabine), microtubule "
        "agents (ixabepilone, eribulin, vinorelbine), kinase modulators (lapatinib, gefitinib, erlotinib, afatinib, bemcentinib, "
        "alpelisib) and CDK4/6 inhibitors (palbociclib, ribociclib, abemaciclib). Of these, 35 completed docking and 33 have a converged "
        "GFN2-xTB drug-cage complex; the analyses below use those real subsets."
    )

    add_heading_styled(doc, "4.2 Quantum-chemical framework", level=2)
    doc.add_paragraph(
        "Each isolated drug, the pristine B36N36 cage, and every drug-cage complex were geometry-optimized and evaluated at single point "
        "with GFN2-xTB (xtb v6.7.1) including the D4 dispersion correction [25,26], in the gas phase. The standardized single-point "
        "interaction energy is Delta_E_int,SP = E(complex) - E(cage) - E(drug), with both fragments taken at the complex geometry; a "
        "relaxed-geometry adsorption energy was additionally computed for a curated 8-compound subset (Supporting Information). "
        "Frontier-orbital energies and conceptual-DFT reactivity indices were read directly from the xtb output using:"
    )
    
    eqs = [
        ("Ionization Potential (I):", "I ≈ -E_HOMO"),
        ("Electron Affinity (A):", "A ≈ -E_LUMO"),
        ("Chemical Hardness (η):", "η = (E_LUMO - E_HOMO) / 2"),
        ("Global Softness (S):", "S = 1 / (2η) = 1 / (E_LUMO - E_HOMO)"),
        ("Electronegativity (χ) & Chemical Potential (μ):", "χ = -μ = -(E_HOMO + E_LUMO) / 2"),
        ("Global Electrophilicity Index (ω):", "ω = μ² / (2η) = (E_HOMO + E_LUMO)² / [4(E_LUMO - E_HOMO)]"),
        ("Standardized interaction energy (ΔE_int,SP):", "ΔE_int,SP = E_complex - E_cage - E_drug  (fragments at the complex geometry)")
    ]
    for name, form in eqs:
        p_eq = doc.add_paragraph()
        p_eq.paragraph_format.left_indent = Inches(0.5)
        p_eq.paragraph_format.space_after = Pt(3)
        r_n = p_eq.add_run(f"{name}  ")
        r_n.font.bold = True
        p_eq.add_run(form)
        
    add_heading_styled(doc, "4.3 Molecular docking against human PARP1 (PDB 4UND)", level=2)
    doc.add_paragraph(
        "The X-ray structure of the human PARP1 catalytic domain (PDB ID: 4UND) was prepared by removing crystallographic waters, "
        "extracting the co-crystallized ligand to centre the search grid, adding polar hydrogens and assigning Gasteiger charges. "
        "Ligand conformers were generated with ETKDGv3 / UFF in RDKit and formatted with Meeko; docking used AutoDock Vina v1.2.7 "
        "(exhaustiveness 8, 22 x 22 x 22 A grid). Self-redocking of the co-crystallized ligand did not reproduce the native pose within "
        "2 A heavy-atom RMSD, so the Vina scores are used only as a relative exploratory ranking and never as a QSAR endpoint."
    )
    
    add_heading_styled(doc, "4.4 Machine Learning, Explainable AI (SHAP), and OECD Validation", level=2)
    doc.add_paragraph(
        "A regularized RidgeCV surrogate model with four pre-specified descriptors (MW, molar refractivity, E_HOMO, electrophilicity "
        "omega; n = 30 for the PARP1 Vina docking endpoint and n = 25 for the pristine-B36N36 physisorption endpoint, chemisorbers excluded) was evaluated by a leak-free nested 5x5 cross-validation "
        "protocol: an outer 5-fold split produced out-of-fold predictions for every compound, while StandardScaler and the Ridge "
        "regularization strength (alpha) were fit exclusively on each outer-training split via an inner 5-fold RidgeCV, so no "
        "test-fold information leaked into preprocessing or hyperparameter selection. Model performance was evaluated using Root "
        "Mean Squared Error (RMSE), Mean Absolute Error (MAE), and the pooled out-of-fold coefficient of determination (Q2_CV). "
        "SHAP (Shapley Additive Explanations) values [39, 43], computed from an exploratory ExtraTrees estimator [40] fit on the full data, "
        "were used only to rank candidate descriptors and were not used to select or validate the reported RidgeCV surrogate. "
        "Compliance with OECD Principle 3 (domain of applicability) [41, 42] "
        "was confirmed via Williams plots of standardized residuals versus hat leverage values (h_i) relative to the critical threshold h* = 3(p+1)/n, "
        "following established QSAR model-validation best practice [44]."
    )
    
    # ==============================================================================
    # 3. RESULTS AND DISCUSSION
    # ==============================================================================

    add_heading_styled(doc, "Data Availability", level=1)
    doc.add_paragraph(
        "All code, the curated dataset, the real GFN2-xTB and AutoDock Vina outputs, the leak-free cross-validation predictions and the "
        "figure/manuscript generators are in the public repository https://github.com/sircalch/nano-qsar-ai-therapeutics. The full pipeline "
        "reproduces every value and figure.")
    import sys as _bsys, os as _bos
    _bsys.path.insert(0, _bos.path.dirname(_bos.path.abspath(__file__)))
    import _backmatter
    _backmatter.append(doc, add_heading_styled,
                       "TNBC_B36N36_Supporting_Information.docx",
                       "curated dataset (N = 33), formal charges at pH 7.4, the OECD Principles 1-5 checklist and per-residue PARP1 contact frequencies")

    # ==============================================================================
    # 5. REFERENCES (45 REAL, VERIFIED CITATIONS WITH DOIS)
    # ==============================================================================
    add_heading_styled(doc, "References", level=1)
    
    from build_comprehensive_verified_references import VERIFIED_REFERENCES
    for idx, ref in enumerate(VERIFIED_REFERENCES, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.space_after = Pt(3)
        r_num = p_ref.add_run(f"{idx}. ")
        r_num.font.bold = True
        p_ref.add_run(ref['citation'] + " ")
        if ref.get('doi'):
            r_doi = p_ref.add_run(f"doi:{ref['doi']}")
            r_doi.font.italic = True
            r_doi.font.size = Pt(9.0)
            r_doi.font.color.rgb = RGBColor(13, 71, 161)
        
    doc.save(out_docx)
    print(f"Successfully generated Beilstein Word Manuscript: {out_docx}")
    return out_docx

if __name__ == "__main__":
    build_manuscript_word()
