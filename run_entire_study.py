"""
run_entire_study.py
Master end-to-end pipeline for the TNBC / B36N36 nanocage study.
Reproduces the real numbers and figures in the Beilstein manuscript.

NOTE (2026-09-08): the B36N36 adsorption dataset was fully recomputed with
relaxed complexes by `recompute_tnbc_adsorption.py` (commit b80c25e). That step
is GFN2-xTB heavy (~2 h, needs xtb on PATH) and its outputs
(data/processed/dataset_tnbc_bn_pristine.csv, relaxed_adsorption_subset.csv,
calculations/tnbc_recompute/*/result.json) are committed, so this master
pipeline consumes them rather than regenerating them. To rebuild from scratch:
    python recompute_tnbc_adsorption.py --nproc 5
    python recompute_tnbc_adsorption.py --commit-datasets
Result: 30 organic drugs modelled = 25 physisorb / 5 chemisorb; 3 Pt(II) agents
not modelled. QSPR is non-predictive on both endpoints (Vina Q2_CV = 0.11,
physisorption Q2_CV = 0.0).
"""
import os
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))


def run_step(n, total, title, rel_path, args=""):
    script = os.path.join(BASE, rel_path)
    print(f"\n{'='*70}\n  [Step {n}/{total}] {title}\n{'='*70}")
    t0 = time.time()
    ret = os.system(f'python "{script}" {args}')
    if ret != 0:
        print(f"[ERROR] Step {n}: {title} (exit {ret})")
        return False
    print(f"[OK] Step {n} in {time.time()-t0:.1f}s")
    return True


def main():
    print("=" * 70)
    print("  TNBC / B36N36 NANOCAGE : MASTER REPRODUCIBILITY PIPELINE")
    print("=" * 70)
    steps = [
        ("Library curation & canonicalization", "src/descriptors/curate_dataset.py"),
        ("RDKit + GFN2-xTB descriptors", "src/descriptors/compute_descriptors.py"),
        ("Real AutoDock Vina docking (PARP1, PDB 4UND)", "src/docking/run_real_vina_docking.py"),
        ("Residue-level contact analysis", "src/docking/analyze_real_interactions.py"),
        ("OECD applicability domain (Williams)", "src/ml_models/compute_oecd_applicability_domain.py"),
        ("Figure suite (fig 1-9)", "src/visualization/generate_all_q1_figures.py"),
        ("Master 3D + docking-coupling figures (fig 3, 6)", "src/visualization/generate_master_q1_figure_set.py"),
        ("3D geometry renders + Delta-rho + adsorption landscape (fig 5, 10, 11)", "src/visualization/render_perfect_fig3_and_fig5.py"),
        ("Beilstein Word manuscript", "src/visualization/generate_beilstein_word_manuscript.py"),
        ("Supporting information", "src/visualization/generate_supporting_information.py"),
    ]
    for i, (title, path) in enumerate(steps, 1):
        if not run_step(i, len(steps), title, path):
            sys.exit(1)
    print("\n" + "=" * 70)
    print(">>> PIPELINE COMPLETE <<<")
    print("  manuscript/Beilstein_Manuscript_Monreal_Hernandez_et_al.docx")
    print("=" * 70)


if __name__ == "__main__":
    main()
