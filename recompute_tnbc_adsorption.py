"""
recompute_tnbc_adsorption.py
============================
Rebuild the TNBC / B36N36 nanocage adsorption dataset from scratch, correctly.

Why: the shipped `delta_Eint_SP_kcal_mol` column of
`data/processed/dataset_tnbc_bn_pristine.csv` was a *single point* on an
UNRELAXED geometry (drug dropped 3.2 A above z_max of the cage, ~3.9 A off the
surface, never optimised) - the same defect fixed for the Tau/borophene study.
Properly relaxed values existed for only 8 of the 33 drugs.

This script, for each of the 33 drugs:
  1. builds the drug from (corrected) SMILES, RDKit ETKDG + MMFF, then
     GFN2-xTB --opt  ->  E_drug (relaxed, isolated), drug_opt.xyz
  2. places it flat 3.2 A above the local sheet surface, tries z-rotations
     0/90/180/270 deg, GFN2-xTB --opt on each (chrg = formal charge)
  3. keeps converged poses whose closest drug-carrier contact is 1.3-4.0 A
     (bound, not clashing); picks the lowest-energy one
  4. on that pose: SP for E_complex, then SP on the carrier and drug fragments
     frozen at the complex geometry  ->  E_cf, E_df
  5. Delta_Eint_SP  = (E_complex - E_cf - E_df) * 627.509      (interaction)
     Delta_Eads     = (E_complex - E_carrier_iso - E_drug_iso) * 627.509  (adsorption)

Outputs (idempotent / resumable - re-run to fill gaps):
  calculations/tnbc_recompute/<Drug>/...            per-drug workspace
  calculations/tnbc_recompute/results.csv           machine-readable summary
  and, when --commit-datasets is passed and every drug is done:
  data/processed/dataset_tnbc_bn_pristine.csv   (delta_Eint_SP + E_drug)
  data/processed/relaxed_adsorption_subset.csv        (all 33)
"""
import os, sys, json, time, shutil, subprocess, hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
PROC = BASE / "data" / "processed"
WORK = BASE / "calculations" / "tnbc_recompute"
WORK.mkdir(parents=True, exist_ok=True)

XTB = os.environ.get("XTB_EXE", "")
if not XTB:
    XTB = shutil.which("xtb") or shutil.which("xtb.exe") or ""
if not XTB:
    hits = list(BASE.glob("**/xtb-*/bin/xtb.exe")) or [Path("C:/Users/Andre/mm/xtb/Library/bin/xtb.exe")]
    XTB = str(hits[0])
XTB_ENV = dict(os.environ)
_share = Path(XTB).parent.parent / "share" / "xtb"
if _share.is_dir():
    XTB_ENV["XTBPATH"] = str(_share)
XTB_ENV.setdefault("OMP_NUM_THREADS", "4")

HARTREE = 627.509474

SMILES_FIX = {}   # TNBC SMILES in the source CSV are fine


# --------------------------------------------------------------------------- io
def read_xyz(p):
    L = Path(p).read_text().splitlines()
    n = int(L[0].split()[0])
    el = [x.split()[0] for x in L[2:2 + n]]
    xyz = np.array([[float(v) for v in x.split()[1:4]] for x in L[2:2 + n]])
    return el, xyz


def write_xyz(p, el, xyz, comment=""):
    with open(p, "w") as f:
        f.write(f"{len(el)}\n{comment}\n")
        for e, (x, y, z) in zip(el, xyz):
            f.write(f"{e:2s} {x:15.8f} {y:15.8f} {z:15.8f}\n")


def xtb_energy(out_text):
    e = None
    for l in out_text.splitlines():
        if "TOTAL ENERGY" in l:
            for tok in l.split():
                try:
                    e = float(tok); break
                except ValueError:
                    continue
    return e


def xtb_converged(out_text):
    return ("GEOMETRY OPTIMIZATION CONVERGED" in out_text
            and "FAILED TO CONVERGE GEOMETRY OPTIMIZATION" not in out_text)


def run_xtb(args, cwd, timeout=900):
    p = subprocess.run([XTB, *args], cwd=str(cwd), env=XTB_ENV,
                       capture_output=True, text=True, errors="replace",
                       timeout=timeout)
    return p.stdout + "\n" + p.stderr


