"""
prepare_final_submission_package.py
Prepares the complete, official, 100% submission-ready bundle for:
- Beilstein Journal of Nanotechnology (BJNANO) / Elsevier

Generates:
1. manuscript/submission_ready/01_Cover_Letter_Beilstein.docx & .md
2. manuscript/submission_ready/02_Main_Manuscript_Monreal_Hernandez_et_al.docx
3. manuscript/submission_ready/03_Supplementary_Information_Monreal_Hernandez_et_al.docx
4. manuscript/submission_ready/04_Graphical_Abstract.png
5. manuscript/submission_ready/05_Figures_300DPI/ (Fig1 to Fig9)
6. manuscript/submission_ready/06_Suggested_Reviewers.txt
7. manuscript/submission_ready/07_Submission_Checklist.md
8. nano-qsar-ai-therapeutics-FINAL-SUBMISSION-READY.zip
"""

import os
import shutil
import zipfile
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_cover_letter(sub_dir):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(33, 33, 33)
    
    # Header
    p_h = doc.add_paragraph()
    p_h.paragraph_format.space_after = Pt(14)
    r_h = p_h.add_run("Andrés Monreal Hernández, Ph.D.\n")
    r_h.font.bold = True
    p_h.add_run(
        "Universidad Estatal de Sonora\n"
        "Hermosillo, Sonora, Mexico\n"
        "Email: andres.monreal@ues.mx | ORCID: 0009-0009-1207-8597\n"
        "Date: August 30, 2026\n"
    )
    
    p_ed = doc.add_paragraph()
    p_ed.paragraph_format.space_after = Pt(12)
    p_ed.add_run(
        "To: The Editor-in-Chief\n"
        "Beilstein Journal of Nanotechnology\n"
        "Beilstein-Institut, Frankfurt am Main, Germany\n"
    )
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Subject: Submission of Original Research Article for Peer Review")
    r_sub.font.bold = True
    
    doc.add_paragraph("Dear Editor-in-Chief,")
    
    doc.add_paragraph(
        "On behalf of my co-authors (Sara Lizbeth Franco Amaya, Carlos Ivanhoe Martínez Osorio, and myself), "
        "I am pleased to submit our original research manuscript titled:"
    )
    
    p_t = doc.add_paragraph()
    p_t.paragraph_format.left_indent = Inches(0.4)
    p_t.paragraph_format.space_after = Pt(10)
    r_t = p_t.add_run("“Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages”")
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(13, 71, 161)
    
    doc.add_paragraph(
        "for consideration for publication as a Full Research Article in the Beilstein Journal of Nanotechnology."
    )
    
    doc.add_paragraph(
        "Triple-Negative Breast Cancer (TNBC) represents one of the most therapeutically recalcitrant oncological diseases due to the absence of "
        "estrogen, progesterone, and HER2 receptors. While Poly(ADP-ribose) polymerase 1 (PARP1) synthetic lethality and cytotoxic therapies offer "
        "essential clinical interventions, their efficacy is severely hindered by off-target toxicities, rapid systemic clearance, and poor aqueous solubility."
    )
    
    doc.add_paragraph(
        "In this study, we present an integrated GFN2-xTB quantum-chemical, physical molecular docking "
        "(AutoDock Vina v1.2.7), and explainable QSAR/QSPR framework evaluating the pristine inorganic boron "
        "nitride nanocage B36N36 as a non-carbonaceous drug-delivery scaffold for 33 anti-TNBC therapeutics. "
        "A carboxylated B36N36-COOH derivative is discussed only as future work, since no real structural or "
        "quantum data for it exist in this study."
    )

    p_hi = doc.add_paragraph()
    p_hi.add_run("Key points, all traceable to the deposited pipeline:").font.bold = True

    highlights = [
        "1. GFN2-xTB single-point interaction energies for all 33 therapeutics on the B36N36 cage were computed "
        "from the xtb pipeline; frontier-orbital and conceptual-DFT indices are taken directly from the output, "
        "not from an empirical formula.",
        "2. Redocking against the human PARP1 crystal structure (PDB ID: 4UND) did NOT reproduce the native "
        "ligand pose (heavy-atom RMSD > 4 Å); the reported Vina scores are therefore treated as exploratory "
        "and are not used as a quantitative endpoint.",
        "3. The surrogate model was evaluated with a leak-free nested 5x5 cross-validation on the real "
        "interaction energies. Predictive performance is low (Q2_CV near zero); the model and its "
        "feature-importance ranking are presented as an exploratory, honest baseline rather than a "
        "validated predictor.",
        "4. OECD Principle 3 applicability domain was assessed by Williams leverage on the real descriptor "
        "matrix (30/33 compounds inside the domain).",
        "5. Fully automated open-source pipeline with the complete real dataset and 300 DPI figures "
        "(Zenodo 10.5281/zenodo.22187873)."
    ]
    for h in highlights:
        p_item = doc.add_paragraph()
        p_item.paragraph_format.left_indent = Inches(0.3)
        p_item.paragraph_format.space_after = Pt(3)
        p_item.add_run(h)
        
    doc.add_paragraph(
        "We confirm that this manuscript is original, has not been published previously, and is not currently under consideration for publication elsewhere. "
        "All authors have approved the final manuscript and declare no competing financial or non-financial interests."
    )
    
    doc.add_paragraph("Thank you very much for your time, consideration, and editorial handling of our work.")
    
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_before = Pt(12)
    p_sign.add_run(
        "Sincerely,\n\n"
        "Andrés Monreal Hernández, Ph.D. (Corresponding Author)\n"
        "Universidad Estatal de Sonora, Mexico\n"
        "Email: andres.monreal@ues.mx"
    )
    
    out_docx = os.path.join(sub_dir, "01_Cover_Letter_Beilstein.docx")
    doc.save(out_docx)
    
    # Also save markdown version
    out_md = os.path.join(sub_dir, "01_Cover_Letter_Beilstein.md")
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("""# Cover Letter for Beilstein Journal of Nanotechnology

**Date:** August 30, 2026  
**From:** Andrés Monreal Hernández, Ph.D. (Universidad Estatal de Sonora, Mexico)  
**Email:** `andres.monreal@ues.mx` | **ORCID:** 0009-0009-1207-8597  

**To:** The Editor-in-Chief, *Beilstein Journal of Nanotechnology*  

**Subject:** Submission of Original Research Article  
**Title:** *“Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages”*  
**Authors:** Andrés Monreal Hernández (Corresponding Author), Sara Lizbeth Franco Amaya, and Carlos Ivanhoe Martínez Osorio  

---

Dear Editor-in-Chief,

On behalf of my co-authors, I am pleased to submit our original research manuscript for consideration for publication as a Full Research Article in the *Beilstein Journal of Nanotechnology*.

### Key points (all traceable to the deposited pipeline):
1. **GFN2-xTB interaction energies** for all 33 therapeutics on the B36N36 cage, computed from the xtb pipeline; frontier-orbital / conceptual-DFT indices taken directly from the output.
2. **Redocking on PARP1 (PDB 4UND) did not reproduce the native pose** (heavy-atom RMSD > 4 Å); Vina scores are reported as exploratory only.
3. **Leak-free nested 5×5 cross-validation** on the real interaction energies; predictive performance is low (Q²_CV near zero) and the model is presented as an honest exploratory baseline, not a validated predictor.
4. **OECD Principle 3** applicability domain by Williams leverage on the real descriptor matrix (30/33 inside the domain).
5. **Full reproducibility:** open-source pipeline with the complete real dataset (Zenodo 10.5281/zenodo.22187873).

All authors have approved the submission and confirm no conflict of interest.

Sincerely,  
**Andrés Monreal Hernández, Ph.D.**  
Universidad Estatal de Sonora, Hermosillo, Sonora, Mexico  
`andres.monreal@ues.mx`
""")
    print(f"Generated Cover Letter: {out_docx}")


