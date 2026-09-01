import re, hashlib, time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import spearmanr

base = Path(r"c:\Users\Andre\Proyectos doctorado\nano-qsar-ai-therapeutics")
calc = base / "calculations" / "tnbc"
proc = base / "data" / "processed"

# 1. Update dataset_tnbc_bn_pristine.csv with authentic Vina affinities
df = pd.read_csv(proc / "dataset_tnbc_bn_pristine.csv")

for idx, row in df.iterrows():
    name = row["name"]
    dir_name = name.replace(" ", "_").replace("-", "_")
    mol_dir = calc / dir_name
    
    # Check possible log names
    log_candidates = [
        mol_dir / f"{dir_name}_4UND_vina.log",
        mol_dir / f"{dir_name}_vina.log",
        mol_dir / f"{name}_vina.log"
    ]
    vina_val = None
    for cand in log_candidates:
        if cand.exists():
            for l in cand.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"\s+1\s+(-?\d+\.\d+)", l)
                if m:
                    vina_val = float(m.group(1))
                    break
            if vina_val is not None: break
    
    df.at[idx, "vina_4UND_kcal_mol"] = vina_val

df.to_csv(proc / "dataset_tnbc_bn_pristine.csv", index=False)
print(f"TNBC Dataset updated: {len(df)} compounds. Vina values present for {df['vina_4UND_kcal_mol'].notna().sum()} compounds.")

# 2. Relaxed subset
df_rel = pd.read_csv(proc / "relaxed_adsorption_subset.csv")
print(f"\nRelaxed subset: N={len(df_rel)} compounds")
rho_s, p_s = spearmanr(df_rel["delta_Eint_SP_kcal_mol"], df_rel["delta_Eint_relaxed_kcal_mol"])
mae_s = mean_absolute_error(df_rel["delta_Eint_SP_kcal_mol"], df_rel["delta_Eint_relaxed_kcal_mol"])
print(f"Spearman rho = {rho_s:.4f} (p={p_s:.4f}), MAE = {mae_s:.2f} kcal/mol")

# 3. Redocking validation
df_redock = pd.read_csv(proc / "redocking_validation.csv")
print("\nRedocking Validation:")
print(df_redock.to_string())

# 4. Nested CV on N=30 organic compounds
desc_cols = ["E_HOMO_eV", "E_LUMO_eV", "Omega_eV", "MolMR"]
target_col = "vina_4UND_kcal_mol"
df_qsar = df.dropna(subset=desc_cols + [target_col]).copy()
n = len(df_qsar)
X = df_qsar[desc_cols].values
y = df_qsar[target_col].values

outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
alphas = np.logspace(-3, 3, 50)
y_pred_nested = np.zeros(n)

for tr, te in outer_cv.split(X):
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X[tr])
    X_te_s = scaler.transform(X[te])
    rcv = RidgeCV(alphas=alphas, cv=5)
    rcv.fit(X_tr_s, y[tr])
    y_pred_nested[te] = rcv.predict(X_te_s)

q2_nested = r2_score(y, y_pred_nested)
rmse_nested = mean_squared_error(y, y_pred_nested)**0.5
mae_nested = mean_absolute_error(y, y_pred_nested)
h_star = 3 * (4 + 1) / n

# 1,000 Y-scramblings
best_alpha = 1.0
scaler_p = StandardScaler()
X_s_full = scaler_p.fit_transform(X)

np.random.seed(99)
scramble_q2 = []
for _ in range(1000):
    y_perm = np.random.permutation(y)
    yp_p = np.zeros(n)
    for tr, te in outer_cv.split(X_s_full):
        r_mod = Ridge(alpha=best_alpha)
        r_mod.fit(X_s_full[tr], y_perm[tr])
        yp_p[te] = r_mod.predict(X_s_full[te])
    scramble_q2.append(r2_score(y_perm, yp_p))

p_val = (np.array(scramble_q2) >= q2_nested).mean()

