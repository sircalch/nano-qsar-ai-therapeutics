"""build_cover_letter.py - cover letter for Structural Chemistry (Word)."""
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docx_kit as k  # noqa: E402
from build_manuscript import AFFIL, AUTHOR, EMAIL, ORCID, load, stats  # noqa: E402

OUT = HERE.parents[1] / "manuscript" / "submission"


# status of the companion methods paper; submit it first, then build this letter
METHODS_STATUS = "submitted to the Journal of Computational Biophysics and Chemistry"

def main():
    d = load()
    s = stats(d)
    doc = k.new_document()
    for t in (AUTHOR, AFFIL, EMAIL, "", date.today().strftime("%d %B %Y"), "",
              "The Editor-in-Chief", "Structural Chemistry", ""):
        k.para(doc, t, align="left", space_after=0)
    k.para(doc, "Dear Editor,", align="left")
    k.para(doc,
           "I submit the manuscript \"Physisorption and dative-bond chemisorption of anti-TNBC drugs on a "
           "B_{36}N_{36} fullerene-like cage: validated PARP1 docking, GFN2-xTB adsorption and QSPR analysis\" "
           "for consideration as a Research article in Structural Chemistry.")
    k.para(doc,
           f"The study models {s['n']} drugs used against triple-negative breast cancer on a chemically valid "
           f"B_{{36}}N_{{36}} cage at the GFN2-xTB level and finds two binding regimes: {s['n_phys']} drugs "
           f"physisorb and {s['n_chem']} chemisorb through B–O or B–N dative bonds, with the bonding of every "
           "complex checked explicitly. Docking into PARP1 uses a protocol validated by two redocking controls "
           f"(RMSD {s['r_xtal']:.2f} and {s['r_smi']:.2f} Å). Descriptor-based QSPR models are evaluated with "
           "nested cross-validation and Y-scrambling and are reported as non-predictive, a negative result that "
           "I consider informative for carrier screening.")
    k.para(doc,
           "Related work. Supporting files of an earlier version of this study were deposited on Zenodo "
           "(https://doi.org/10.5281/zenodo.22700597); that version was superseded when the study was rebuilt from its raw "
           "inputs, and the results reported here replace it. A methods paper by the author, " + METHODS_STATUS + ", "
           "uses this study as one of four case studies of "
           "errors found and corrected during such rebuilds, and cites some of its summary numbers; the study "
           "is reported in full only in this manuscript.")
    k.para(doc,
           "All structures, relaxed geometries, docking poses and the complete pipeline that regenerates every "
           "number and figure are openly available. The manuscript is original, has not been published and is "
           "not under consideration elsewhere. The author declares no competing interests.")
    k.para(doc, "Sincerely,", align="left", space_after=0)
    k.para(doc, f"{AUTHOR} (ORCID {ORCID})", align="left")
    out = OUT / "Cover_Letter_StructChem.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