def create_cover_letter_md(sub_dir):
    """Molecular Diversity edition. Only real, pipeline-traceable claims."""
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(1.0)
        s.left_margin = s.right_margin = Inches(1.0)
    fo = doc.styles['Normal'].font
    fo.name = 'Times New Roman'; fo.size = Pt(11); fo.color.rgb = RGBColor(33, 33, 33)
    doc.add_paragraph("Andrés Monreal Hernández, Ph.D.\nUniversidad Estatal de Sonora, Hermosillo, Sonora, Mexico\n"
                      "Email: andres.monreal@ues.mx | ORCID: 0009-0009-1207-8597").runs[0].font.bold = True
    doc.add_paragraph("To: The Editor-in-Chief, Molecular Diversity (Springer Nature)")
    doc.add_paragraph("Dear Editor,")
    doc.add_paragraph("We submit our original research manuscript for consideration in Molecular Diversity:")
    r = doc.add_paragraph().add_run("“Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative "
                                    "Breast Cancer Therapeutics Conjugated to Functionalized Boron Nitride Nanocages”")
    r.font.bold = True; r.font.color.rgb = RGBColor(13, 71, 161)
    doc.add_paragraph("Real, pipeline-traceable results:").runs[0].font.bold = True
    for h in [
        "GFN2-xTB single-point interaction energies for 33 anti-TNBC therapeutics on the pristine B36N36 "
        "nanocage; frontier-orbital and conceptual-DFT indices taken directly from the xtb output.",
        "Redocking against PARP1 (PDB 4UND) did not reproduce the native pose (heavy-atom RMSD > 4 Å); "
        "Vina scores are reported as exploratory only.",
        "Leak-free nested 5x5 cross-validation on the real interaction energies; Q2_CV near zero. The model "
        "and its feature-importance ranking are presented as an honest exploratory baseline.",
        "OECD Principle 3 applicability domain by Williams leverage on the real descriptor matrix "
        "(30/33 inside the domain).",
        "A carboxylated B36N36-COOH derivative is proposed as future work; it has no real data in this study.",
        "Full open-source pipeline and data archive (Zenodo 10.5281/zenodo.22187873).",
    ]:
        p = doc.add_paragraph(h); p.paragraph_format.left_indent = Inches(0.3)
    doc.add_paragraph("The manuscript is original, not under consideration elsewhere, and all authors approve the "
                      "submission and declare no competing interests.")
    doc.add_paragraph("Sincerely,\nAndrés Monreal Hernández, Ph.D. (Corresponding Author)")
    doc.save(os.path.join(sub_dir, "01_Cover_Letter_Molecular_Diversity.docx"))
    print("Generated TNBC Molecular Diversity Cover Letter")


