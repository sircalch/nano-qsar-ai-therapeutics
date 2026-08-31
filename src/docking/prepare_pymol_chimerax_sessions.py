"""
prepare_pymol_chimerax_sessions.py
Builds ready-to-use 3D complex files and 1-click execution scripts for:
1. PyMOL (render_parp1_pymol.pml)
2. UCSF ChimeraX (render_parp1_chimerax.cxc)
3. Discovery Studio / PLIP

Creates:
- data/processed/4UND_Olaparib_complex.pdb
- data/processed/4UND_Talazoparib_complex.pdb
"""

import os
import numpy as np

def convert_vina_pose_to_pdb(protein_pdb, ligand_pdbqt, out_complex_pdb):
    """Merges protein PDB with Vina docked ligand PDBQT into a clean combined PDB."""
    with open(protein_pdb, 'r', encoding='utf-8') as f_prot:
        prot_lines = [l for l in f_prot if l.startswith("ATOM") or l.startswith("TER")]
        
    lig_lines = []
    in_model_1 = False
    atom_num = 10000
    with open(ligand_pdbqt, 'r', encoding='utf-8') as f_lig:
        for line in f_lig:
            if line.startswith("MODEL 1") or line.startswith("MODEL"):
                in_model_1 = True
            elif line.startswith("ENDMDL"):
                break
            elif in_model_1 and (line.startswith("ATOM") or line.startswith("HETATM")):
                atom_num += 1
                # Format into standard PDB HETATM record
                atom_name = line[12:16].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                elem = line[76:78].strip() if len(line) > 76 else atom_name[0]
                pdb_line = f"HETATM{atom_num:5d} {atom_name:<4s} LIG A 999    {x:8.3f}{y:8.3f}{z:8.3f}  1.00 20.00          {elem:>2s}\n"
                lig_lines.append(pdb_line)
                
    with open(out_complex_pdb, 'w', encoding='utf-8') as f_out:
        f_out.writelines(prot_lines)
        f_out.write("TER\n")
        f_out.writelines(lig_lines)
        f_out.write("END\n")
        
    print(f"Created combined complex PDB: {out_complex_pdb}")

def create_pymol_script(base_dir, complex_pdb):
    pml_path = os.path.join(base_dir, "results", "docking", "render_parp1_pymol.pml")
    pml_content = f"""# PyMOL Publication Render Script for PARP1 (4UND) + Olaparib
# Run in PyMOL: File -> Run Script -> select this file
# or from command line: pymol render_parp1_pymol.pml

reinitialize
load {complex_pdb}, parp1_complex

# 1. Background and display
bg_color white
set ray_shadows, 1
set ray_trace_mode, 1
set ray_trace_fog, 0
set antialias, 2
set ambient, 0.4
set direct, 0.6
set reflect, 0.5
set light_count, 2

# 2. Protein Cartoon Representation
hide everything, all
show cartoon, resn ALA+ARG+ASN+ASP+CYS+GLN+GLU+GLY+HIS+ILE+LEU+LYS+MET+PHE+PRO+SER+THR+TRP+TYR+VAL
color slate, resn ALA+ARG+ASN+ASP+CYS+GLN+GLU+GLY+HIS+ILE+LEU+LYS+MET+PHE+PRO+SER+THR+TRP+TYR+VAL
set cartoon_fancy_helices, 1
set cartoon_highlight_color, grey90
set cartoon_transparency, 0.2

# 3. Ligand 3D Sticks
show sticks, resn LIG
set stick_radius, 0.28
color magenta, resn LIG and elem C
color red, resn LIG and elem O
color blue, resn LIG and elem N
color green, resn LIG and elem F

# 4. Catalytic Triad Key Residues (Gly863, Tyr907, Glu988, His862, Ser904, Arg878)
select pocket_res, resi 862+863+878+904+907+988
show sticks, pocket_res
color cyan, pocket_res and elem C
set stick_radius, 0.20, pocket_res

# 5. Hydrogen Bonds Detection & Dashed Lines
distance hb1, (resn LIG and elem O+N), (resi 863 and elem N+O), 3.5
distance hb2, (resn LIG and elem O+N), (resi 907 and elem OH), 3.8
distance hb3, (resn LIG and elem O+N), (resi 988 and elem OE1+OE2), 3.5
color yellow, hb1
color yellow, hb2
color yellow, hb3
set dash_gap, 0.25
set dash_width, 2.5
set dash_radius, 0.08

# 6. Labels
set label_size, 14
set label_color, black
set label_font_id, 7
label (resi 863 and name CA), '"Gly863"'
label (resi 907 and name CA), '"Tyr907"'
label (resi 988 and name CA), '"Glu988"'
label (resi 862 and name CA), '"His862"'
label (resi 904 and name CA), '"Ser904"'
label (resi 878 and name CA), '"Arg878"'

# 7. Semi-transparent Surface on Pocket
select pocket_env, (resn LIG around 6.0)
show surface, pocket_env
set surface_color, grey90, pocket_env
set transparency, 0.65, pocket_env

# 8. Center and Orient Camera
center resn LIG
zoom resn LIG, 8

# 9. Ray-Trace and Save High-Resolution 300 DPI PNG
ray 2400, 1800
png parp1_olaparib_pymol_publication_hd.png, dpi=300
"""
    with open(pml_path, 'w', encoding='utf-8') as f:
        f.write(pml_content)
    print(f"Generated PyMOL script: {pml_path}")
    return pml_path

def create_chimerax_script(base_dir, complex_pdb):
    cxc_path = os.path.join(base_dir, "results", "docking", "render_parp1_chimerax.cxc")
    cxc_content = f"""# UCSF ChimeraX Publication Render Script
# Open ChimeraX: File -> Open -> select this .cxc file

open {complex_pdb}
set bgColor white
lighting soft
graphics silhouettes true

# Cartoon and pocket surface
hide atoms
show cartoon
color cartoon #26A69A
color cartoon/helices #00897B
color cartoon/sheets #5E35B1

# Show ligand and active site
show :LIG
style :LIG stick
color :LIG #E91E63
color :LIG & element O red
color :LIG & element N blue
color :LIG & element F green

# Show catalytic residues
show :862,863,878,904,907,988
style :862,863,878,904,907,988 stick
color :862,863,878,904,907,988 byelement

# Pocket surface
surface :LIG expand 5.0
transparency surface 60
color surface #B0BEC5

# H-Bonds
hbonds :LIG color yellow linewidth 3

# View and export
view :LIG
save parp1_chimerax_publication_hd.png width 2400 height 1800 transparentBackground false
"""
    with open(cxc_path, 'w', encoding='utf-8') as f:
        f.write(cxc_content)
    print(f"Generated ChimeraX script: {cxc_path}")
    return cxc_path

def generate_all_scripts():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prot_pdb = os.path.join(base_dir, "data", "raw", "4UND.pdb")
    olap_pdbqt = os.path.join(base_dir, "results", "docking", "real_poses", "Olaparib_out.pdbqt")
    complex_pdb = os.path.join(base_dir, "results", "docking", "4UND_Olaparib_real_complex.pdb")
    
    convert_vina_pose_to_pdb(prot_pdb, olap_pdbqt, complex_pdb)
    create_pymol_script(base_dir, complex_pdb)
    create_chimerax_script(base_dir, complex_pdb)

if __name__ == "__main__":
    generate_all_scripts()
