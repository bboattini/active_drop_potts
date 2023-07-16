from math import *
import random
import numpy as np

from PySteppables import *
import CompuCell
import sys
class drop_passiveSteppable(SteppableBasePy):

    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        # any code in the start function runs before MCS=0
        pass
    def step(self,mcs):  
        pass      
        #type here the code that will run every _frequency MCS
#         for cell in self.cellList:
#             print "cell.id=",cell.id
    def finish(self):
        # Finish Function gets called after the last MCS
        pass
      
class Gravity(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1, parameters=None):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        if parameters is not None:
            self.gravity = parameters['gravity']
        else:
            self.gravity = 0.0
    def start(self):
        for cell in self.cellList:
            cell.lambdaVecX = 0.0
            cell.lambdaVecY = 0.0
            cell.lambdaVecZ = self.gravity
    def step(self,mcs):  
        for cell in self.cellList:
            cell.lambdaVecX = 0.0
            cell.lambdaVecY = 0.0
            cell.lambdaVecZ = self.gravity
    def finish(self):
        # Finish Function gets called after the last MCS
        pass

        
class CellMotilitySteppable(SteppableBasePy):
    def __init__(self, _simulator, _frequency=1, parameters = None):
        SteppableBasePy.__init__(self, _simulator, _frequency)
        self.track_cell_level_scalar_attribute(field_name='ANGLE', attribute_name='angle')
        if parameters is not None:
            self.motility = parameters['motility']
            self.persistance = parameters['persistance']
        else:
            self.motility = 0.0
            self.persistance = 0.0
    def start(self):
        for cell in self.cellList:    
            if cell.type == 1:
                #init_angle = 6.283185 * random.random() - 3.14159
                init_angle = 0.0
                cell.lambdaVecX = self.motility * cos(init_angle)
                cell.lambdaVecY = self.motility * sin(init_angle)
                cell.dict['angle'] = init_angle
            else:
                cell.dict['angle'] = -0.7        
    def step(self, mcs):        
        if mcs > 1:
            for cell in self.cellList:
                displ_x = cell.xCOM - cell.xCOMPrev
                displ_y = cell.yCOM - cell.yCOMPrev
                displ_z = cell.zCOM - cell.zCOMPrev     
                displacement = [displ_x, displ_y, displ_z, sqrt(displ_x * displ_x + displ_y * displ_y + displ_z * displ_z)]
                if displacement[3] == 0.0:
                    displacement[3] = 1.0
                
                polarization_x = 0.0
                polarization_y = 0.0
                polarization_z = 0.0
                
                # keep old angle
                polarization_x -= self.persistance * cos(cell.dict['angle'])
                polarization_y -= self.persistance * sin(cell.dict['angle'])
                # follow true displacement
                polarization_x -= (1-self.persistance) * displacement[0]/displacement[3]
                polarization_y -= (1-self.persistance) * displacement[1]/displacement[3]

                polarization = sqrt(polarization_x * polarization_x + 
                polarization_y * polarization_y + polarization_z * polarization_z)
                
                cell.lambdaVecX -= self.motility * polarization_x/polarization  # force component along X axis
                cell.lambdaVecY -= self.motility * polarization_y/polarization  # force component along Y axis
                cell.lambdaVecZ -= 0.0
                cell.dict['angle'] = atan2(-polarization_y,-polarization_x) 
                
                if cell.type == 2:
                    cell.dict['angle'] = -0.7
        