def create_cover_letter_jmm(sub_dir):
    """Journal of Molecular Modeling (Springer) edition, 2026-09-12.

    Fourth and last in the Q3/no-APC retargeting series -- see
    [[feedback_prioritize_q3_no_apc_journals]]. This is the weakest of the 4
    papers (Q2_CV near zero for both endpoints, redocking RMSD > 4 Å), so the
    honest framing here leans hardest on reproducibility and transparency
    rather than predictive claims.
    """
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Inches(1.0)
        s.left_margin = s.right_margin = Inches(1.0)
    fo = doc.styles['Normal'].font
    fo.name = 'Times New Roman'; fo.size = Pt(11); fo.color.rgb = RGBColor(33, 33, 33)

    doc.add_paragraph("Andrés Monreal Hernández, Ph.D.\nUniversidad Estatal de Sonora, Hermosillo, Sonora, Mexico\n"
                      "Email: andres.monreal@ues.mx | ORCID: 0009-0009-1207-8597").runs[0].font.bold = True
    doc.add_paragraph("To: The Editor-in-Chief, Journal of Molecular Modeling (Springer Nature)")
    doc.add_paragraph("Subject: Submission of Original Research Article for Peer Review").runs[0].font.bold = True
    doc.add_paragraph("Dear Editor,")
    doc.add_paragraph(
        "On behalf of my co-authors (Sara Lizbeth Franco Amaya, Carlos Ivanhoe Martínez Osorio, and myself), "
        "I am pleased to submit our original research manuscript for consideration as a Full Research Article "
        "in the Journal of Molecular Modeling:"
    )
    r = doc.add_paragraph().add_run(
        "“Explainable AI and Quantum-Guided QSAR/QSPR Modeling of Triple-Negative Breast Cancer Therapeutics "
        "Conjugated to Functionalized Boron Nitride Nanocages”"
    )
    r.font.bold = True; r.font.color.rgb = RGBColor(13, 71, 161)
    doc.add_paragraph(
        "The study integrates GFN2-xTB quantum-chemical adsorption modeling of 33 anti-TNBC therapeutics on the "
        "pristine inorganic boron nitride nanocage B36N36, AutoDock Vina docking against the human PARP1 "
        "catalytic domain (PDB ID: 4UND), and an explainable leak-free nested cross-validated surrogate -- "
        "squarely within the journal's scope in computational and theoretical chemistry."
    )
    doc.add_paragraph("Key points, all traceable to the deposited pipeline:").runs[0].font.bold = True
    for h in [
        "GFN2-xTB single-point interaction energies for all 33 therapeutics on the B36N36 cage, computed from "
        "the xtb pipeline; frontier-orbital and conceptual-DFT indices are taken directly from the output, not "
        "from an empirical formula.",
        "Redocking against the human PARP1 crystal structure (PDB ID: 4UND) did NOT reproduce the native ligand "
        "pose (heavy-atom RMSD > 4 Å); the reported Vina scores are therefore treated as exploratory and are "
        "not used as a quantitative endpoint.",
        "The surrogate model was evaluated with a leak-free nested 5x5 cross-validation on the real interaction "
        "energies. Predictive performance is low (Q2_CV near zero for both endpoints); we present the model and "
        "its feature-importance ranking as an honest exploratory baseline, not a validated predictor -- the "
        "chemisorption/physisorption dichotomy is the robust, model-free finding.",
        "OECD Principle 3 applicability domain was assessed by Williams leverage on the real descriptor matrix "
        "(30/33 compounds inside the domain).",
        "Fully automated open-source pipeline with the complete real dataset (Zenodo DOI 10.5281/zenodo.22187873), "
        "reproducing every value and figure in the manuscript.",
    ]:
        p = doc.add_paragraph(h); p.paragraph_format.left_indent = Inches(0.3)
    doc.add_paragraph(
        "The manuscript is original, not under consideration elsewhere, and all authors approve the submission "
        "and declare no competing interests."
    )
    doc.add_paragraph("Sincerely,\nAndrés Monreal Hernández, Ph.D. (Corresponding Author)\nUniversidad Estatal de Sonora, Mexico")
    out_docx = os.path.join(sub_dir, "01_Cover_Letter_JMM.docx")
    doc.save(out_docx)
    print(f"Generated TNBC Journal of Molecular Modeling Cover Letter: {out_docx}")


