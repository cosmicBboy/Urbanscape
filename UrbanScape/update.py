'''
Module defining update state for the UrbanScape class
'''

import numpy as np

#==============================
#  						   	  |
#  UrbanScape Update Methods  |
#  					  	 	  |
#==============================


#------------------------------------------------
# Methods for updating agents in the UrbanScape |
#------------------------------------------------

def add_agent(UrbanScape, agent):
	UrbanScape.agents.append(agent)
	
def remove_agent(UrbanScape, agent):
	UrbanScape.agents.remove(agent)

def update_agent_locations(UrbanScape):
	'''
	agent locations are specified as -1 if FastFoodAgent, 1 if GroceryStoreAgent, and -0.5 if block has both
	these values correspond to red, green, and orange on the 'RdYlGn' colormap on matplotlib.pyplot
	'''
	u = UrbanScape
	u.agent_locations = np.zeros((u.size,u.size))
	u.agent_coords = {}
	for agent in u.agents:
		u.agent_coords[agent] = u.loc     #keeps track of type coord and type of agent
		
	#this finds redundant and single-occurring coordinates.
	#redundant coordinates are assumed to contain both 
	#FastFoodAgents and GroceryStoreAgents
	coords = self.agent_coords.values()
	set_coords = sorted(set(coords))

	for coord in set_coords:
		coords.remove(coord)
	redundant_locs = coords

	for loc in redundant_locs:
		set_coords.remove(loc)
	single_locs = set_coords

	for agent, loc in self.agent_coords.items():
	    string = str(agent)
	    x,y = loc
	    
	    if loc in redundant_locs:
	        self.agent_locations[x,y] = -0.5
	    if loc in single_locs:    
	        if 'FastFoodAgent' in string:
	            self.agent_locations[x,y] = -1               
	        if 'GroceryStoreAgent' in string:
	            self.agent_locations[x,y] = 1

#------------------------------------------
# Methods for updating economic variables |
#------------------------------------------

# defines effect radius within particular radius and location
def effect_radius(loc, radius):
	r = radius
	effect_coordinates = []
	x,y = loc
	for i in range(x-r,x+r+1):
		for j in range(y-r,y+r+1):
			effect_coordinates.append((i,j))
	return effect_coordinates

# defines the $ amount spent on fast food and groceries in blocks of given coordinates
def capture_expenditures(UrbanScape, coords):
	u = UrbanScape
	coords = coords
	ff_capture_total, gs_capture_total = 0, 0

	for k in range(len(coords)):
		x,y = coords[k]
		
		if 0 <= x <= (u.size-1) and 0 <= y <= (u.size-1):
			ff_capture = (u.fast_food[x,y] / u.ffexposure[x,y]) * u.population_per_block
			ff_capture_total += ff_capture
			
			gs_capture = (u.grocery[x,y] / u.gsexposure[x,y]) * u.population_per_block
			gs_capture_total += gs_capture
		
	return ff_capture_total, gs_capture_total


def update_income(self):
	self.income = (self.rent * 4) * self.mobility

def update_exposure(self):
	self.ffexposure = np.zeros((self.size,self.size))
	self.gsexposure = np.zeros((self.size,self.size))
	for agent in self.agents:
        string = str(agent)
        
        if 'FastFoodAgent' in string:
	     for coords in agent.effect_coordinates:
		    x,y = coords
		    if 0 <= x <= (self.size-1) and 0<= y <= (self.size-1):
			   self.ffexposure[x,y] += 1
				   
		if 'GroceryStoreAgent' in string:
		     for coords in agent.effect_coordinates:
		            x,y = coords
		            if 0 <= x <= (self.size-1) and 0<= y <= (self.size-1):
		                   self.gsexposure[x,y] += 1

def update_expenditures(self):
	#Expenditures on 'Food Away From Home'
	#Defining constants a1, b1
	a1 = 1.5802
	b1 = -0.32

	for i in range(self.size):
		for j in range(self.size):
		        rand_multiplier = self.random_float_range(0.75,1.25)
			FA = a1 * (self.income[i,j]**b1)
			self.food_away[i,j] = FA * self.income[i,j] * rand_multiplier
			
	#Expenditures on 'Fast Food Restaurants'
	#Defining constants a2, b2, c2
	a2 = 5.528e-6
	b2 = -0.332
	c2 = 0.40
	
	for i in range(self.size):
		for j in range(self.size):
		        rand_multiplier = self.random_float_range(0.75,1.25)
			FF = -(a2 * self.income[i,j] + b2)**2 + c2
			if FF < 0.075:
				FF = 0.075
			self.fast_food[i,j] = FF * self.food_away[i,j] * rand_multiplier
			
	#Expenditures on 'Food At Home', which as assumed to be all grocery expenditures
	a1 = 73.969
	b1 = -0.632
	
	for i in range(self.size):
	        for j in range(self.size):
	                rand_multiplier = self.random_float_range(0.75,1.25)
	                FH = a1 * (self.income[i,j]**b1)
	                self.grocery[i,j] = FH * self.income[i,j] * rand_multiplier


#----------------------------------------
# Methods for updating health variables |
#----------------------------------------

def update_externalities(UrbanScape):
	'''
	Externalities refer to 'negative externalities':
	ffseposure adds to externalities, and gsexposure substracts from it.
	diminishes externalities by heal_rate if exposure = 0
	'''

	heal_rate = float(0.95)

	    for i in range(self.size):
	            for j in range(self.size):
	                self.externalities[i,j] = self.externalities[i,j] + self.ffexposure[i,j] - self.gsexposure[i,j]
	                   
	                if self.externalities[i,j] <= 0:
	                    self.externalities[i,j] = 0

	                if (self.ffexposure[i,j]-self.gsexposure[i,j]) == 0:
						self.externalities[i,j] = int(self.externalities[i,j] * heal_rate)

def update_work_ability(self):
	#a logistic decay function
	#decreases mobility to limit of 'a3' as externality count approaches infinity
	
	a3 = float(0.75)
	b3 = float(1.5)
	c3 = float(50)
	
	for i in range(self.size):
		for j in range(self.size):
			E = float(self.externalities[i,j])
			M = a3 + ((1 - a3) / (1 + b3**(E - c3)))
			self.mobility[i,j] = M	

