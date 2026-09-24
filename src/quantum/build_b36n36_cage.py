"""
build_b36n36_cage.py
====================
Builds a chemically valid B36N36 fullerene-like nanocage and relaxes it with
GFN2-xTB.

Topology: octahedral Goldberg-type cage GP(1,1) = leapfrog of the truncated
octahedron (B12N12). 72 vertices, 108 edges, 6 four-membered + 32
six-membered rings. Every face has even size, so the cage graph is bipartite
and B/N can alternate strictly: all 108 bonds are B-N, none B-B or N-N
(the "isolated-square" rule for stable (BN)n cages).

Replaces the earlier Thomson-sphere construction, whose random B/N labelling
left 19 B-B and 21 N-N bonds in the "optimised" cage.

Output: calculations/tnbc/B36N36_optimized.xyz (+ B36N36_opt.out, energy in
calculations/tnbc/B36N36_energy.json).
"""
import itertools
import json
import os
import shutil
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull

BASE = Path(__file__).resolve().parents[2]
OUT_DIR = BASE / "calculations" / "tnbc"
BN_BOND = 1.45  # A, initial guess before GFN2-xTB relaxation


def truncated_octahedron():
    pts = set()
    for perm in set(itertools.permutations((0, 1, 2))):
        for sx in (-1, 1):
            for sy in (-1, 1):
                v = [0, 0, 0]
                v[perm[1]] = sx * 1
                v[perm[2]] = sy * 2
                pts.add(tuple(v))
    return np.array(sorted(pts), float)


def polyhedron_faces(V):
    """Faces of a convex polyhedron as vertex cycles (coplanar hull triangles merged)."""
    hull = ConvexHull(V)
    groups = {}
    for simplex, eq in zip(hull.simplices, hull.equations):
        key = tuple(np.round(eq, 6))
        groups.setdefault(key, set()).update(simplex.tolist())
    faces = []
    for key, idx in groups.items():
        idx = list(idx)
        n = np.array(key[:3])
        c = V[idx].mean(0)
        u = V[idx[0]] - c
        u /= np.linalg.norm(u)
        w = np.cross(n, u)
        ang = [np.arctan2((V[i] - c) @ w, (V[i] - c) @ u) for i in idx]
        faces.append([i for _, i in sorted(zip(ang, idx))])
    return faces


def leapfrog(V, faces):
    """Leapfrog: one new vertex per (face, face-edge); returns coords + edges."""
    node = {}
    X = []
    for fi, f in enumerate(faces):
        c = V[f].mean(0)
        for k in range(len(f)):
            a, b = f[k], f[(k + 1) % len(f)]
            node[(fi, frozenset((a, b)))] = len(X)
            X.append((c + V[a] + V[b]) / 3.0)
    edges = set()
    edge_faces = {}
    for fi, f in enumerate(faces):
        m = len(f)
        for k in range(m):
            e1 = frozenset((f[k], f[(k + 1) % m]))
            e2 = frozenset((f[(k + 1) % m], f[(k + 2) % m]))
            edges.add(frozenset((node[(fi, e1)], node[(fi, e2)])))  # around the face
            edge_faces.setdefault(e1, []).append(fi)
    for e, fs in edge_faces.items():
        assert len(fs) == 2
        edges.add(frozenset((node[(fs[0], e)], node[(fs[1], e)])))  # across the old edge
    return np.array(X), [tuple(e) for e in edges]