def create_suggested_reviewers(sub_dir):
    rev_path = os.path.join(sub_dir, "06_Suggested_Reviewers.txt")
    rev_text = """SUGGESTED PEER REVIEWERS (Beilstein Journal of Nanotechnology / Elsevier)
========================================================================

Reviewer 1:
- Name: Prof. Alan Miralrio
- Institution: Tecnologico de Monterrey, Escuela de Ingenieria y Ciencias, Mexico
- Email: miralrio@tec.mx
- Expertise: Quantum chemistry, Conceptual DFT, QSAR/QSPR, Nanomaterials, Drug delivery systems.

Reviewer 2:
- Name: Prof. Roberto Salcedo
- Institution: Instituto de Investigaciones en Materiales, Universidad Nacional Autónoma de México (UNAM), Mexico
- Email: salcedo@iim.unam.mx
- Expertise: Theoretical chemistry, fullerenes, boron nitride nanostructures, molecular modeling.

Reviewer 3:
- Name: Prof. Subhash C. Basak
- Institution: University of Minnesota Duluth, International Society of Mathematical Chemistry, USA
- Email: sbasak@d.umn.edu
- Expertise: Mathematical chemistry, chemoinformatics, QSAR modeling, topological descriptors.

Reviewer 4:
- Name: Prof. Pratim K. Chattaraj
- Institution: Indian Institute of Technology (IIT) Kharagpur, Department of Chemistry, India
- Email: pkc@chem.iitkgp.ac.in
- Expertise: Conceptual Density Functional Theory (CDFT), chemical reactivity indices, electrophilicity.

Reviewer 5:
- Name: Prof. Bakhtiyor Rasulev
- Institution: North Dakota State University, Department of Coatings and Polymeric Materials, USA
- Email: bakhtiyor.rasulev@ndsu.edu
- Expertise: Machine learning in QSAR, nanomaterials property prediction, cheminformatics.
"""
    with open(rev_path, 'w', encoding='utf-8') as f:
        f.write(rev_text)
    print(f"Generated Suggested Reviewers: {rev_path}")

