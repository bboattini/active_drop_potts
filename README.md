# active_drop_potts
Compucell3d project that simulates a drop of active material in a surface with texture

# Requirements

The scripts were written for Compucell3d version 3.7.8 running in Ubuntu 18.04. You can 
find all installing infomation in [Compucell3d](https://compucell3d.org/).

# Getting Started

You can open the active_drop project in the Tweedit++ and run Compucell3D from it.
Or you can directly run Compucell3d and open the project from it.


# Editing Parameters

The file parameters_inputs.py defines a dictionary with all parameters.
Edit this file to change any simulation parameters.

| Parameter | Value | Description |
| --- | --- | --- |
| size_x |  100 | Number of pixels in the x direction |
| size_y |  100 | Number of pixels in the y direction |
| size_z |  100 | Number of pixels in the z direction |
| MC_steps |  1000 | Number of Monte-Carlo steps the simulation will run |
| temperature |  10.0 | Temperature in Potts Model |
| drop_size |  30 | Initial size of the drop (the volume is drop_size**3) | 
| energy_gas_gas | 0.0 | Tension beetween gas and gas pixels |
| energy_gas_liq | 10.0 | Tension beetween gas and liquid pixels |
| energy_gas_sol | 10.0 | Tension beetween gas and solid pixels |
| energy_liq_liq | 10.0 | Tension beetween liquid and liquid pixels |
| energy_liq_sol | 20.0 | Tension beetween liquid and solid pixels  |
| energy_sol_sol | 100.0 | Tension beetween solid and solid pixels |
| obstacle_hight |  5 | floor obstacle height |
| obstacle_width |  5 | floor obstacle width |
| obstacle_distance |  5 | floor obstacle space between obstacles |
| gravity |  50 | value of gravity on z axis |
| motility |  100 | cell motility level, a drop with motility = 0 is passive |
| persistance |  0.9 | Fraction of the polarity that persist, the 1-persistance comes from the real displacement [0.0, 1.0) |

# Active Drop

The [Active Drop]{Simulation/active_drop.py} defines the simulation setuo. 
Edit this file to change the initial configuration and compucell properties.

# Steppables

The file [Active Drop Steppables](active_dropSteppables.py) defines the external potential 
acting on cells. 

The Gravity class defines the gravitational potential on cells,

The CellMotilitySteppable class defines the cell motility. In the case, the drop is simulated as
a single cell from the Cellular Potts Model working in the Compucell3D.

