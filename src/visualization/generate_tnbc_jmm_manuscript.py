"""
generate_tnbc_jmm_manuscript.py
=================================
Builds a Journal of Molecular Modeling (Springer) submission variant of the
TNBC/B36N36 manuscript. Does NOT touch the canonical Beilstein/Molecular
Diversity body produced by generate_beilstein_word_manuscript.py -- it
post-processes a freshly regenerated copy of that docx, same recipe as the
GBM/Tau JMM variants:

  1. Structured Context/Methods abstract (JMM requirement, 150-250 words).
     Unlike GBM/Tau, TNBC's abstract is a single inline paragraph ("Abstract: "
     bold label run + body run in the same paragraph, not a separate Heading +
     paragraph) so it is located/rebuilt differently here. Context is a
     condensed re-derivation of the original abstract with the
     dynamically-computed numbers (Vina mean/range, Q2_CV for both endpoints,
     n_phys) extracted via regex from the freshly generated text, never
     retyped by hand.
  2. Section reorder: JMM wants Methods to follow the Introduction. The
     Beilstein body instead puts "4. Experimental" after Conclusions.
     Moved + renumbered:
         1. Introduction            (unchanged)
         2. Experimental            (was "4.", subsections 4.1-4.4 -> 2.1-2.4)
         3. Results and Discussion  (was "2.", subsections 2.1-2.6 -> 3.1-3.6)
         4. Summary                 (was "3. Conclusions")
     The two in-text cross-references ("Section 2.1", "Section 2.2") are
     fixed to "Section 3.1" / "Section 3.2".
"""

import os
import re
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from docx import Document
from docx.shared import Pt

import generate_beilstein_word_manuscript as full_gen

JMM_METHODS = (
    "Each isolated drug, the pristine B36N36 cage, and every complex were geometry-optimized and evaluated at "
    "single point with GFN2-xTB (xtb v6.7.1, D4 dispersion, gas phase); reactivity indices were read directly "
    "from the xtb output. The human PARP1 catalytic domain (PDB ID: 4UND) was docked with AutoDock Vina v1.2.7; "
    "self-redocking did not reproduce the native pose within 2 Å, so scores are a relative ranking only. A "
    "four-descriptor RidgeCV surrogate was evaluated by a leak-free nested 5×5 cross-validation, with "
    "StandardScaler and Ridge strength fit only on each outer-training split; SHAP from an ExtraTrees fit "
    "ranked descriptors. The applicability domain follows OECD Principle 3 (Williams leverage)."
)


def _build_condensed_context(original_abstract):
    """Re-derive a <=150-word Context paragraph, extracting the dynamically
    computed numbers (Vina mean/range, Q2_CV for both endpoints, n_phys) with
    regex so they can never drift stale.
    """
    m_vina = re.search(r"mean ([\-0-9.]+) kcal/mol, range ([\-0-9. to]+)\)", original_abstract)
    m_q2 = re.search(r"Q2_CV = ([0-9.\-n/a]+), n = (\d+)\); the docking-score QSPR is no better \(Q2_CV = ([0-9.\-n/a]+)\)", original_abstract)
    if not (m_vina and m_q2):
        raise RuntimeError("Could not extract one or more dynamic values from the original TNBC abstract "
                            "-- source text likely changed; update the regexes in _build_condensed_context.")
    vina_mean, vina_range = m_vina.group(1), m_vina.group(2)
    q2_phys, n_phys, q2_vina = m_q2.group(1), m_q2.group(2), m_q2.group(3)

    return (
        "Triple-negative breast cancer (TNBC) lacks the estrogen, progesterone and HER2 receptors other "
        "subtypes can be targeted through. We evaluate the pristine inorganic boron nitride nanocage B36N36 as "
        "a drug-loading scaffold for 33 anti-TNBC therapeutics, combining GFN2-xTB adsorption modeling, "
        "AutoDock Vina docking against the human PARP1 catalytic domain (PDB ID: 4UND), and a leak-free "
        "cross-validated QSPR surrogate. Of 30 organic drugs modelled, 25 physisorb on the pristine cage "
        "(ΔE_int,SP = -6 to -31 kcal/mol) and 5 chemisorb, forming a covalent B-O or B-N bond (-43 to -186 "
        f"kcal/mol). Docking gave Vina scores (mean {vina_mean} kcal/mol, range {vina_range}), reported only as "
        f"an exploratory ranking since self-redocking failed within 4 Å. QSPR is non-predictive for both "
        f"endpoints (Q2_CV = {q2_phys}, n = {n_phys}, physisorption; Q2_CV = {q2_vina}, docking) -- the "
        "chemisorption/physisorption dichotomy itself is the honest result of this exploratory study."
    )


def _find_heading(doc, text_exact=None):
    for i, p in enumerate(doc.paragraphs):
        if not p.style.name.startswith("Heading"):
            continue
        if text_exact is not None and p.text.strip() == text_exact:
            return i, p
    raise RuntimeError(f"Heading not found: {text_exact}")