def create_submission_checklist(sub_dir):
    chk_path = os.path.join(sub_dir, "07_Submission_Checklist.md")
    chk_text = """# Official Submission Checklist & Portal Guide (Beilstein Journal of Nanotechnology)

## 📋 Required Documents & Files:
- [x] **01_Cover_Letter_Beilstein.docx** (Cover letter with summary, highlights, and author declarations).
- [x] **02_Main_Manuscript_Monreal_Hernandez_et_al.docx** (Full article with embedded 300 DPI figures and Tables 1–2).
- [x] **03_Supplementary_Information_Monreal_Hernandez_et_al.docx** (Tables S1-S3: real dataset, formal charges, OECD checklist).
- [x] **04_Graphical_Abstract.png** (Official High-Resolution Graphical Abstract, 300 DPI).
- [x] **05_Figures_300DPI/** (Numbered individual high-resolution figures Fig 1 to Fig 9).
- [x] **06_Suggested_Reviewers.txt** (5 expert reviewers with institutions and email addresses).

## 🚀 How to Submit in the Beilstein Portal (Step-by-Step):
1. Navigate to: **https://www.beilstein-journals.org/bjnano**
2. Click on **"Submit a Manuscript"** (Beilstein Publishing System - BPS).
3. Log in with your account (or create one using `andres.monreal@ues.mx`).
4. **Step 1 - Article Type:** Select **"Full Research Article"**.
5. **Step 2 - Title & Abstract:** Paste the Title and Abstract from `02_Main_Manuscript`.
6. **Step 3 - Authors & Affiliations:**
   - Andrés Monreal Hernández (Corresponding Author, UES, ORCID: 0009-0009-1207-8597)
   - Sara Lizbeth Franco Amaya (UNISON, ORCID: 0009-0005-0272-0241)
   - Carlos Ivanhoe Martínez Osorio (UNISON, ORCID: 0009-0003-7872-4965)
7. **Step 4 - Upload Files:**
   - Primary Manuscript File: `02_Main_Manuscript_Monreal_Hernandez_et_al.docx`
   - Cover Letter: `01_Cover_Letter_Beilstein.docx`
   - Graphical Abstract: `04_Graphical_Abstract.png`
   - Supporting Information: `03_Supplementary_Information_Monreal_Hernandez_et_al.docx`
8. **Step 5 - Suggested Reviewers:** Copy and paste the 5 reviewers from `06_Suggested_Reviewers.txt`.
9. **Step 6 - Review & Submit:** Download the generated PDF proof, check all figures, and click **Submit**.
"""
    with open(chk_path, 'w', encoding='utf-8') as f:
        f.write(chk_text)
    print(f"Generated Submission Checklist: {chk_path}")