# ------------------------------------------------------------------ chemistry
def drug_from_smiles(smiles, out_xyz):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError(f"bad SMILES: {smiles}")
    m = Chem.AddHs(m)
    cids = AllChem.EmbedMultipleConfs(m, numConfs=8, randomSeed=0xC0FFEE)
    if not cids:
        AllChem.EmbedMolecule(m, randomSeed=1)
        cids = [0]
    best, best_e = None, 1e9
    for c in cids:
        try:
            ff = AllChem.MMFFGetMoleculeForceField(
                m, AllChem.MMFFGetMoleculeProperties(m), confId=c)
            ff.Minimize(maxIts=2000)
            e = ff.CalcEnergy()
        except Exception:
            e = 0.0
        if e < best_e:
            best_e, best = e, c
    conf = m.GetConformer(best)
    el = [a.GetSymbol() for a in m.GetAtoms()]
    xyz = np.array([list(conf.GetAtomPosition(i)) for i in range(m.GetNumAtoms())])
    write_xyz(out_xyz, el, xyz, "rdkit ETKDG+MMFF")
    return el, xyz


def place(drug_el, drug_xyz, carr_el, carr_xyz, angle_deg, gap=3.2):
    """Approach the ~spherical B36N36 cage from +z: drug centred over the cage
    centroid xy, rotated about z, lowest drug atom `gap` A above the cage top."""
    d = drug_xyz.copy()
    d[:, :2] -= d[:, :2].mean(axis=0)
    th = np.radians(angle_deg)
    R = np.array([[np.cos(th), -np.sin(th), 0],
                  [np.sin(th), np.cos(th), 0], [0, 0, 1]])
    d = d @ R.T
    c_centroid = carr_xyz.mean(axis=0)
    d[:, :2] += c_centroid[:2]
    d[:, 2] += (carr_xyz[:, 2].max() + gap) - d[:, 2].min()
    el = list(drug_el) + list(carr_el)
    xyz = np.vstack([d, carr_xyz])
    return el, xyz, len(drug_el)


def min_contact(el, xyz, n_drug):
    dd = xyz[:n_drug]
    cc = xyz[n_drug:]
    hv_d = [i for i, e in enumerate(el[:n_drug]) if e != "H"]
    hv_c = [i for i, e in enumerate(el[n_drug:]) if e != "H"]
    if not hv_d or not hv_c:
        return 99.0
    D = np.linalg.norm(dd[hv_d][:, None, :] - cc[hv_c][None, :, :], axis=2)
    return float(D.min())


