<h1>KICAD coil generator</h1>

<h2>Files</h2>

coil_generator_rev4.py

coild_generator_rev10_4.py
or coil_generator_rev10_5.py

<h2>Short description</h2>

- Script generates *.kicad_mod of a coil based on the user input provided
- Multiple settings for the radius of the edges can be select (see example for rev 4)
- Function implemented to create MxN matrices of coils (only rev4)
- Versions higher than rev10_4 add smooth transition feature between the spiral section and the connection section

<h2>Examples for revision 4</h2>

_Example for the three different settings for the edge rounding (all cu layers visible)_
![kicad_coil_gen_example_differently_rounded_edges_all_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_all_cu.png)

_Example for the three different settings for the edge rounding (F.Cu layer visible)_
![kicad_coil_gen_example_differently_rounded_edges_f_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_f_cu.png)

_Example for the three different settings for the edge rounding (B.Cu layer visible)_
![kicad_coil_gen_example_differently_rounded_edges_b_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_b_cu.png)

_Example for the three different settings for the edge rounding (3D view)_
![kicad_coil_gen_example_differently_rounded_edges_3D_all_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_3D_all_cu.png)

<h2>General</h2>

- Tested with KICAD 9.0.4
  
<h2>Known issues</h2>
- DRC raises errors due to zero clearance between PTH and traces (so far no solution found)
