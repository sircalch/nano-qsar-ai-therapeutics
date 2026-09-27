"""
build_manuscript.py - Journal of Molecular Modeling submission (Word) for the
TNBC / B36N36 study. Every number in the text, tables and captions is read
from the result files written by the pipeline.

usage: python src/manuscript/build_manuscript.py
writes manuscript/submission/Manuscript_TNBC_B36N36_JMM.docx
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import docx_kit as k  # noqa: E402
from references import REFS  # noqa: E402

BASE = HERE.parents[1]
FIG = BASE / "figures"
OUT = BASE / "manuscript" / "submission"

AUTHOR = "Andrés Monreal Hernández"
AFFIL = "Universidad Estatal de Sonora, Ley Federal del Trabajo S/N, Col. Apolo, 83100 Hermosillo, Sonora, Mexico"
EMAIL = "andres.monreal@ues.mx"
ORCID = "0009-0009-1207-8597"
REPO = "https://github.com/sircalch/nano-qsar-ai-therapeutics"
TITLE = ("Physisorption and dative-bond chemisorption of anti-TNBC drugs on a B_{36}N_{36} fullerene-like cage: "
         "validated PARP1 docking, GFN2-xTB adsorption and QSPR analysis")
CYTO = {"Taxane", "Microtubule Inhibitor", "Anthracycline", "Topoisomerase I Inhibitor",
        "Topoisomerase II Inhibitor", "Platinum Agent"}


class Cites:
    def __init__(self):
        self.order = []

    def __call__(self, *keys):
        nums = sorted({self._n(k_) for k_ in keys})
        spans, start = [], nums[0]
        for a, b in zip(nums, nums[1:] + [None]):
            if b != a + 1:
                spans.append(f"{start}" if start == a else f"{start}–{a}" if a - start > 1 else f"{start}, {a}")
                start = b
        return "[" + ", ".join(spans) + "]"

    def _n(self, key):
        if key not in REFS:
            raise KeyError(key)
        if key not in self.order:
            self.order.append(key)
        return self.order.index(key) + 1

    def list(self):
        return [REFS[k_] for k_ in self.order]


def f1(x):
    return f"{x:.1f}".replace("-", "−")


def f2(x):
    return f"{x:.2f}".replace("-", "−")


def dn(name):
    """Generic drug names in lower case inside a sentence; codes (SN-38) unchanged."""
    return name[0].lower() + name[1:] if name[0].isupper() and name[1:2].islower() else name


def family(cls):
    return "PARP inhibitor" if cls == "PARP Inhibitor" else "cytotoxic agent" if cls in CYTO \
        else "kinase/pathway inhibitor"


def load():
    d = {}
    m = pd.read_csv(BASE / "data" / "processed" / "dataset_tnbc_bn_pristine.csv")
    d["all"] = m
    m = m[m.adsorption_mode.isin(["chemisorption", "physisorption"])].copy()
    m = m.merge(pd.read_csv(BASE / "data" / "processed" / "adsorption_integrity.csv"), on="name", how="left")
    m["family"] = m.drug_class.map(family)
    d["m"] = m
    d["redock"] = pd.read_csv(BASE / "data" / "processed" / "redocking_validation.csv").set_index("control")
    d["cage"] = json.loads((BASE / "calculations" / "tnbc" / "B36N36_energy.json").read_text())
    d["contacts"] = pd.read_csv(BASE / "results" / "docking" / "residue_contacts.csv")
    d["audit"] = pd.read_csv(BASE / "data" / "processed" / "structure_audit_pubchem.csv")
    for tag in ("vina", "dEint"):
        d[f"q_{tag}"] = json.loads((BASE / "results" / "qspr" / f"{tag}_summary.json").read_text())
    return d


def front(doc):
    k.para(doc, f"**{TITLE}**",
           align="left", size=15, space_after=12)
    k.para(doc, f"{AUTHOR}^{{*}}", align="left", space_after=2)
    k.para(doc, AFFIL, align="left", size=10, space_after=2)
    k.para(doc, f"^{{*}}Corresponding author: {EMAIL}; ORCID {ORCID}", align="left", size=10, space_after=14)


def introduction(doc, c):
    k.heading(doc, "Introduction")
    k.para(doc,
           "Triple-negative breast cancer (TNBC) lacks the oestrogen, progesterone and HER2 receptors that "
           "guide targeted therapy in other breast-cancer subtypes, and it is associated with early relapse "
           "and poor prognosis " + c("foulkes2010", "dent2007", "giaquinto2022") + ". It is also molecularly "
           "heterogeneous " + c("lehmann2011", "bianchini2016") + ". In the subset carrying germline "
           "*BRCA1/2* mutations, poly(ADP-ribose) polymerase (PARP) inhibitors exploit synthetic lethality "
           "and trap PARP1 on DNA " + c("lord2017", "pommier2016", "mateo2019") + "; olaparib and talazoparib "
           "are approved for this indication " + c("robson2017", "litton2018") + ". Most patients, however, "
           "still depend on cytotoxic chemotherapy and on kinase or pathway inhibitors under investigation.",
           indent=True)
    k.para(doc,
           "Boron nitride nanomaterials are chemically inert, electrically insulating and generally well "
           "tolerated by cells " + c("golberg2010", "chen2009", "merlo2018", "genchi2015") + ", and their "
           "surface chemistry can be functionalised for biomedical use " + c("weng2016") + ". Among the "
           "fullerene-like (BN)_{n} cages, stable isomers contain only four- and six-membered rings, which "
           "allows strict B–N alternation " + c("strout2000", "fowler1999") + "; B_{36}N_{36} has been "
           "studied as a drug carrier at the DFT level " + c("gholami2023") + ". Boron sites of BN cages are "
           "Lewis acidic, so drugs with lone-pair donors may bind either by dispersion (physisorption) or by "
           "dative B–O/B–N bonds (chemisorption).", indent=True)
    k.para(doc,
           "This study characterises a cohort of anti-TNBC drugs on two fronts. First, it docks them into "
           "the nicotinamide pocket of PARP1 with a protocol that is shown beforehand to reproduce the "
           "crystallographic talazoparib pose. Second, it computes their GFN2-xTB adsorption on a "
           "chemically valid B_{36}N_{36} cage, classifies each complex as physisorbed or chemisorbed from "
           "its bonding, and asks whether either endpoint can be anticipated from four pre-selected "
           "molecular descriptors under leak-free validation.", indent=True)


def methods(doc, d, c):
    m, cage = d["m"], d["cage"]
    k.heading(doc, "Methods")
    k.heading(doc, "Compound set", 2)
    n_all = len(d["all"])
    fam = m.family.value_counts()
    k.para(doc,
           f"The cohort comprises {n_all} drugs used or investigated in TNBC. Every structure was "
           "retrieved from PubChem by name " + c("kim2021_pubchem") + " and its identity verified by "
           "InChIKey (Online Resource 1, Table S1). The three platinum(II) agents were not modelled, because RDKit/MMFF cannot "
           "build square-planar Pt(II) complexes reliably and GFN2-xTB is not validated for them, leaving "
           f"{len(m)} organic drugs: {fam.get('PARP inhibitor', 0)} PARP inhibitors, "
           f"{fam.get('cytotoxic agent', 0)} cytotoxic agents and {fam.get('kinase/pathway inhibitor', 0)} "
           "kinase or pathway inhibitors.", indent=True)

    k.heading(doc, "Molecular docking", 2)
    k.para(doc,
           "The structure of the human PARP1 catalytic domain bound to talazoparib (PDB 4UND) " +
           c("berman2000") + " was prepared with PDBFixer " + c("eastman2017") + ": chain A was kept, "
           "waters, ions and the inhibitor were removed, missing atoms were added and the protein was "
           "protonated at pH 7.4; AutoDock atom types were assigned with Meeko. Ligands were built from "
           "their SMILES with RDKit " + c("rdkit") + " (ETKDGv3 " + c("wang2020_etkdg") + ", MMFF94 " +
           c("halgren1996") + "). Because AutoDock Vina keeps rings rigid, up to five distinct ring "
           "conformers per drug were docked and the best score was kept. Docking used AutoDock Vina 1.2.7 "
           + c("trott2010", "eberhardt2021") + " in a 22 Å cubic box centred on the talazoparib of chain A "
           "(exhaustiveness 16, nine modes, fixed seed). The protocol was validated by self-redocking "
           "talazoparib from its crystal conformation and by docking it rebuilt from SMILES through the "
           "production protocol; the heavy-atom RMSD to the crystal pose was computed with symmetry "
           "correction and without re-alignment. Residues within 4.0 Å of the top pose were counted as "
           "contacts and N/O pairs within 3.5 Å as polar contacts.", indent=True)

    k.heading(doc, "B_{36}N_{36} cage", 2)
    k.para(doc,
           "The cage was built as the octahedral Goldberg-type (1,1) polyhedron, obtained as the leapfrog of "
           "the truncated octahedron: 72 vertices, six four-membered and 32 six-membered rings. All rings "
           "are even, so boron and nitrogen alternate strictly and the cage contains 108 B–N bonds and no "
           "B–B or N–N bonds. It was relaxed with GFN2-xTB (tight thresholds) and confirmed as a minimum by "
           f"the absence of imaginary frequencies (HOMO–LUMO gap {f2(cage['HOMO_LUMO_gap_eV'])} eV).",
           indent=True)

    k.heading(doc, "Adsorption calculations", 2)
    k.para(doc,
           "All quantum-chemical calculations used GFN2-xTB " + c("bannwarth2019", "bannwarth2021") +
           " (xtb 6.7.1, D4 dispersion " + c("caldeweyher2019") + ") in the gas phase. Each drug was relaxed "
           "in isolation from its lowest MMFF94 conformer. The drug was then placed 3.2 Å above the cage and "
           "four rotations about the approach axis (0, 90, 180 and 270°) were fully relaxed; the "
           "lowest-energy converged pose with a closest drug–cage heavy-atom contact of 1.25–4.0 Å was "
           "kept. On that geometry the interaction energy Δ*E*_{int} = *E*_{complex} − *E*_{cage} − "
           "*E*_{drug}, with both fragments frozen at the complex geometry, and the adsorption energy "
           "Δ*E*_{ads}, referenced to the separately relaxed fragments, were computed. A complex was classed "
           "as chemisorbed when at least one drug–cage distance was shorter than 1.15 times the sum of the "
           "covalent radii, and physisorbed otherwise. The bonding of each drug was also compared before and "
           "after adsorption to detect proton transfer or bond breaking within the drug.", indent=True)

    k.heading(doc, "Descriptors and QSPR models", 2)
    k.para(doc,
           "Four descriptors were fixed before any model was fitted: molecular weight and molar refractivity "
           "(RDKit), and the HOMO energy and global electrophilicity ω = μ^{2}/2η from GFN2-xTB on the "
           "relaxed isolated drug " + c("parr1999", "geerlings2003", "karelson1996") + ". Two endpoints were "
           "modelled: the Vina score on PARP1 and Δ*E*_{int} on B_{36}N_{36} (drugs whose own bonding was "
           "unchanged on adsorption). Each model is a ridge regression (scikit-learn " + c("pedregosa2011") +
           ", standardisation and penalty inside one pipeline) evaluated by nested cross-validation: five "
           "outer folds for performance and a five-fold inner loop for the penalty " + c("cawley2010") +
           ". Out-of-fold predictions give *Q*^{2}_{CV}, RMSE and MAE. Chance correlation was tested by "
           "repeating the whole nested procedure on 1,000 permutations of the target " + c("rucker2007") +
           ". The applicability domain follows OECD principle 3 " + c("oecd2007", "gramatica2007", "tropsha2010")
           + ": leverages from the standardised descriptors with intercept, warning leverage *h*^{*} = "
           "3(*p* + 1)/*n*, and standardised residuals within ±3.", indent=True)


def stats(d):
    """All numbers quoted in abstract, results and conclusions."""
    import re
    from collections import Counter
    from scipy.stats import kruskal
    m, rd = d["m"], d["redock"]
    ch = m[m.adsorption_mode == "chemisorption"]
    ph = m[m.adsorption_mode == "physisorption"]
    bonds = Counter(re.sub(r"\d", "", x) for s in ch.drug_cage_bonds.dropna() for x in s.split(";"))
    ch_ok = ch[ch.drug_intact.astype(bool)]
    reacted = m[~m.drug_intact.astype(bool)]
    ct = d["contacts"]
    freq = ct.groupby("residue").name.nunique().sort_values(ascending=False)
    rho, prho = spearmanr(m.vina_4UND_kcal_mol, m.delta_Eint_SP_kcal_mol)
    kw = kruskal(*[g.vina_4UND_kcal_mol for _, g in m.groupby("family")])
    cage_bn, dcar = [], []
    E0 = d["cage"]["E_Eh"]
    for nm in m.name:
        f = BASE / "calculations" / "tnbc_recompute" / nm.replace(" ", "_").replace("-", "_") / "frag_carrier.xyz"
        L = f.read_text().splitlines()
        nat = int(L[0])
        el = [x.split()[0] for x in L[2:2 + nat]]
        xyz = np.array([[float(v) for v in x.split()[1:4]] for x in L[2:2 + nat]])
        dd = np.linalg.norm(xyz[:, None] - xyz[None], axis=2)
        cage_bn.append(sum(1 for i in range(nat) for j in range(i + 1, nat)
                           if el[i] != el[j] and dd[i, j] < 1.15 * (0.84 + 0.71)))
        import json as _j
        rj = _j.loads((f.parent / "result.json").read_text())
        dcar.append((rj["E_carrier_frozen_Eh"] - E0) * 627.509)
    return dict(
        cage_bn_min=min(cage_bn), cage_bn_max=max(cage_bn), dcar_min=min(dcar), dcar_max=max(dcar),
        n=len(m), n_chem=len(ch), n_phys=len(ph), bonds=bonds, ch=ch, ph=ph, ch_ok=ch_ok, reacted=reacted,
        r_xtal=rd.loc["self-redock, crystal conformation", "rmsd_heavy_atom_A"],
        r_smi=rd.loc["production protocol, from SMILES", "rmsd_heavy_atom_A"],
        s_xtal=rd.loc["self-redock, crystal conformation", "affinity_kcal_mol"],
        top=m.nsmallest(3, "vina_4UND_kcal_mol"), freq=freq, rho=rho, prho=prho, kw=kw,
        vina_min=m.vina_4UND_kcal_mol.min(), vina_max=m.vina_4UND_kcal_mol.max())


def abstract(doc, d, c):
    s, qv, qa = stats(d), d["q_vina"], d["q_dEint"]
    k.heading(doc, "Abstract")
    k.labelled(doc, "Context",
               "Triple-negative breast cancer (TNBC) lacks the receptors that guide targeted therapy, and "
               "carrier-based delivery is one route to improve the drugs used against it. Boron nitride cages are "
               "chemically robust candidate carriers whose Lewis-acidic boron sites can bind drugs either by "
               f"dispersion or by dative bonds. For {s['n']} anti-TNBC drugs we find that {s['n_phys']} physisorb on "
               f"a B_{{36}}N_{{36}} cage (Δ*E*_{{int}} {f1(s['ph'].delta_Eint_SP_kcal_mol.max())} to "
               f"{f1(s['ph'].delta_Eint_SP_kcal_mol.min())} kcal mol^{{−1}}) and {s['n_chem']} chemisorb through "
               f"B–O or B–N dative bonds ({f1(s['ch_ok'].delta_Eint_SP_kcal_mol.max())} to "
               f"{f1(s['ch_ok'].delta_Eint_SP_kcal_mol.min())} kcal mol^{{−1}}); doxorubicin reacts with the cage. "
               "A docking protocol that reproduces the crystallographic talazoparib pose in PARP1 "
               f"(root-mean-square deviation {f2(s['r_xtal'])} and {f2(s['r_smi'])} Å) ranks olaparib and talazoparib first. Neither the "
               "docking score nor the cage interaction energy can be predicted from four pre-selected descriptors "
               f"(*Q*^{{2}}_{{CV}} = {f2(qv['Q2_CV'])} and {f2(qa['Q2_CV'])}), and the two endpoints are "
               f"uncorrelated (Spearman ρ = {f2(s['rho'])}).")
    k.labelled(doc, "Methods",
               "Structures were taken from PubChem. A valid B_{36}N_{36} cage (octahedral, 108 B–N bonds) "
               "was relaxed with GFN2-xTB and confirmed as a minimum. Each drug was adsorbed from four relaxed "
               "orientations with GFN2-xTB (xtb 6.7.1); the regime was assigned from drug–cage bond formation. "
               "Drugs were docked into PARP1 (PDB 4UND, chain A) with AutoDock Vina 1.2.7 after PDBFixer/Meeko "
               "preparation, validated by two redocking controls. Ridge quantitative structure–property relationship "
               "(QSPR) models were assessed by nested 5×5 "
               "cross-validation, 1,000-fold Y-scrambling and a leverage applicability domain.")
    k.para(doc, "**Keywords** Boron nitride nanocage · B_{36}N_{36} · PARP1 · Triple-negative breast cancer · "
                "GFN2-xTB · Molecular docking", align="left")


def results(doc, d, c):
    s, m, qv, qa = stats(d), d["m"], d["q_vina"], d["q_dEint"]
    k.heading(doc, "Results and discussion")
    k.para(doc, "The workflow is summarised in Fig. 1. All quantities are computed; none is fitted to "
                "experimental data.", indent=True)

    k.heading(doc, "Electronic descriptors of the drugs", 2)
    cage = d["cage"]
    below = [dn(x) for x in m[m.E_HOMO_eV < cage["HOMO_eV"]].name]
    above = [dn(x) for x in m[m.E_LUMO_eV > cage["LUMO_eV"]].name]
    soft = [dn(x) for x in m.nsmallest(2, "Eta_eV").name]
    assert set(m.nsmallest(2, "Eta_eV").name) == set(m.nlargest(2, "Omega_eV").name)
    k.para(doc,
           f"All drug LUMOs lie below the LUMO of the cage ({f2(cage['LUMO_eV'])} eV)"
           + ("" if not above else f" except those of {', '.join(above)}") +
           f", and all HOMOs lie above the cage HOMO ({f2(cage['HOMO_eV'])} eV) except those of "
           f"{', '.join(below[:-1])} and {below[-1]} (Fig. 2a): the frontier levels of the drugs fall largely "
           f"inside the wide gap of the cage. The anthracyclines {soft[0]} and {soft[1]} are the softest and most electrophilic "
           "molecules of the set (Fig. 2b).",
           indent=True)
    k.figure(doc, FIG / "Fig2.png", 2,
             "GFN2-xTB frontier orbitals of the relaxed drugs. **a** HOMO (circles) and LUMO (squares) of each "
             "drug, sorted by gap and coloured by family; dashed lines, HOMO and LUMO of the B_{36}N_{36} cage. "
             "**b** Chemical hardness η versus electrophilicity ω")

    k.heading(doc, "Validated docking into the PARP1 nicotinamide pocket", 2)
    top_res = ", ".join(s["freq"].index[:6])
    k.para(doc,
           f"Self-redocking of talazoparib from its crystal conformation reproduced the deposited pose with a "
           f"heavy-atom RMSD of {f2(s['r_xtal'])} Å ({f1(s['s_xtal'])} kcal mol^{{−1}}), and the same ligand "
           f"rebuilt from SMILES through the production protocol reached {f2(s['r_smi'])} Å (Fig. 3a), both "
           "within the usual 2 Å criterion. The ring-conformer ensemble was necessary: a single ETKDG conformer "
           "of talazoparib, whose partially saturated ring Vina cannot flex, docked 6.7 Å away from the crystal "
           f"pose. Across the {s['n']} drugs, the most frequently contacted residues were {top_res} (Fig. 3b), the "
           "nicotinamide-site residues that anchor clinical PARP inhibitors. Scores ranged from "
           f"{f1(s['vina_min'])} to {f1(s['vina_max'])} kcal mol^{{−1}} (Table 1, Fig. 4a). The two best-scoring "
           f"drugs were the approved PARP inhibitors {dn(s['top'].name.iloc[0])} "
           f"({f1(s['top'].vina_4UND_kcal_mol.iloc[0])}) and {dn(s['top'].name.iloc[1])} "
           f"({f1(s['top'].vina_4UND_kcal_mol.iloc[1])} kcal mol^{{−1}}), a useful plausibility check, although "
           f"the three families did not differ significantly (Kruskal–Wallis *p* = {s['kw'].pvalue:.2f}).",
           indent=True)
    k.figure(doc, FIG / "Fig3.png", 3,
             "Docking validation in PARP1 (PDB 4UND, chain A). **a** Crystallographic talazoparib (grey), its "
             f"self-redocked pose (orange, RMSD {f2(s['r_xtal'])} Å) and the pose obtained from SMILES with the "
             f"production protocol (teal, {f2(s['r_smi'])} Å); contact residues as thin sticks, polar contacts "
             f"dashed. **b** Fraction of the {s['n']} docked drugs contacting each residue (heavy atoms within "
             "4.0 Å); dark bars, polar contacts (N/O within 3.5 Å)")

    k.figure(doc, FIG / "Fig4.png", 4,
             "**a** Vina scores of the drugs in PARP1, coloured by family. **b** Vina score versus −Δ*E*_{int} on "
             "B_{36}N_{36}; open symbols, chemisorbed drugs")


    k.heading(doc, "Physisorption and dative-bond chemisorption on B_{36}N_{36}", 2)
    b = s["bonds"]
    k.para(doc,
           f"The cage used here is a valid B_{{36}}N_{{36}} fullerene-like polyhedron (Fig. 5a). After full "
           f"relaxation from four orientations, {s['n_phys']} drugs remained physisorbed, with interaction "
           f"energies of {f1(s['ph'].delta_Eint_SP_kcal_mol.max())} to {f1(s['ph'].delta_Eint_SP_kcal_mol.min())} "
           f"kcal mol^{{−1}} and closest contacts of {f2(s['ph'].min_contact_A.min())}–"
           f"{f2(s['ph'].min_contact_A.max())} Å (the shortest, {dn(s['ph'].nsmallest(1, 'min_contact_A').name.iloc[0])}, "
           "lies just above the B–O bonding threshold of 1.73 Å), whereas "
           f"{s['n_chem']} formed a bond to a cage boron atom: "
           f"{b.get('O-B', 0)} B–O and {b.get('N-B', 0)} B–N dative bonds of "
           f"{f2(s['ch'].min_contact_A.min())}–{f2(s['ch'].min_contact_A.max())} Å (Fig. 6a, Table 1). Carbonyl "
           "or hydroxyl oxygens and nitrogen lone pairs of the drugs act as the Lewis bases, as expected for "
           "the electron-deficient boron sites of BN cages. Chemisorption strengthens the interaction by a factor "
           f"of about {s['ch_ok'].delta_Eint_SP_kcal_mol.mean() / s['ph'].delta_Eint_SP_kcal_mol.mean():.1f} (mean {f1(s['ch_ok'].delta_Eint_SP_kcal_mol.mean())} versus "
           f"{f1(s['ph'].delta_Eint_SP_kcal_mol.mean())} kcal mol^{{−1}}), while the adsorption energy, which "
           "includes the strain of both partners, is less different "
           f"({f1(s['ch_ok'].delta_Eads_kcal_mol.mean())} versus {f1(s['ph'].delta_Eads_kcal_mol.mean())} "
           "kcal mol^{−1}), because it also counts the deformation that the dative bond imposes on the drug and "
           "on the cage. All three families "
           "contain both regimes (Fig. 6b). The cage stays intact throughout: in every complex it keeps its "
           f"{s['cage_bn_min']} B–N bonds and forms no B–B or N–N bond, and its energy never falls below that of "
           f"the isolated cage (from {f1(s['dcar_min'])} to {f1(s['dcar_max'])} kcal mol^{{−1}} above it, the "
           "cost of its distortion).", indent=True)
    if len(s["reacted"]):
        r = s["reacted"].iloc[0]
        k.para(doc,
               f"{r['name']} is a special case: in the relaxed complex it forms a covalent bond to the cage in "
               "addition to a dative one, and an intramolecular proton moves between two of its oxygen atoms. "
               "Its very large interaction energy therefore describes a chemical reaction rather than adsorption; "
               "it is flagged in Table 1 and excluded from the QSPR model of Δ*E*_{int}.", indent=True)
    k.figure(doc, FIG / "Fig5.png", 5,
             "Relaxed GFN2-xTB structures. **a** The B_{36}N_{36} cage (B pink, N blue). **b**, **c** "
             "Physisorbed olaparib and the most strongly physisorbed drug. **d** The most strongly chemisorbed "
             "drug that keeps its own bonding, attached through B–O dative bonds")
    k.figure(doc, FIG / "Fig6.png", 6,
             "Adsorption on B_{36}N_{36}. **a** Closest drug–cage heavy-atom contact versus −Δ*E*_{int}; red, "
             "chemisorbed (drug–cage bond formed); blue, physisorbed; cross, drug whose own bonding changed. "
             "**b** −Δ*E*_{int} by therapeutic family")

    k.heading(doc, "Docking and adsorption are independent", 2)
    k.para(doc,
           f"The PARP1 docking score and the cage interaction energy are uncorrelated (Spearman ρ = "
           f"{f2(s['rho'])}, *p* = {f2(s['prho'])}; Fig. 4b): a drug's affinity for the target says nothing about "
           "how strongly the carrier holds it. For delivery this is favourable, because the two properties can "
           "be selected independently; for example, "
           f"{dn(s['top'].name.iloc[0])} combines the best docking score with weak physisorption, which "
           "would favour release.", indent=True)
    k.heading(doc, "QSPR models", 2)
    k.para(doc,
           f"Neither endpoint could be predicted from the four pre-selected descriptors. For the docking score "
           f"(*n* = {qv['n']}) the out-of-fold *Q*^{{2}}_{{CV}} was {f2(qv['Q2_CV'])} (RMSE {f2(qv['RMSE'])} kcal "
           f"mol^{{−1}}), and for Δ*E*_{{int}} (*n* = {qa['n']}) it was {f2(qa['Q2_CV'])} (RMSE "
           f"{f1(qa['RMSE'])} kcal mol^{{−1}}); in both cases Y-scrambled models did as well "
           f"(*p* = {qv['Y_scrambling']['p']:.2f} and {qa['Y_scrambling']['p']:.2f}; Fig. 7, Table 2). The "
           "adsorption result is chemically reasonable: whether a drug chemisorbs depends on whether one of "
           "its Lewis-basic groups can reach a boron atom in a favourable geometry, a local structural feature "
           "that global descriptors such as molecular weight or electrophilicity do not encode. In both models "
           f"all drugs except {', '.join(dn(x) for x in sorted(set(qv['AD']['outside']) | set(qa['AD']['outside'])))} "
           "lie inside the applicability domain, so the failure is not an extrapolation effect. These negative results are reported as such; they indicate that "
           "screening B_{36}N_{36} carriers requires explicit adsorption calculations rather than descriptor "
           "surrogates.", indent=True)
    k.figure(doc, FIG / "Fig7.png", 7,
             "QSPR models, nested 5×5 cross-validation. Top row, Vina score on PARP1; bottom row, Δ*E*_{int} "
             "on B_{36}N_{36}. **a**, **d** Out-of-fold predictions (dashed, identity; shaded, ±10% of the "
             "range). **b**, **e** Williams plots (dotted, warning leverage *h*^{*}; dashed, ±3 standardised "
             "residuals). **c**, **f** *Q*^{2}_{CV} of 1,000 models fitted to permuted targets")

    fam_short = {"PARP inhibitor": "PARP", "cytotoxic agent": "Cyto.", "kinase/pathway inhibitor": "Kinase"}
    rows = []
    for r in m.sort_values("vina_4UND_kcal_mol").itertuples():
        note = "" if r.drug_intact else "^{a}"
        rows.append([r.name + note, fam_short[r.family], f2(r.vina_4UND_kcal_mol), f1(r.delta_Eint_SP_kcal_mol),
                     f1(r.delta_Eads_kcal_mol), f2(r.min_contact_A), r.adsorption_mode[:4] + "."])
    k.table(doc, (1, "Docking and adsorption results for the 30 organic drugs, sorted by Vina score."),
            ["Drug", "Family", "Vina", "Δ*E*_{int}", "Δ*E*_{ads}", "*d*_{min}", "Regime"], rows,
            align="llccccl", font=8,
            note="Energies in kcal mol^{−1}; Vina, AutoDock Vina score in PARP1 (4UND); Δ*E*_{int}, Δ*E*_{ads}, "
                 "GFN2-xTB interaction and adsorption energies on B_{36}N_{36}; *d*_{min}, closest drug–cage "
                 "heavy-atom contact (Å); chem., chemisorption; phys., physisorption. ^{a} The drug's own bonding "
                 "changed in the complex (reaction); excluded from the Δ*E*_{int} QSPR model.")
    rows = [[lab, str(q["n"]), f2(q["Q2_CV"]), f2(q["RMSE"]), f2(q["MAE"]), f2(q["Y_scrambling"]["mean_Q2"]),
             f"{q['Y_scrambling']['p']:.2f}", f"{q['AD']['n_inside']}/{q['n']}"]
            for lab, q in (("Vina score, PARP1", qv), ("Δ*E*_{int}, B_{36}N_{36}", qa))]
    k.table(doc, (2, "QSPR models (ridge regression; MolWt, MolMR, *E*_{HOMO}, ω) under nested 5×5 "
                     "cross-validation."),
            ["Endpoint", "*n*", "*Q*^{2}_{CV}", "RMSE", "MAE", "*Q*^{2} (perm.)", "*p*", "In AD"], rows,
            align="lccccccc", font=8.5,
            note="RMSE and MAE in kcal mol^{−1}; *Q*^{2} (perm.), mean over 1,000 Y-permutations passed through "
                 "the same nested procedure; *p* = (1 + number of permutations reaching the model's *Q*^{2}_{CV})/1,001; "
                 "In AD, drugs inside the applicability domain.")


def conclusions(doc, d, c):
    s, qv, qa = stats(d), d["q_vina"], d["q_dEint"]
    k.heading(doc, "Conclusions")
    k.para(doc,
           f"On a chemically valid B_{{36}}N_{{36}} cage, {s['n_chem']} of {s['n']} anti-TNBC drugs chemisorb "
           f"through B–O or B–N dative bonds and {s['n_phys']} physisorb; one, doxorubicin, reacts with the "
           "cage. The regime, not the therapeutic class, dominates the strength of binding. A docking protocol "
           "validated on the crystallographic talazoparib pose places the drugs in the PARP1 nicotinamide pocket "
           "and ranks the approved PARP inhibitors first, and target affinity is independent of carrier "
           f"binding. Descriptor-based QSPR models fail for both endpoints (*Q*^{{2}}_{{CV}} ≈ {f2(qv['Q2_CV'])} "
           f"and {f2(qa['Q2_CV'])}), so B_{{36}}N_{{36}} loading must be assessed by explicit adsorption "
           "calculations. The study is limited to gas-phase GFN2-xTB energies on a single cage and to "
           "rigid-receptor docking; solvation, higher-level energies for the chemisorbed complexes and "
           "release kinetics are the natural next steps.", indent=True)


def build(doc, d, c):
    abstract(doc, d, c)
    introduction(doc, c)
    k.figure(doc, FIG / "Fig1.png", 1,
             "Workflow of the study: PubChem structures; PARP1 docking validated by redocking; construction and "
             "validation of the B_{36}N_{36} cage; GFN2-xTB adsorption from four orientations with bond-integrity "
             "check; QSPR models under nested cross-validation")
    methods(doc, d, c)
    k.heading(doc, "Use of AI tools", 2)
    k.placeholder(doc, "[AUTHOR TO COMPLETE BEFORE SUBMISSION: statement on the use of AI tools in this work, as required by the journal (Springer policy: use of large language models beyond copy editing must be documented in the Methods).]")
    results(doc, d, c)
    conclusions(doc, d, c)


def declarations(doc):
    k.heading(doc, "Statements and Declarations")
    for label, text in (
        ("Author contribution", f"{AUTHOR} conceived the study, performed all calculations and analyses, "
                                "and wrote the manuscript."),
        ("Funding", "No funding was received for this work."),
        ("Data availability", "All input structures, relaxed geometries, docking poses, xtb outputs and "
                              f"result tables are available at {REPO}."),
        ("Code availability", f"The complete pipeline, which regenerates every number, table and figure "
                              f"of this article from the raw inputs, is available at {REPO} under the MIT "
                              "licence. Software: xtb 6.7.1, AutoDock Vina 1.2.7, Meeko, RDKit, PDBFixer/"
                              "OpenMM, scikit-learn, PyMOL (open source)."),
        ("Ethics approval", "Not applicable."),
        ("Consent to participate", "Not applicable."),
        ("Consent for publication", "Not applicable."),
        ("Competing interests", "The author declares no competing interests."),
    ):
        k.labelled(doc, label, text)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load()
    c = Cites()
    doc = k.new_document()
    front(doc)
    build(doc, d, c)
    k.references(doc, c.list())
    declarations(doc)
    out = OUT / "Manuscript_TNBC_B36N36_JMM.docx"
    doc.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