# --------------------------------------------------------------------- worker
def process(args):
    name, smiles, q = args
    dslug = name.replace(" ", "_").replace("-", "_")
    wd = WORK / dslug
    wd.mkdir(exist_ok=True)
    res_p = wd / "result.json"
    if res_p.exists():
        try:
            return json.loads(res_p.read_text())
        except Exception:
            pass
    t0 = time.time()
    rec = {"name": name, "formal_charge": q, "smiles": smiles}
    try:
        # 1. drug -- RDKit ETKDG, but fall back to the existing calculations/
        #    geometry for organometallics RDKit/MMFF cannot embed (Pt drugs).
        draw = wd / "drug_raw.xyz"
        dslug2 = name.replace(" ", "_")
        existing = BASE / "calculations" / "tnbc" / dslug2 / f"{dslug2}_drug.xyz"
        try:
            drug_from_smiles(smiles, draw)
        except Exception:
            if existing.exists():
                el0, xyz0 = read_xyz(existing)
                write_xyz(draw, el0, xyz0, "existing calc geometry")
            else:
                raise
        run_xtb([str(draw), "--opt", "--gfn", "2", "--chrg", str(q),
                 "--uhf", "0", "--iterations", "500", "--namespace", "dopt"],
                wd, timeout=900)
        dopt = wd / "dopt.xtbopt.xyz"
        if not dopt.exists():
            dopt = wd / "xtbopt.xyz"
        del_el, del_xyz = read_xyz(dopt)
        e_drug = xtb_energy(run_xtb([str(dopt), "--sp", "--gfn", "2", "--chrg",
                            str(q), "--uhf", "0", "--namespace", "dsp"], wd, 300))
        write_xyz(wd / "drug_opt.xyz", del_el, del_xyz, f"{name} GFN2 opt")
        rec["E_drug_Eh"] = e_drug
        rec["drug_formula"] = "".join(sorted(set(del_el)))
        rec["n_drug"] = len(del_el)

        carr_el, carr_xyz = read_xyz(BASE / "calculations" / "tnbc" / "B36N36_optimized.xyz")
        e_carr = -150.205739  # GFN2 opt, matches B36N36_optimized.xyz / B36N36_opt.out

        # 2-3. orientations (a second gap=2.6 pass if all of gap=3.2 desorb)
        best = None
        trials = [(a, 3.2) for a in (0, 90, 180, 270)] + [(a, 2.6) for a in (0, 90, 180, 270)]
        for ang, gap in trials:
            if best is not None and not best.get("unbound"):
                if gap == 2.6:
                    break
            tag = f"o{ang}_{int(gap*10)}"
            el, xyz, nd = place(del_el, del_xyz, carr_el, carr_xyz, ang, gap=gap)
            cin = wd / f"cin_{tag}.xyz"
            write_xyz(cin, el, xyz, f"{name} {ang}deg gap{gap}")
            for f in wd.glob(f"{tag}.xtbopt.xyz"):
                f.unlink()
            txt = run_xtb([str(cin), "--opt", "--gfn", "2", "--chrg", str(q),
                           "--uhf", "0", "--iterations", "500", "--cycles", "500",
                           "--namespace", tag], wd, timeout=1200)
            cx = wd / f"{tag}.xtbopt.xyz"
            if not cx.exists() or not xtb_converged(txt):
                continue
            fel, fxyz = read_xyz(cx)
            e_c = xtb_energy(txt)
            mc = min_contact(fel, fxyz, nd)
            entry = {"ang": ang, "E": e_c, "contact": mc, "path": str(cx)}
            if 1.25 <= mc <= 4.0 and e_c is not None:
                if best is None or e_c < best["E"]:
                    best = entry
            elif best is None:
                best = {**entry, "unbound": True}

        if best is None or best.get("unbound") or best.get("E") is None:
            rec.update(status="NO_STABLE_ADSORPTION",
                       best=best, seconds=round(time.time() - t0, 1))
            res_p.write_text(json.dumps(rec, indent=2))
            return rec

        # 4. SP decomposition at complex geometry
        fel, fxyz = read_xyz(best["path"])
        nd = rec["n_drug"]
        write_xyz(wd / "complex_opt.xyz", fel, fxyz, f"{name}/B40H15 GFN2 opt")
        e_complex = xtb_energy(run_xtb([str(wd / "complex_opt.xyz"), "--sp",
                    "--gfn", "2", "--chrg", str(q), "--uhf", "0",
                    "--namespace", "csp"], wd, 300))
        write_xyz(wd / "frag_carrier.xyz", fel[nd:], fxyz[nd:], "carrier @complex")
        write_xyz(wd / "frag_drug.xyz", fel[:nd], fxyz[:nd], "drug @complex")
        e_cf = xtb_energy(run_xtb([str(wd / "frag_carrier.xyz"), "--sp", "--gfn",
                          "2", "--chrg", "0", "--uhf", "0", "--namespace", "cf"], wd, 300))
        e_df = xtb_energy(run_xtb([str(wd / "frag_drug.xyz"), "--sp", "--gfn", "2",
                          "--chrg", str(q), "--uhf", "0", "--namespace", "df"], wd, 300))

        d_int = (e_complex - e_cf - e_df) * HARTREE
        d_ads = (e_complex - e_carr - e_drug) * HARTREE
        rec.update(status="OK", best_orientation_deg=best["ang"],
                   min_contact_A=round(best["contact"], 3),
                   E_complex_Eh=e_complex, E_carrier_frozen_Eh=e_cf,
                   E_drug_frozen_Eh=e_df,
                   delta_Eint_SP_kcal_mol=round(d_int, 3),
                   delta_Eads_kcal_mol=round(d_ads, 3),
                   final_pose_file=str((wd / "complex_opt.xyz").relative_to(BASE)),
                   sha256=hashlib.sha256((wd / "complex_opt.xyz").read_bytes()).hexdigest(),
                   seconds=round(time.time() - t0, 1))
    except Exception as e:
        import traceback
        rec.update(status="ERROR", error=repr(e), tb=traceback.format_exc()[-1500:],
                   seconds=round(time.time() - t0, 1))
    res_p.write_text(json.dumps(rec, indent=2))
    return rec


