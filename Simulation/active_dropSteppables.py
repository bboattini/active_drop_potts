from math import *
import random
import numpy as np

try:
    from cc3d.core.PySteppables import *
except:
    try:
        from PySteppables import *
        import CompuCell
    except:
        print("Error importing PySteppables")

import sys

time_interval = 10
class Initializer(SteppableBasePy):

    def __init__(self,_simulator,_frequency=1, parameters=None):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        if parameters is not None:
            self.drop_rad = parameters['drop_size']
            self.pillar_dist = parameters['obstacle_distance']
            self.pillar_hight = parameters['obstacle_hight']
            self.pillar_width = parameters['obstacle_width']
        else:
            self.drop_rad = 30
            self.pillar_dist = 0
            self.pillar_hight = 0
            self.pillar_width = 0
    def start(self):
        # any code in the start function runs before MCS=0
        cell = self.new_cell(self.LIQUID)										
        
        for x, y, z in self.every_pixel():											# creating a liquid drop over the substrate
            x0 = int(self.dim.x/2); y0 = int(self.dim.y/2); z0 = self.drop_rad
            r = np.sqrt((x-x0)**2+(y-y0)**2+(z-z0)**2)
            if r < self.drop_rad:
                self.cell_field[x, y, z] = cell
        
        cell = self.new_cell(self.SOLID) 											# creating a flat substrate
        self.cell_field[0:self.dim.x, 0:self.dim.y, 0] = cell
        
        pillar_min = 0
        pillar_max = self.pillar_width
        arr_pillar = []
        for x in range(self.dim.x):													# creating a micropillar substrate
            if pillar_min<=x<pillar_max:
                arr_pillar.append(1)
            elif x==pillar_max:
                    pillar_min += self.pillar_width + self.pillar_dist
                    pillar_max += self.pillar_width + self.pillar_dist
                    arr_pillar.append(1)
            else:
                arr_pillar.append(0)
        for x, y, z in self.every_pixel():
            if arr_pillar[x]==1 and arr_pillar[y]==1 and z<self.pillar_hight:
                self.cell_field[x, y, z] = cell
                
        pass
    def step(self,mcs):  
        
        pass      
        #type here the code that will run every _frequency MCS
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
                
                if polarization != 0:
                    cell.lambdaVecX -= self.motility * polarization_x/polarization  # force component along X axis
                    cell.lambdaVecY -= self.motility * polarization_y/polarization  # force component along Y axis
                    cell.lambdaVecZ -= 0.0
                else:
                    cell.lambdaVecX = 0.0  # force component along X axis
                    cell.lambdaVecY = 0.0  # force component along Y axis
                    cell.lambdaVecZ = 0.0
                cell.dict['angle'] = atan2(-polarization_y,-polarization_x) 
                
                if cell.type == 2:
                    cell.dict['angle'] = -0.7
        

class Measures_and_Plot(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1, parameters=None):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        if parameters is not None:
            self.drop_rad = parameters['drop_size']
            self.pillar_dist = parameters['obstacle_distance']
            self.pillar_hight = parameters['obstacle_hight']
            self.pillar_width = parameters['obstacle_width']
        else:
            self.drop_rad = 30
            self.pillar_dist = 0
            self.pillar_hight = 0
            self.pillar_width = 0  

    def start(self):
		# creating window to plot B and H overtime
        self.plot_win = self.add_new_plot_window(title='Geometry',x_axis_title='x',y_axis_title='y', x_scale_type='linear', y_scale_type='linear',grid=False)
        self.plot_win.add_plot("B", style='Lines', color='red', size=5)
        self.plot_win.add_plot("H", style='Lines', color='green', size=5)

    def step(self,mcs):  
        if mcs%time_interval==0:											# selcting pixels by cell id
            cell = self.fetch_cell_by_id(1)
            pixel_list = self.get_cell_pixel_list(cell)
            pixel_arr = []                     
            

            for pixel_data in pixel_list:									# saving pixels coordinates
                pixel_arr.append(self.point_3d_to_numpy(pixel_data.pixel))
            pixel_arr = np.array(pixel_arr)
            z_cords = pixel_arr[:,2]
            y_cords = pixel_arr[:,1]
            x_cords = pixel_arr[:,0]
			# calculating B and H
            By_max = np.max(y_cords[z_cords == self.pillar_hight+1]) - np.min(y_cords[z_cords == self.pillar_hight+1])
            Bx_max = np.max(x_cords[z_cords == self.pillar_hight+1]) - np.min(x_cords[z_cords == self.pillar_hight+1])
            B = (By_max + Bx_max)/4
            H = np.max(z_cords) - self.pillar_hight
			# plotting and printing B and H data
            self.plot_win.add_data_point("B", mcs, B)
            self.plot_win.add_data_point("H", mcs, H)
            print("Bx=",Bx_max/2,"   By=",By_max/2,"   H=", H,"   sin=", 2*H*B/(H**2 + B**2))
        pass  
        
    def finish(self):
        # Finish Function gets called after the last MCS
        pass