def two_colour(n, edges):
    adj = {i: [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    col = {0: 0}
    q = deque([0])
    while q:
        i = q.popleft()
        for j in adj[i]:
            if j not in col:
                col[j] = 1 - col[i]
                q.append(j)
            elif col[j] == col[i]:
                raise RuntimeError("cage graph is not bipartite")
    return [col[i] for i in range(n)]


def build():
    V0 = truncated_octahedron()
    faces0 = polyhedron_faces(V0)
    X, edges = leapfrog(V0, faces0)
    assert len(X) == 72 and len(edges) == 108, (len(X), len(edges))
    assert all(sum(1 for e in edges if i in e) == 3 for i in range(72))
    X -= X.mean(0)
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    mean_edge = np.mean([np.linalg.norm(X[a] - X[b]) for a, b in edges])
    X *= BN_BOND / mean_edge
    col = two_colour(72, edges)
    el = ["B" if c == 0 else "N" for c in col]
    # leapfrog faces = the parent faces (same size) + one 2*deg-gon per parent vertex
    ring_sizes = sorted([len(f) for f in faces0] + [6] * len(V0))
    return el, X, edges, ring_sizes


def bond_census(el, X, cut=1.75):
    census = {}
    for i, j in itertools.combinations(range(len(el)), 2):
        if np.linalg.norm(X[i] - X[j]) < cut:
            k = "".join(sorted(el[i] + el[j]))
            census[k] = census.get(k, 0) + 1
    return census


def write_xyz(path, el, X, comment):
    with open(path, "w") as fh:
        fh.write(f"{len(el)}\n{comment}\n")
        for e, (x, y, z) in zip(el, X):
            fh.write(f"{e:2s} {x:15.8f} {y:15.8f} {z:15.8f}\n")


def read_xyz(path):
    L = Path(path).read_text().splitlines()
    n = int(L[0])
    return ([l.split()[0] for l in L[2:2 + n]],
            np.array([[float(v) for v in l.split()[1:4]] for l in L[2:2 + n]]))


def main():
    el, X, edges, rings = build()
    print(f"topology: {len(X)} atoms, {len(edges)} bonds, rings {dict((r, rings.count(r)) for r in set(rings))}")
    print("initial bond census:", bond_census(el, X))

    xtb = os.environ.get("XTB_EXE") or shutil.which("xtb") or "C:/Users/Andre/mm/xtb/Library/bin/xtb.exe"
    env = dict(os.environ)
    share = Path(xtb).parent.parent / "share" / "xtb"
    if share.is_dir():
        env["XTBPATH"] = str(share)
    env.setdefault("OMP_NUM_THREADS", "4")

    wd = OUT_DIR / "b36n36_build"
    wd.mkdir(parents=True, exist_ok=True)
    write_xyz(wd / "B36N36_leapfrog_initial.xyz", el, X, "B36N36 GP(1,1) leapfrog, unrelaxed")
    p = subprocess.run([xtb, "B36N36_leapfrog_initial.xyz", "--opt", "tight", "--gfn", "2",
                        "--chrg", "0", "--uhf", "0", "--iterations", "500"],
                       cwd=wd, env=env, capture_output=True, text=True, errors="replace")
    out = p.stdout
    (OUT_DIR / "B36N36_opt.out").write_text(out, encoding="utf-8")
    if "GEOMETRY OPTIMIZATION CONVERGED" not in out:
        sys.exit("xtb optimisation did not converge")
    el2, X2 = read_xyz(wd / "xtbopt.xyz")
    census = bond_census(el2, X2)
    print("relaxed bond census:", census)
    if census.get("BB") or census.get("NN"):
        sys.exit("homonuclear bonds after relaxation - cage rejected")
    energy = gap = homo = lumo = None
    for line in out.splitlines():
        if "TOTAL ENERGY" in line:
            energy = float(line.split()[3])
        if "HOMO-LUMO GAP" in line:
            gap = float(line.split()[3])
        if "(HOMO)" in line:
            homo = float(line.split()[-2])
        if "(LUMO)" in line:
            lumo = float(line.split()[-2])
    write_xyz(OUT_DIR / "B36N36_optimized.xyz", el2, X2,
              f"B36N36 GP(1,1) cage, GFN2-xTB opt tight, E = {energy:.8f} Eh")
    (OUT_DIR / "B36N36_energy.json").write_text(json.dumps(
        {"E_Eh": energy, "HOMO_LUMO_gap_eV": gap, "HOMO_eV": homo, "LUMO_eV": lumo, "bond_census": census,
         "topology": "octahedral GP(1,1) leapfrog of truncated octahedron",
         "rings": {"4": rings.count(4), "6": rings.count(6)}}, indent=2))
    print(f"E = {energy} Eh, gap = {gap} eV")


if __name__ == "__main__":
    main()