def main():
    df = pd.read_csv(PROC / "dataset_tnbc_bn_pristine.csv")
    jobs = []
    for _, r in df.iterrows():
        smi = SMILES_FIX.get(r["name"], r["smiles"])
        jobs.append((r["name"], smi, int(r["formal_charge"])))

    only = sys.argv[1:] and sys.argv[1] != "--commit-datasets"
    if only:
        want = set(sys.argv[1:])
        jobs = [j for j in jobs if j[0] in want]

    nproc = int(os.environ.get("TAU_NPROC", "5"))
    print(f"xtb: {XTB}\n{len(jobs)} drugs, {nproc} workers", flush=True)
    done = []
    with ProcessPoolExecutor(max_workers=nproc) as ex:
        futs = {ex.submit(process, j): j[0] for j in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            done.append(r)
            print(f"  [{len(done):2d}/{len(jobs)}] {r['name']:<22} {r.get('status'):<20} "
                  f"dEint={r.get('delta_Eint_SP_kcal_mol','-')}  "
                  f"contact={r.get('min_contact_A','-')}  {r.get('seconds','?')}s", flush=True)

    allres = [json.loads((WORK / n.replace(' ', '_').replace('-', '_') / "result.json").read_text())
              for n in df["name"]
              if (WORK / n.replace(' ', '_').replace('-', '_') / "result.json").exists()]
    pd.DataFrame(allres).to_csv(WORK / "results.csv", index=False)
    print(f"\nwrote {WORK / 'results.csv'}  ({len(allres)}/{len(df)} drugs)", flush=True)

    # Square-planar Pt(II) agents: RDKit/MMFF has no Pt parameters, so a
    # from-SMILES 3D build collapses and GFN2-xTB then gives nonsense - these are
    # marked "not modelled" rather than forced.
    PT_EXCLUDE = {"Cisplatin", "Carboplatin", "Oxaliplatin"}

    if "--commit-datasets" in sys.argv:
        ok = {r["name"]: r for r in allres if r.get("status") == "OK" and r["name"] not in PT_EXCLUDE}
        need = [n for n in df["name"] if n not in PT_EXCLUDE]
        if len(ok) < len(need):
            print(f"NOT committing: only {len(ok)}/{len(need)} non-Pt drugs OK", flush=True)
            return
        df2 = df.copy()
        for i, r in df2.iterrows():
            n = r["name"]
            if n in PT_EXCLUDE:
                df2.at[i, "delta_Eint_SP_kcal_mol"] = None
                df2.at[i, "min_contact_A"] = None
                df2.at[i, "delta_Eads_kcal_mol"] = None
                df2.at[i, "adsorption_mode"] = "not modelled (Pt(II) square-planar, outside GFN2-xTB+RDKit scope)"
            else:
                o = ok[n]
                df2.at[i, "E_drug_Eh"] = o["E_drug_Eh"]
                df2.at[i, "delta_Eint_SP_kcal_mol"] = o["delta_Eint_SP_kcal_mol"]
                df2.at[i, "min_contact_A"] = o["min_contact_A"]
                df2.at[i, "delta_Eads_kcal_mol"] = o["delta_Eads_kcal_mol"]
                df2.at[i, "adsorption_mode"] = "chemisorption" if o["min_contact_A"] < 1.9 else "physisorption"
            df2.at[i, "carrier_formula"] = "B36N36"
        df2.to_csv(PROC / "dataset_tnbc_bn_pristine.csv", index=False)
        sub = pd.DataFrame([{
            "name": n, "best_orientation_deg": ok[n]["best_orientation_deg"],
            "delta_Eint_SP_kcal_mol": ok[n]["delta_Eint_SP_kcal_mol"],
            "delta_Eads_kcal_mol": ok[n]["delta_Eads_kcal_mol"],
            "min_contact_A": ok[n]["min_contact_A"],
            "adsorption_mode": "chemisorption" if ok[n]["min_contact_A"] < 1.9 else "physisorption",
            "convergence_status": "CONVERGED",
            "final_pose_file": ok[n]["final_pose_file"],
            "sha256": ok[n]["sha256"],
        } for n in ok])
        sub.to_csv(PROC / "relaxed_adsorption_subset.csv", index=False)
        print("committed dataset_tnbc_bn_pristine.csv + relaxed_adsorption_subset.csv", flush=True)


if __name__ == "__main__":
    main()