print(f"\nTNBC STATISTICAL AUDIT REPORT (TRUE NESTED CV)")
print(f"  n compounds:                 {n}")
print(f"  p descriptors:               4 (HOMO, LUMO, Omega, MolMR)")
print(f"  n/p ratio:                   {n/4:.2f}")
print(f"  Nested Q2_CV (exploratory):  {q2_nested:.4f}")
print(f"  RMSE:                        {rmse_nested:.3f} kcal/mol")
print(f"  MAE:                         {mae_nested:.3f} kcal/mol")
print(f"  Williams threshold h*:       {h_star:.4f}")
print(f"  1,000 Y-scrambling mean Q2:  {np.mean(scramble_q2):.4f}")
print(f"  Empirical p-value:           {p_val:.4f}")

# 5. Calculation provenance
prov_rows = []
for name in df["name"]:
    dir_name = name.replace(" ", "_").replace("-", "_")
    mol_dir = calc / dir_name
    out_f = mol_dir / f"{dir_name}_drug_sp.out"
    
    log_candidates = [
        mol_dir / f"{dir_name}_4UND_vina.log",
        mol_dir / f"{dir_name}_vina.log",
        mol_dir / f"{name}_vina.log"
    ]
    log_f_str = "N/A"
    for cand in log_candidates:
        if cand.exists():
            log_f_str = str(cand.relative_to(base))
            break
            
    c_out = mol_dir / f"{dir_name}_complex_clean_sp.out"
    prov_rows.append({
        "compound": name,
        "drug_xtb_log": str(out_f.relative_to(base)) if out_f.exists() else "N/A",
        "vina_4und_log": log_f_str,
        "complex_sp_log": str(c_out.relative_to(base)) if c_out.exists() else "N/A"
    })

pd.DataFrame(prov_rows).to_csv(proc / "calculation_provenance.csv", index=False)
print("\nProvenance CSV written.")

# 6. Manifest generation
def sha256_file(fp):
    h = hashlib.sha256()
    with open(fp, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

manifest_lines = [
    "# TNBC B36N36 — SHA-256 Integrity Manifest (AUTHENTIC EXECUTABLE RAW LOGS)",
    f"# Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}",
    "# AutoDock Vina: v1.2.7 | xTB: v6.7.1-pre | ORCA: v6.1.1",
    f"# Total processed compounds: {len(df)} (30 organic + 3 platinum controls, PARP1 4UND docking + xTB quantum calculated)",
    "# Primary Target: Human PARP1 Catalytic Domain (PDB: 4UND, 2.30 A X-ray)",
    "# Carrier: Fully tight-optimized 72-atom spherical B36N36 cage (E_cage = -150.205739 Eh)",
    "# Heavy-Atom Redocking RMSD: 4UND (2YQ, 25 heavy atoms) = 4.474 A",
    f"# Multi-Orientation Relaxed Subset (N=8): Spearman rho = {rho_s:.4f} (p={p_s:.4f}), MAE = {mae_s:.2f} kcal/mol",
    f"# Nested Ridge Q2_CV (exploratory): {q2_nested:.4f}, RMSE: {rmse_nested:.3f} kcal/mol, MAE: {mae_nested:.3f} kcal/mol, h*: {h_star:.4f}",
    "#",
    "# SHA256                                                               bytes  role  path",
    "#" + "-"*95,
]

seen_hashes = set()
for p in sorted(base.rglob("*")):
    if p.is_file() and not p.name.startswith(".") and "MANIFEST" not in p.name and ".git" not in str(p):
        h = sha256_file(p)
        if (h, p.name) not in seen_hashes:
            seen_hashes.add((h, p.name))
            manifest_lines.append(f"{h}  {p.stat().st_size:>12} bytes  [tnbc]  {p.relative_to(base)}")

manifest_path = base / "MANIFEST_SHA256.txt"
manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
print(f"\n[SAVED] MANIFEST_SHA256.txt: {manifest_path} ({len(seen_hashes)} files)")
