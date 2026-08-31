# PyMOL Publication Render Script for PARP1 (4UND) + Olaparib
# Run in PyMOL: File -> Run Script -> select this file
# or from command line: pymol render_parp1_pymol.pml

reinitialize
load c:\Users\Andre\Proyectos doctorado\nano-qsar-ai-therapeutics\results\docking\4UND_Olaparib_real_complex.pdb, parp1_complex

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