def generate_tnbc_jmm_manuscript():
    full_gen.build_manuscript_word()

    src_docx = os.path.join(base_dir, "manuscript", "Beilstein_Manuscript_Monreal_Hernandez_et_al.docx")
    doc = Document(src_docx)

    # ---------------------------------------------------------------
    # 1) Structured Context/Methods abstract
    #    (TNBC's abstract is one paragraph: "Abstract: " bold run + body run)
    # ---------------------------------------------------------------
    abs_para_idx = None
    for i, p in enumerate(doc.paragraphs):
        if p.runs and p.runs[0].text.strip() == "Abstract:":
            abs_para_idx = i
            break
    if abs_para_idx is None:
        raise RuntimeError("Could not find the inline 'Abstract:' paragraph in the TNBC manuscript.")

    abstract_para = doc.paragraphs[abs_para_idx]
    original_abstract = "".join(r.text for r in abstract_para.runs[1:])  # skip the "Abstract: " label run
    context_text = _build_condensed_context(original_abstract)

    p_context = abstract_para.insert_paragraph_before()
    p_context.paragraph_format.space_after = abstract_para.paragraph_format.space_after
    p_context.paragraph_format.line_spacing = abstract_para.paragraph_format.line_spacing
    r1 = p_context.add_run("Context ")
    r1.font.bold = True
    p_context.add_run(context_text)

    p_methods = abstract_para.insert_paragraph_before()
    p_methods.paragraph_format.space_after = abstract_para.paragraph_format.space_after
    p_methods.paragraph_format.line_spacing = abstract_para.paragraph_format.line_spacing
    r2 = p_methods.add_run("Methods ")
    r2.font.bold = True
    p_methods.add_run(JMM_METHODS)

    abstract_para._element.getparent().remove(abstract_para._element)

    # ---------------------------------------------------------------
    # 2) Move "4. Experimental" (+ its subsections) to right after Introduction
    # ---------------------------------------------------------------
    exp_idx, _ = _find_heading(doc, text_exact="4. Experimental")
    data_avail_idx, _ = _find_heading(doc, text_exact="Data Availability")
    results_idx, results_head = _find_heading(doc, text_exact="2. Results and Discussion")

    elements_to_move = [doc.paragraphs[i]._p for i in range(exp_idx, data_avail_idx)]
    anchor_element = results_head._p
    for el in elements_to_move:
        anchor_element.addprevious(el)

    # ---------------------------------------------------------------
    # 3) Renumber headings
    # ---------------------------------------------------------------
    _, exp_head = _find_heading(doc, text_exact="4. Experimental")
    exp_head.runs[0].text = "2. Experimental"

    _, results_head2 = _find_heading(doc, text_exact="2. Results and Discussion")
    results_head2.runs[0].text = "3. Results and Discussion"

    exp_subsection_renumber = {
        "4.1 Curated Anti-TNBC Therapeutic Library": "2.1 Curated Anti-TNBC Therapeutic Library",
        "4.2 Quantum-chemical framework": "2.2 Quantum-chemical framework",
        "4.3 Molecular docking against human PARP1 (PDB 4UND)": "2.3 Molecular docking against human PARP1 (PDB 4UND)",
        "4.4 Machine Learning, Explainable AI (SHAP), and OECD Validation": "2.4 Machine Learning, Explainable AI (SHAP), and OECD Validation",
    }
    results_subsection_renumber = {
        "2.1 Quantum conceptual-DFT reactivity of the isolated therapeutics": "3.1 Quantum conceptual-DFT reactivity of the isolated therapeutics",
        "2.2 Physical Molecular Docking on PARP1 and Active Site Relocation": "3.2 Physical Molecular Docking on PARP1 and Active Site Relocation",
        "2.3 3D Quantum Geometries and Intermolecular Interactions": "3.3 3D Quantum Geometries and Intermolecular Interactions",
        "2.4 Statistical Docking Distributions and Residue Interactions": "3.4 Statistical Docking Distributions and Residue Interactions",
        "2.5 Machine Learning Benchmarking and Explainable AI (SHAP)": "3.5 Machine Learning Benchmarking and Explainable AI (SHAP)",
        "2.6 Explicit Analytical QSAR Mathematical Models": "3.6 Explicit Analytical QSAR Mathematical Models",
    }
    # NOTE: apply exp_subsection_renumber BEFORE results_subsection_renumber -- both start
    # with "2.x" but refer to different sections; after the move, headings are searched by
    # their OLD text (still "4.x" / "2.x" at this point since only top-level "2."/"4." were
    # renamed above), so there is no collision.
    for old, new in exp_subsection_renumber.items():
        _, h = _find_heading(doc, text_exact=old)
        h.runs[0].text = new
    for old, new in results_subsection_renumber.items():
        _, h = _find_heading(doc, text_exact=old)
        h.runs[0].text = new

    _, concl_head = _find_heading(doc, text_exact="3. Conclusions")
    concl_head.runs[0].text = "4. Summary"

    # Fix in-text cross-references (old Results 2.1/2.2 are now Results 3.1/3.2)
    for p in doc.paragraphs:
        for r in p.runs:
            if "Section 2.2" in r.text:
                r.text = r.text.replace("Section 2.2", "Section 3.2")
            if "Section 2.1" in r.text:
                r.text = r.text.replace("Section 2.1", "Section 3.1")

    out_dir = os.path.join(base_dir, "manuscript", "submission_ready")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "02_Manuscript_TNBC_B36N36_JMM_Submission.docx")
    doc.save(out_path)
    print(f"[SUCCESS] Generated JMM submission manuscript: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_tnbc_jmm_manuscript()
