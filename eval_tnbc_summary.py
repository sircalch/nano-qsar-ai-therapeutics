import re, hashlib, time
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import spearmanr

base = Path(r"c:\Users\Andre\Proyectos doctorado\nano-qsar-ai-therapeutics")
calc = base / "calculations" / "tnbc"
proc = base / "data" / "processed"

# 1. Update redocking_validation.csv with FAILED status and verified RCSB PDB metadata (4UND = 2.20 A)
redock_rows = [
    {
        "pdb_id": "4UND",
        "target_desc": "Human PARP1 Catalytic Domain (X-ray)",
        "resolution_A": 2.20,
        "probe_ligand": "Talazoparib (2YQ)",
        "affinity_kcal_mol": -9.28,
        "n_heavy_atoms": 25,
        "rmsd_heavy_atom_A": 4.474,
        "docking_status": "FAILED (RMSD > 2.0 A criterion)",
        "scientific_interpretation": "Crystallographic redocking did not reproduce experimental pose (RMSD=4.474 A > 2.0 A); docking scores treated as exploratory.",
        "mapping_method": "Hungarian symmetry-aware matching",
        "pose_file": "calculations/tnbc/redock_2YQ_4UND_out.pdbqt"
    }
]
df_redock = pd.DataFrame(redock_rows)
df_redock.to_csv(proc / "redocking_validation.csv", index=False)
print("Saved redocking_validation.csv (4UND = 2.20 A, FAILED status):")
print(df_redock.to_string())

# 2. Relaxed Adsorption Subset and Rigorous Rank Analysis
df_rel = pd.read_csv(proc / "relaxed_adsorption_subset.csv")
rho_s, p_s = spearmanr(df_rel["delta_Eint_SP_kcal_mol"], df_rel["delta_Eint_relaxed_kcal_mol"])
mae_s = mean_absolute_error(df_rel["delta_Eint_SP_kcal_mol"], df_rel["delta_Eint_relaxed_kcal_mol"])
print(f"\nTNBC Relaxed Adsorption Analysis (N={len(df_rel)}):")
print(f"  Spearman rho = {rho_s:.4f} (p={p_s:.4f}), MAE = {mae_s:.2f} kcal/mol")
print("  Scientific interpretation: SP screening on curved spherical B36N36 does NOT predict relaxed thermodynamic ranking (rho=0.0476, p=0.9108); Delta_Eint_SP is strictly an unrelaxed screening descriptor, and true carrier affinity requires full geometry optimization.")

# 3. Strict Nested CV on N=30 organic compounds & 1,000 Y-scramblings
df_main = pd.read_csv(proc / "dataset_tnbc_bn_pristine.csv")
desc_cols = ["E_HOMO_eV", "E_LUMO_eV", "Omega_eV", "MolMR"]
target_col = "vina_4UND_kcal_mol"
df_qsar = df_main.dropna(subset=desc_cols + [target_col]).copy()
n_qsar = len(df_qsar)
X = df_qsar[desc_cols].values
y = df_qsar[target_col].values

outer_cv = KFold(n_splits=5, shuffle=True, random_state=42)
alphas = np.logspace(-3, 3, 50)
y_pred_nested = np.zeros(n_qsar)

for tr, te in outer_cv.split(X):
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X[tr])
    X_te_s = scaler.transform(X[te])
    rcv = RidgeCV(alphas=alphas)
    rcv.fit(X_tr_s, y[tr])
    y_pred_nested[te] = rcv.predict(X_te_s)

q2_nested = r2_score(y, y_pred_nested)
rmse_nested = mean_squared_error(y, y_pred_nested)**0.5
mae_nested = mean_absolute_error(y, y_pred_nested)
h_star = 3 * (4 + 1) / n_qsar

np.random.seed(99)
scramble_q2 = []
for _ in range(1000):
    y_perm = np.random.permutation(y)
    yp_p = np.zeros(n_qsar)
    for tr, te in outer_cv.split(X):
        scaler = StandardScaler()
        X_tr_s = scaler.fit_transform(X[tr])
        X_te_s = scaler.transform(X[te])
        rcv = RidgeCV(alphas=alphas)
        rcv.fit(X_tr_s, y_perm[tr])
        yp_p[te] = rcv.predict(X_te_s)
    scramble_q2.append(r2_score(y_perm, yp_p))

p_val = (np.array(scramble_q2) >= q2_nested).mean()

print(f"\nTNBC STATISTICAL AUDIT REPORT (STRICT NESTED CV)")
print(f"  n compounds:                 {n_qsar}")
print(f"  p descriptors:               4 (HOMO, LUMO, Omega, MolMR)")
print(f"  n/p ratio:                   {n_qsar/4:.2f}")
print(f"  Nested Q2_CV (exploratory):  {q2_nested:.4f}")
print(f"  RMSE:                        {rmse_nested:.3f} kcal/mol")
print(f"  MAE:                         {mae_nested:.3f} kcal/mol")
print(f"  Williams threshold h*:       {h_star:.4f}")
print(f"  1,000 Y-scrambling mean Q2:  {np.mean(scramble_q2):.4f}")
print(f"  Empirical p-value:           {p_val:.4f}")

# 4. Manifest generation
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
    f"# Total processed compounds: {len(df_main)} (30 organic + 3 platinum controls, PARP1 4UND docking + xTB quantum calculated)",
    "# Primary Target: Human PARP1 Catalytic Domain (PDB: 4UND, 2.20 A X-ray)",
    "# Carrier: Fully tight-optimized 72-atom spherical B36N36 cage (E_cage = -150.205739 Eh)",
    "# Heavy-Atom Redocking Validation: 4UND RMSD = 4.474 A (FAILED) -> Docking treated as exploratory",
    f"# Multi-Orientation Relaxed Subset (N=8): Spearman rho = {rho_s:.4f} (p={p_s:.4f}), MAE = {mae_s:.2f} kcal/mol",
    "# Note on Adsorption: SP screening on curved cage does not predict relaxed ranking; carrier affinity requires full geometry optimization",
    f"# Strict Nested Ridge Q2_CV: {q2_nested:.4f}, RMSE: {rmse_nested:.3f} kcal/mol, MAE: {mae_nested:.3f} kcal/mol, h*: {h_star:.4f}",
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
print(f"\n[SAVED] TNBC MANIFEST_SHA256.txt: {len(seen_hashes)} files hashed.")