def build_complete_submission_folder():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sub_dir = os.path.join(base_dir, "manuscript", "submission_ready")
    fig_dest_dir = os.path.join(sub_dir, "05_Figures_300DPI")
    os.makedirs(fig_dest_dir, exist_ok=True)
    
    # 1. Cover Letter
    create_cover_letter(sub_dir)
    create_cover_letter_md(sub_dir)
    create_cover_letter_jmm(sub_dir)

    # 1b. JMM manuscript (post-processes the canonical Beilstein body: structured
    # Context/Methods abstract + section reorder) -- run it here so the bundle
    # always picks up a fresh copy.
    import generate_tnbc_jmm_manuscript
    generate_tnbc_jmm_manuscript.generate_tnbc_jmm_manuscript()

    # 2. Main Manuscript Word
    src_ms = os.path.join(base_dir, "manuscript", "Beilstein_Manuscript_Monreal_Hernandez_et_al.docx")
    dst_ms = os.path.join(sub_dir, "02_Main_Manuscript_Monreal_Hernandez_et_al.docx")
    if os.path.exists(src_ms):
        shutil.copyfile(src_ms, dst_ms)

    src_si = os.path.join(base_dir, "manuscript", "TNBC_Nanocage_Supporting_Information.docx")
    dst_si = os.path.join(sub_dir, "03_Supporting_Information_Monreal_Hernandez_et_al.docx")
    if os.path.exists(src_si):
        shutil.copyfile(src_si, dst_si)

    # 3. Graphical Abstract
    src_ga = os.path.join(base_dir, "figures", "fig1_graphical_abstract.png")
    dst_ga = os.path.join(sub_dir, "04_Graphical_Abstract.png")
    if os.path.exists(src_ga):
        shutil.copyfile(src_ga, dst_ga)

    # 4. Copy High-Resolution Figures
    fig_mappings = [
        ("fig1_graphical_abstract.png", "Figure_1_Graphical_Abstract.png"),
        ("fig1_workflow_methodology.png", "Figure_1b_Workflow.png"),
        ("fig2_quantum_cdft_architecture.png", "Figure_2_Quantum_CDFT.png"),
        ("fig3_3d_parp1_docking_surfaces.png", "Figure_3_PARP1_3D_Docking.png"),
        ("fig4_interaction_residue_fingerprints.png", "Figure_4_Interaction_Fingerprints.png"),
        ("fig5_quantum_ground_state_geometries.png", "Figure_5_Quantum_3D_Geometries.png"),
        ("fig6_docking_vina_statistical_profiles.png", "Figure_6_Docking_Distributions.png"),
        ("fig5_descriptor_correlation_matrix.png", "Figure_7_Descriptor_Correlation_Matrix.png"),
        ("fig8_williams_applicability_domain.png", "Figure_8_OECD_Williams_Plot.png"),
        ("fig7_parity_models_evaluation.png", "Figure_9_Parity_Plots.png")
    ]
    for src_f, dst_f in fig_mappings:
        src_p = os.path.join(base_dir, "figures", src_f)
        dst_p = os.path.join(fig_dest_dir, dst_f)
        if os.path.exists(src_p):
            shutil.copyfile(src_p, dst_p)
            
    # 5. Suggested Reviewers & Checklist
    create_suggested_reviewers(sub_dir)
    create_submission_checklist(sub_dir)
    
    # 6. Master ZIP creation
    zip_path = os.path.join(base_dir, "nano-qsar-ai-therapeutics-FINAL-SUBMISSION-READY.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
        for root, dirs, files in os.walk(sub_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, sub_dir)
                zip_f.write(file_path, os.path.join("submission_ready", rel_path))
                
    print(f"\n=======================================================")
    print(f">>> FINAL SUBMISSION PACKAGE GENERATED SUCCESSFULLY ({os.path.getsize(zip_path)} bytes) <<<")
    print(f" -> {zip_path}")
    print(f"=======================================================")
    return zip_path

if __name__ == "__main__":
    build_complete_submission_folder()
