def configureSimulation(sim, parameters):
    import CompuCellSetup
    from XMLUtils import ElementCC3D
    
    CompuCell3DElmnt=ElementCC3D("CompuCell3D",{"Revision":"20180728","Version":"3.7.8"})
    
    PottsElmnt=CompuCell3DElmnt.ElementCC3D("Potts")
    
    # Basic properties of CPM (GGH) algorithm
    PottsElmnt.ElementCC3D("Dimensions",{"x":parameters['size_x'],"y":parameters['size_y'],"z":parameters['size_z']})
    PottsElmnt.ElementCC3D("Steps",{},parameters['MC_steps'])
    PottsElmnt.ElementCC3D("Temperature",{},parameters['temperature'])
    PottsElmnt.ElementCC3D("NeighborOrder",{},"3")
    
    PluginElmnt=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CellType"})
    
    # Listing all cell types in the simulation
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"0","TypeName":"Medium"})
    PluginElmnt.ElementCC3D("CellType",{"TypeId":"1","TypeName":"Liquid"})
    PluginElmnt.ElementCC3D("CellType",{"Freeze":"","TypeId":"2","TypeName":"Solid"})
    
    target_volume = parameters['drop_size']**3
    
    PluginElmnt_1=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Volume"})
    PluginElmnt_1.ElementCC3D("VolumeEnergyParameters",{"CellType":"Liquid","LambdaVolume":"2.0","TargetVolume":target_volume})
    
    PluginElmnt_2=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"ExternalPotential"})
    
    # External force applied to cell. Each cell has different force and force components have to be managed in Python.
    # e.g. cell.lambdaVecX=0.5; cell.lambdaVecY=0.1 ; cell.lambdaVecZ=0.3;
    PluginElmnt_2.ElementCC3D("Algorithm",{},"PixelBased")
    
    PluginElmnt_3=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"CenterOfMass"})
    
    # Module tracking center of mass of each cell
    
    PluginElmnt_4=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"NeighborTracker"})
    
    # Module tracking neighboring cells of each cell
    
    PluginElmnt_5=CompuCell3DElmnt.ElementCC3D("Plugin",{"Name":"Contact"})
    # Specification of adhesion energies
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Medium"},parameters['energy_gas_gas'])
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Liquid"},parameters['energy_gas_liq'])
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Medium","Type2":"Solid"},parameters['energy_gas_sol'])
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Liquid","Type2":"Liquid"},parameters['energy_liq_liq'])
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Liquid","Type2":"Solid"},parameters['energy_liq_sol'])
    PluginElmnt_5.ElementCC3D("Energy",{"Type1":"Solid","Type2":"Solid"},parameters['energy_sol_sol'])
    PluginElmnt_5.ElementCC3D("NeighborOrder",{},"1")
    
    SteppableElmnt=CompuCell3DElmnt.ElementCC3D("Steppable",{"Type":"UniformInitializer"})
    
    # Floor
    RegionElmnt=SteppableElmnt.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("BoxMin",{"x":"1","y":"1","z":"1"})
    RegionElmnt.ElementCC3D("BoxMax",{"x":parameters['size_x'],"y":parameters['size_y'],"z":"5"})
    RegionElmnt.ElementCC3D("Gap",{},"0")
    RegionElmnt.ElementCC3D("Width",{},"5")
    RegionElmnt.ElementCC3D("Types",{},"Solid")
    
    parameters['obstacle_hight'] += 5
    # Obstacles
    RegionElmnt=SteppableElmnt.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("BoxMin",{"x":"1","y":"1","z":"5"})
    RegionElmnt.ElementCC3D("BoxMax",{"x":parameters['size_x'],"y":parameters['size_y'],"z":parameters['obstacle_hight']})
    RegionElmnt.ElementCC3D("Gap",{},parameters['obstacle_distance'])
    RegionElmnt.ElementCC3D("Width",{},parameters['obstacle_width'])
    RegionElmnt.ElementCC3D("Types",{},"Solid")
    
    x_center = parameters['size_x']/2
    y_center = parameters['size_y']/2
        
    drop_half_size = parameters['drop_size']/2
    
    RegionElmnt=SteppableElmnt.ElementCC3D("Region")
    RegionElmnt.ElementCC3D("BoxMin",{"x":x_center - drop_half_size,"y":y_center - drop_half_size,"z":parameters['obstacle_hight']})
    RegionElmnt.ElementCC3D("BoxMax",{"x":x_center + drop_half_size,"y":y_center + drop_half_size,"z":parameters['obstacle_hight']+parameters['drop_size']})
    RegionElmnt.ElementCC3D("Gap",{},"0")
    RegionElmnt.ElementCC3D("Width",{},parameters['drop_size'])
    RegionElmnt.ElementCC3D("Types",{},"Liquid")

    CompuCellSetup.setSimulationXMLDescription(CompuCell3DElmnt)    
    

            
import sys
from os import environ
from os import getcwd
import string
import os.path

import CompuCellSetup

# for var in dir(CompuCellSetup):
#     print(var)

import inspect
source_file_path_with_name = inspect.getfile(inspect.currentframe())
file_name = os.path.basename(source_file_path_with_name)
source_file_path = source_file_path_with_name.replace(file_name,'')

if source_file_path not in sys.path:
    sys.path.append(source_file_path)
    
from parameters_inputs import *
    
sim,simthread = CompuCellSetup.getCoreSimulationObjects()

configureSimulation(sim, parameters)            
            
# add extra attributes here
        
CompuCellSetup.initializeSimulationObjects(sim,simthread)
# Definitions of additional Python-managed fields go here
        
#Add Python steppables here
steppableRegistry=CompuCellSetup.getSteppableRegistry()

from active_dropSteppables import Gravity
steppableInstance=Gravity(sim,_frequency=1, parameters=parameters)
steppableRegistry.registerSteppable(steppableInstance)

from active_dropSteppables import CellMotilitySteppable
steppableInstance=CellMotilitySteppable(sim,_frequency=1, parameters=parameters)
steppableRegistry.registerSteppable(steppableInstance)
CellMotilitySteppable
        
CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
        