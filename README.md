<h1>KICAD coil generator</h1>

**FILES:**

coil_generator_rev4.py
coild_generator_rev10_4.py or coil_generator_rev10_5.py

**SHORT DESCRIPTION**

- Script generates *.kicad_mod of a coil based on the user input provided in file.
- Function implemented to create MxN matrices of coils (only rev4)

**Examples for revision 4:**

_Example for the three different settings for the edge rounding (all cu layers visible)_
![kicad_coil_gen_example_differently_rounded_edges_all_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_all_cu.png)

_Example for the three different settings for the edge rounding (F.Cu layer visible)_
![kicad_coil_gen_example_differently_rounded_edges_f_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_f_cu.png)

_Example for the three different settings for the edge rounding (B.Cu layer visible)_
![kicad_coil_gen_example_differently_rounded_edges_b_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_b_cu.png)

_Example for the three different settings for the edge rounding (3D view)_
![kicad_coil_gen_example_differently_rounded_edges_3D_all_cu](https://github.com/MIPIthon/kicad_coil_generator/blob/main/rev_4/kicad_coil_gen_example_differently_rounded_edges_3D_all_cu.png)

**GENERAL**

- Tested with KICAD 9.0.4

**KNOWN ISSUE**
- DRC raises errors due to zero clearance between PTH and traces (so far no solution found)
