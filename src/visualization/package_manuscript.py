"""
package_manuscript.py
Packages the LaTeX manuscript, BibTeX references, supplementary info, and high-resolution figures
into a ready-to-use Overleaf / Journal submission ZIP file.
"""

import os
import zipfile
import glob

def create_submission_package():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    zip_path = os.path.join(base_dir, "nano-qsar-ai-therapeutics-Submission-Package.zip")
    
    files_to_pack = [
        os.path.join(base_dir, "manuscript", "manuscript.tex"),
        os.path.join(base_dir, "manuscript", "references.bib"),
        os.path.join(base_dir, "manuscript", "manuscript.md"),
        os.path.join(base_dir, "manuscript", "supplementary_info.md"),
        os.path.join(base_dir, "README.md")
    ]
    
    fig_files = glob.glob(os.path.join(base_dir, "figures", "*.png"))
    data_files = [
        os.path.join(base_dir, "results", "docking", "real_vina_docking_summary.csv"),
        os.path.join(base_dir, "results", "docking", "real_residue_interactions.csv"),
        os.path.join(base_dir, "results", "models", "qsar_models_benchmark_summary.json")
    ]
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_f:
        for f in files_to_pack:
            if os.path.exists(f):
                zip_f.write(f, os.path.basename(f))
                
        for fig in fig_files:
            if os.path.exists(fig):
                zip_f.write(fig, os.path.join("figures", os.path.basename(fig)))
                
        for d in data_files:
            if os.path.exists(d):
                zip_f.write(d, os.path.join("data", os.path.basename(d)))
                
    print(f"Successfully generated complete submission ZIP package ({os.path.getsize(zip_path)} bytes):")
    print(f" -> {zip_path}")
    return zip_path

if __name__ == "__main__":
    create_submission_package()
