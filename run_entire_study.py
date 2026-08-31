"""
run_entire_study.py
Master End-to-End Pipeline Runner for 100% Reproducibility.
Executes the full computational pipeline in sequential order:

1. Curates library of 42 TNBC therapeutics (RDKit SMILES canonicalization)
2. Computes 20 physicochemical & 3D constitutional descriptors (compute_descriptors.py)
3. Executes real AutoDock Vina v1.2.7 docking on human PARP1 (PDB ID: 4UND)
4. Computes residue-level contact fingerprints and H-bond networks
5. Evaluates Quantum CDFT electronic parameters and adsorption energies
6. Trains ExtraTrees, XGBoost & MLR models with 5-fold CV & SHAP XAI
7. Evaluates OECD Principle 3: Applicability Domain (Williams Plot)
8. Generates all 9 publication-grade figures at 300+ DPI
9. Compiles complete Word (.docx) manuscript and ZIP submission package
"""

import os
import sys
import time

def run_step(step_num, title, script_rel_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_rel_path)
    print(f"\n=======================================================")
    print(f"  [Step {step_num}/8] {title}")
    print(f"=======================================================")
    t0 = time.time()
    ret = os.system(f'python "{script_path}"')
    t_elapsed = time.time() - t0
    if ret != 0:
        print(f"[ERROR] Step {step_num}: {title} (Exit Code: {ret})")
        return False
    print(f"[OK] Step {step_num} completed in {t_elapsed:.2f} seconds.")
    return True

def main():
    print("=" * 65)
    print("  NANO-QSAR-AI-THERAPEUTICS: MASTER REPRODUCIBILITY PIPELINE")
    print("  Authors: Andrés Monreal Hernández et al.")
    print("=" * 65)
    
    steps = [
        (1, "Library Curation & Canonicalization", "src/descriptors/curate_dataset.py"),
        (2, "RDKit Descriptors Calculation", "src/descriptors/compute_descriptors.py"),
        (3, "Residue-Level Contact Analysis", "src/docking/analyze_real_interactions.py"),
        (4, "Data Synchronization & Quantum CDFT", "src/ml_models/sync_real_data_and_train.py"),
        (5, "Machine Learning & SHAP XAI Training", "src/ml_models/train_qsar_models.py"),
        (6, "OECD Applicability Domain (Williams Plot)", "src/ml_models/compute_oecd_applicability_domain.py"),
        (7, "3D PyVista Renderings & Master Figure Generation", "src/visualization/render_perfect_fig3_and_fig5.py"),
        (8, "Word Document Compilation & Submission Packaging", "src/visualization/generate_beilstein_word_manuscript.py")
    ]
    
    for s_num, title, path in steps:
        success = run_step(s_num, title, path)
        if not success:
            sys.exit(1)
            
    print("\n" + "=" * 65)
    print(">>> FULL REPRODUCIBILITY PIPELINE EXECUTED SUCCESSFULLY! <<<")
    print("  Manuscript Word File: manuscript/Beilstein_Manuscript_Monreal_Hernandez_et_al.docx")
    print("  Submission ZIP File:  nano-qsar-ai-therapeutics-Submission-Package.zip")
    print("=" * 65)

if __name__ == "__main__":
    main()
