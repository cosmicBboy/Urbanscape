import numpy as np
import numpy.random as random
import matplotlib.pyplot as pyplot

#Urbanscape v1.4

#Changes:
# randomized the income and rent distribution functions with a random multiplier
# added an element of randomness to the FAFH and FFR functions using a random float multiplier
# changed the FFR function such that the domain of incomes that yield a percent < 0.5% and beyond follows the function f(x) = 0.005
# added a GroceryStore Agent
# added an attribute to the UrbanScape class for income spent on groceries

#-------------------------------------
# Basic Classes: UrbanScape and Agent |
#-------------------------------------

class UrbanScape(object):
	# The urbanscape defines the context within which agents act
	population_per_block = 20

	#size = size of the urban grid
	#rent = yearly cost of commercial and residential space
	def __init__(self, size, rent, create_rule=None, gradient = None, randomize = False):
		blocks = np.ones((size,size))

		self.create_rule = create_rule
		self.size = size
		self.agents = []
		self.agent_locations = np.zeros((self.size,self.size))
		self.agent_coords = {}
		self.time = 0
		self.rent_ceiling = rent
		self.rent_floor = 5000
		self.rent = np.ones_like(blocks) * self.rent_ceiling	#distribution of rent on urbanscape

		if gradient == 'vertical':
			self.vertical_distribution()
		elif gradient == 'diagonal':
			self.diagonal_distribution()
		elif gradient == 'random':
			self.random_distribution()
		elif gradient == 'BDquadrants':
			self.businessdistricts_quadrant_distribution()
		elif gradient == 'CBD':
			self.centralbusinessdistrict_distribution()
					
		self.income = np.ones_like(blocks) * self.rent * 4
		
		if randomize == True:
			self.randomize_distribution()
		
		self.externalities = np.zeros_like(blocks)		#total count of (negative) externality effect
		self.ffcapture_number = np.zeros_like(blocks)	#count of FastFoodAgent effect in UrbanScape
		self.gscapture_number = np.zeros_like(blocks)   #count of GroceryStoreAgent effect in UrbanScape
		self.mobility = np.ones_like(blocks)			#a measure of disability
		self.food_away = np.ones_like(blocks)			#distribution of food-related expenditures per block
		self.fast_food = np.ones_like(blocks)
		self.grocery = np.ones_like(blocks)
		self.update_expenditures()
	
	def add_agent(self, agent):
		self.agents.append(agent)
		
	def remove_agent(self, agent):
		self.agents.remove(agent)
	
	# defines effect radius within particular radius and location
	def effect_radius(self, loc, radius):
		r = radius
		effect_coordinates = []
		x,y = loc
		for i in range(x-r,x+r+1):
			for j in range(y-r,y+r+1):
				effect_coordinates.append((i,j))
		return effect_coordinates
	
	# defines the $ amount spent on fast food and groceries in blocks of given coordinates
	def capture_expenditures(self, coords):
		coords = coords
		ffexposure_total = 0
		gsexposure_total = 0
		
		for k in range(len(coords)):
			x,y = coords[k]
			
			if 0 <= x <= (self.size-1) and 0 <= y <= (self.size-1):
				ffexposure = (self.fast_food[x,y] / (self.ffcapture_number[x,y] + 1e-10)) * self.population_per_block
				ffexposure_total += ffexposure
				
				gsexposure = (self.grocery[x,y] / (self.gscapture_number[x,y] + 1e-10)) * self.population_per_block
				gsexposure_total += gsexposure
			
		return ffexposure_total, gsexposure_total

	def update_agent_locations(self):
		#agent locations are specified as -1 if FastFoodAgent, 1 if GroceryStoreAgent, and -0.5 if block has both
		#these values correspond to red, green, and orange on the 'RdYlGn' colormap on matplotlib.pyplot
		self.agent_locations = np.zeros((self.size,self.size))
		self.agent_coords = {}
		for aa in self.agents:
			self.agent_coords[aa] = aa.loc     #keeps track of type coord and type of agent
			
		#this finds redundant and single-occurring coordinates.
		#redundant coordinates are assumed to contain both FastFoodAgents and GroceryStoreAgents
		coords = self.agent_coords.values()
		set_coords = sorted(set(coords))
		
		for i in set_coords:
			coords.remove(i)
		redundant_locs = coords
		
		for i in redundant_locs:
			try:
				set_coords.remove(i)
			except:
				pass
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

	def update_income(self):
		self.income = (self.rent * 4) * self.mobility
	
	def update_capture_number(self):
		self.ffcapture_number = np.zeros((self.size,self.size))
		self.gscapture_number = np.zeros((self.size,self.size))
		for agent in self.agents:
			string = str(agent)

			if 'FastFoodAgent' in string:
				for coords in agent.effect_coordinates:
					x,y = coords
					if 0 <= x <= (self.size-1) and 0<= y <= (self.size-1):
						self.ffcapture_number[x,y] += 1

			if 'GroceryStoreAgent' in string:
				for coords in agent.effect_coordinates:
					x,y = coords
					if 0 <= x <= (self.size-1) and 0<= y <= (self.size-1):
						self.gscapture_number[x,y] += 1

	def update_externalities(self):
		#externalities here are 'negative externalities':
		#ffscapture_number adds to externalities, and gscapture_number substracts from it.
		#diminishes externalities by heal_rate if capture_number = 0
		heal_rate = float(0.95)

		for i in range(self.size):
			for j in range(self.size):
				self.externalities[i,j] = self.externalities[i,j] + self.ffcapture_number[i,j] - self.gscapture_number[i,j]

				if self.externalities[i,j] <= 0:
					self.externalities[i,j] = 0

				if (self.ffcapture_number[i,j]-self.gscapture_number[i,j]) == 0:
					self.externalities[i,j] = int(self.externalities[i,j] * heal_rate)
		
	def update_mobility(self):
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
	
#-----------------------------------------
# Rent and Income Distribution Functions |
#-----------------------------------------

	#Defining types of block rent distributions, which also determines income level
	def vertical_distribution(self):
		
		gradient = float((self.rent_ceiling - self.rent_floor)/(self.size-1))
		g_multiplier = float(gradient/self.rent_ceiling)
		fr_ratio = float(self.rent_floor)/float(self.rent_ceiling)
		
		for i in range(self.size):
			gg = float(fr_ratio + g_multiplier*i)
			self.rent[i] = self.rent[i] * gg
				
	def diagonal_distribution(self):
		
		gradient = float((self.rent_ceiling - self.rent_floor)/(self.size-1))
		g_multiplier = float(gradient/self.rent_ceiling)
		fr_ratio = float(self.rent_floor/self.rent_ceiling)
		
		for i in range(self.size):
			gg = float(fr_ratio + g_multiplier*i)
			self.rent[i] = self.rent[i] * gg
		for j in range(self.size):
			gg = float(fr_ratio + g_multiplier*j)
			self.rent[:,j] = self.rent[:,j] * gg
			
	def random_distribution(self):
		dist = np.random.randint(self.rent_floor, self.rent_ceiling,(self.size,self.size))
		self.rent = dist
        
        #calculates the rent based on distance from the business district block
        def distance_rent_function(self,quadrant_coords,bd_coords):
                q = quadrant_coords
                bd = bd_coords
                x_dist = float(q[0] - bd[0])
                y_dist = float(q[1] - bd[1])
                dist = np.sqrt(x_dist**2 + y_dist**2)
                return dist      
        
        def exponential_rent_function(self,distance,coord):
                i,j = coord
                Lambda = np.log(float(self.rent_floor)/float(self.rent_ceiling)) * (-1/self.dmax)
                rent_value = self.rent_ceiling * np.e**(-Lambda*distance)
                self.rent[i][j] = rent_value
                
        def linear_rent_function(self,distance,coord):
                i,j = coord
                Alpha = (float(self.rent_floor)-float(self.rent_ceiling))/self.dmax
                rent_value = self.rent_ceiling + (Alpha * distance)
                self.rent[i][j] = rent_value
        
        #the approximate center of each quadrant of the urbanscape is a 'business district'
        #the assumption being that rent and income decreases as one moves further away
        def businessdistricts_quadrant_distribution(self):
                district1 = [(i,j) 
                    for i in range(int(np.ceil(float(self.size)*0.5)))
                    for j in range(int(np.ceil(float(self.size)*0.5)))]
                district2 = [(i,j) 
                    for i in range(int(np.ceil(float(self.size)*0.5)),self.size)
                    for j in range(int(np.ceil(float(self.size)*0.5)))]
                district3 = [(i,j) 
                    for i in range(int(np.ceil(float(self.size)*0.5)))
                    for j in range(int(np.ceil(float(self.size)*0.5)),self.size)]
                district4 = [(i,j) 
                    for i in range(int(np.ceil(float(self.size)*0.5)),self.size)
                    for j in range(int(np.ceil(float(self.size)*0.5)),self.size)]
            
                d1_coords = (np.ceil(float(self.size) * 0.25), np.ceil(float(self.size)* 0.25))
                d2_coords = (np.ceil(float(self.size) * 0.75), np.ceil(float(self.size)* 0.25))
                d3_coords = (np.ceil(float(self.size) * 0.25), np.ceil(float(self.size)* 0.75))
                d4_coords = (np.ceil(float(self.size) * 0.75), np.ceil(float(self.size)* 0.75))
        
                d1_distances = [self.distance_rent_function(q,d1_coords) for q in district1]
                d2_distances = [self.distance_rent_function(q,d2_coords) for q in district2]
                d3_distances = [self.distance_rent_function(q,d3_coords) for q in district3]
                d4_distances = [self.distance_rent_function(q,d4_coords) for q in district4]
                
                self.dmax = max(d1_distances)
                
                for i in range(len(district1)):
                    self.exponential_rent_function(d1_distances[i], district1[i])
                    self.exponential_rent_function(d2_distances[i], district2[i])
                    self.exponential_rent_function(d3_distances[i], district3[i])
                    self.exponential_rent_function(d4_distances[i], district4[i])
        
        def centralbusinessdistrict_distribution(self):
                block_coords = [(i,j)
                    for i in range(self.size)
                    for j in range(self.size)]
                district_coords = (np.ceil(float(self.size) *0.5), np.ceil(float(self.size)*0.5))
                block_distances = [self.distance_rent_function(q,district_coords) for q in block_coords]
                self.dmax = max(block_distances)
                
                for i in range(len(block_coords)):
                    #self.linear_rent_function(block_distances[i], block_coords[i])
                    self.exponential_rent_function(block_distances[i],block_coords[i])
        
        #a function that randomizes the rent and income values (independently) within an error of 20%
        def randomize_distribution(self):
                for i in range(self.size):
                    for j in range(self.size):
                        randfloat = self.random_float_range(0.75,1.25)
                        
                        if self.rent[i][j] * randfloat > self.rent_ceiling:
                            pass
                        else:
                            self.rent[i][j] *= randfloat
                
                for i in range(self.size):
                    for j in range(self.size):
                        randfloat = self.random_float_range(0.75,1.25)
                        
                        if self.income[i][j] * randfloat > (self.rent_ceiling * 4):
                            pass
                        else:
                            self.income[i][j] *= randfloat
                
        #a function that generates a random float between a specified range
        def random_float_range(self, low, high):
                randfloat = np.random.random() * (high - low) + low
                return randfloat
        
	def step(self):
		self.create_rule(self)

		#Update externality-related attributes
		self.update_agent_locations()
		self.update_capture_number()
		self.update_externalities()
		self.update_mobility()
		self.update_income()
		self.update_expenditures()
		
		#Agent actions
		for agent in self.agents:
			agent.step(self)
		
		#Time step
		self.time += 1

#---------------------------------
# Base class for all Food Agents |
#---------------------------------

class Agent(object):
    def __init__(self, loc, wealth):
		self.loc = loc		# x,y coordinates of location in urbanscape
		self.wealth = wealth	# $ amount

	# Called every time-step
    def step(self, urbanscape):
		self.check_bankruptcy(urbanscape)
		
	# Remove the agent if broke
    def check_bankruptcy(self, urbanscape):
		if self.wealth < 0:
			self.wealth = 0
			urbanscape.remove_agent(self)

class FastFoodAgent(Agent):
	operations = 50000	# $ per year
	initial_wealth = 10000	# $ amount
	radius = 2	# number of block effected around location
	effect_coordinates = []

	def __init__(self, loc, urbanscape):
		super(FastFoodAgent, self).__init__(loc, self.initial_wealth)
		self.define_radius(urbanscape)
		self.operating_costs = (urbanscape.rent[loc]) + (FastFoodAgent.operations)
	def step(self, urbanscape):
		# 1. Gather revenues for the year
		self.capture_revenue(urbanscape)
		
		# 2. Perform parent class step function
		super(FastFoodAgent, self).step(urbanscape)
	
	#this function defines how much of fast food expenditures are
	#captured by the FoodAgent. If there are no competing FastFoodAgents,
	#assumes that FoodAgent captures all of block expenditures.
	
	def define_radius(self, urbanscape):
		self.effect_coordinates = urbanscape.effect_radius(self.loc, self.radius)
	
	def capture_revenue(self, urbanscape):
		x,y = self.loc
		self.wealth += (urbanscape.capture_expenditures(self.effect_coordinates)[0]) - self.operating_costs
		#capture_expenditures returns a list of two values, the 0th index being the ff_revenues

class GroceryStoreAgent(Agent):
	operations = 200000	# $ per year
	initial_wealth = 25000	# $ amount
	radius = 2	# number of block effected around location
	effect_coordinates = []

	def __init__(self, loc, urbanscape):
		super(GroceryStoreAgent, self).__init__(loc, self.initial_wealth)
		self.define_radius(urbanscape)
		self.operating_costs = (urbanscape.rent[loc]) + (GroceryStoreAgent.operations)
	def step(self, urbanscape):
		# 1. Gather revenues for the year
		self.capture_revenue(urbanscape)
		
		# 2. Perform parent class step function
		super(GroceryStoreAgent, self).step(urbanscape)
	
	#this function defines how much of grocery store expenditures are
	#captured by the FoodAgent. If there are no competing FoodAgents,
	#assumes that FoodAgent captures all of block expenditures.
	
	def define_radius(self, urbanscape):
		self.effect_coordinates = urbanscape.effect_radius(self.loc, self.radius)
	
	#assumes that the rest of income spent on food away from home is spent on groceries
	def capture_revenue(self, urbanscape):
		x,y = self.loc
		self.wealth += (urbanscape.capture_expenditures(self.effect_coordinates)[1]) - self.operating_costs
		#capture_expenditures returns a list of two values, the 1st index being the ff_revenues
						
									
#------------------------
# Create Rule Functions |
#------------------------

def no_create_rule(urbanscape):
	pass

#creates FastFoodAgents randomly on the grid
def random_create_rule(urbanscape):
	x = random.randint(0,urbanscape.size)
	y = random.randint(0,urbanscape.size)

	if urbanscape.time % 5 == 0:
		agent_type_decision = random.rand()
		if agent_type_decision < 0.5:
			urbanscape.add_agent(FastFoodAgent((x,y),urbanscape))
		else:
			urbanscape.add_agent(GroceryStoreAgent((x,y),urbanscape))

#adds new FastFoodAgent in location with highest potential profit to cost ratio
def profit_probability_create_rule(urbanscape):
	size = urbanscape.size
	potential_fflocations = []
	potential_gslocations = []
	
	#makes a list of available coordinates in UrbanScape
	#only one FastFoodAgent and one GroceryStoreAgent can occupy a block at any given time
	for i in range(size):
		for j in range(size):
		        ff_locs = [loc for agent,loc in urbanscape.agent_coords.items() if 'FastFoodAgent' in str(agent)]
		        gs_locs = [loc for agent,loc in urbanscape.agent_coords.items() if 'GroceryStoreAgent' in str(agent)]
			if (i,j) not in ff_locs:
				potential_fflocations.append((i,j))
			if (i,j) not in gs_locs:
			        potential_gslocations.append((i,j))
	
	#makes a list of profit:cost ratios at potential_location coordinates
	potential_fflist = potential_profits(urbanscape, potential_fflocations, agent = 'FF')
	potential_gslist = potential_profits(urbanscape, potential_gslocations, agent = 'GS')
	
	if not potential_fflist and not potential_gslist:
		print 'no suitable locations at time ' + str(urbanscape.time)
		
	if potential_fflist:
	       potential_creations(urbanscape, potential_fflocations, potential_fflist,agent='FF')
	   
	if potential_gslist:
	       potential_creations(urbanscape, potential_gslocations, potential_gslist,agent='GS')

#a function that creates agents 
def potential_creations(urbanscape, potential_locations, potential_list,agent = ''):
        #generates a random float to make the 'create agent' decision
       	prob_max = 0.15
        rand = random.random()
        maximum = max(potential_list)
	create_locations = []
	
	#generates a 'create' probability based on profit:cost ratios in potential_list
	#modifies prob_max value by a multiplier based on profit ranges
	for i in range(len(potential_list)):
		prob_multiplier = float(potential_list[i])/float(maximum)
		if prob_multiplier < 0:
			prob_multiplier = 0
		probability = prob_max * prob_multiplier
			
		#adds the location to create_locations if the 'create agent' decision
		#is less that the create probability
		if rand < probability:
			create_locations.append(potential_locations[i])
		
	#picks a random location from list of locations that made it through the
	#random 'create agent' decision.
	if create_locations:
		choice = random.randint(0,len(create_locations))
		create_coord = create_locations[choice]
		
		if agent == 'FF':
		      urbanscape.add_agent(FastFoodAgent(create_coord, urbanscape))
		      
		if agent == 'GS':
		      urbanscape.add_agent(GroceryStoreAgent(create_coord, urbanscape))

def potential_profits(urbanscape, potential_locations, agent = ''):
	urbanscape = urbanscape
	locations = potential_locations
	location_profit_list = []
	for loc in locations:
	        if agent == 'FF':
	               startup = (urbanscape.rent[loc]) + (FastFoodAgent.operations)*2
	               potential_radius = urbanscape.effect_radius(loc,FastFoodAgent.radius)
	               revenue = potential_revenue(urbanscape,potential_radius,agent)
	               profits_short = revenue - startup
	               profits_long = (revenue - FastFoodAgent.operations) * 5
	               profit_margin = (profits_short/startup) + (profits_long / (FastFoodAgent.operations*5))
	               location_profit_list.append(profit_margin)
	       
	        if agent == 'GS':
	               startup = (urbanscape.rent[loc]) + (GroceryStoreAgent.operations)*2
	               potential_radius = urbanscape.effect_radius(loc,GroceryStoreAgent.radius)
	               revenue = potential_revenue(urbanscape,potential_radius,agent)
	               profits_short = revenue - startup
	               profits_long = (revenue - GroceryStoreAgent.operations) * 5
	               profit_margin = (profits_short/startup) + (profits_long / (GroceryStoreAgent.operations*5))
	               location_profit_list.append(profit_margin)
	               
	return location_profit_list
			
#define create rule variables
def potential_revenue(urbanscape, coords, agent = ''):
		coords = coords
		s = urbanscape.size
		ff = urbanscape.fast_food
		gs = urbanscape.grocery
		ff_cn = urbanscape.ffcapture_number
		gs_cn = urbanscape.gscapture_number
		capture_total = 0
		
		if agent == 'FF':
		      for k in range(len(coords)):
		          x,y = coords[k]
		          if 0 <= x <= (s-1) and 0 <= y <= (s-1):
		              cc = (ff[x,y] / (ff_cn[x,y]+1)) * urbanscape.population_per_block
		              capture_total += cc
		
		if agent == 'GS':
		      for k in range(len(coords)):
		          x,y = coords[k]
		          if 0 <= x <= (s-1) and 0 <= y <= (s-1):
		              cc = (gs[x,y] / (gs_cn[x,y]+1)) * urbanscape.population_per_block
		              capture_total += cc
		                      
		return capture_total

#---------------------------------------
# Functions for Visualizing UrbanScape |
#---------------------------------------

def plot_urbanscape(urbanscape):
	fig = pyplot.figure()
	
	pyplot.clf()
	pyplot.subplot(221)
	ii = urbanscape.income
	pyplot.imshow(ii, interpolation='nearest')
	pyplot.title("Income Distribution")
	pyplot.subplot(221).axes.get_xaxis().set_ticks([])
	pyplot.subplot(221).axes.get_yaxis().set_ticks([])

	pyplot.subplot(222)
	ff = urbanscape.ffcapture_number
	pyplot.imshow(ff, cmap = 'YlOrRd', interpolation='nearest')
	pyplot.title("FFR Effect Radii")
	pyplot.subplot(222).axes.get_xaxis().set_ticks([])
	pyplot.subplot(222).axes.get_yaxis().set_ticks([])

	pyplot.subplot(223)
	mm = urbanscape.externalities
	pyplot.imshow(mm, cmap = 'Purples', interpolation='nearest')
	pyplot.title("Negative Externalities")
	pyplot.subplot(223).axes.get_xaxis().set_ticks([])
	pyplot.subplot(223).axes.get_yaxis().set_ticks([])
	
	pyplot.subplot(224)
	ll = urbanscape.agent_locations
	pyplot.imshow(ll, cmap = 'RdYlGn', interpolation='nearest',vmin=-1,vmax=1)
	pyplot.title("Food Agent Locations")
	pyplot.subplot(224).axes.get_xaxis().set_ticks([])
	pyplot.subplot(224).axes.get_yaxis().set_ticks([])
	
	#return fig

#------------------------------------------------------------------------------
# Running Simulations that Returns Externalities Exposures by Income Quintile |
#------------------------------------------------------------------------------

def run_experiment(grid_size, rent_ceiling, create_rule, distribution, randomize = True, steps = 100):
	
	n = grid_size
	ceiling = rent_ceiling
	create_rule = create_rule
	steps = steps
	
	#defining the urbanscape
	#u = UrbanScape(20,10000,profit_probability_create_rule,'random')
	u = UrbanScape(n, ceiling, create_rule, distribution, randomize)
	
	externality_quintiles = np.array(([],[],[],[],[]))
	
	for i in range(steps):
		u.step()
		income_distribution = set()
		for uu in u.income:
			for ii in uu:
				income_distribution.add(ii)
		
		idist_sorted = sorted(income_distribution)
		num = len(idist_sorted)
		quintile_cutoffs = sorted([int((float(num)/float(5))*i - 1) for i in range(1,6)])
		
		incomes_q1 = [idist_sorted[i] for i in range(0,quintile_cutoffs[0])]
		incomes_q2 = [idist_sorted[i] for i in range(quintile_cutoffs[0],quintile_cutoffs[1])]
		incomes_q3 = [idist_sorted[i] for i in range(quintile_cutoffs[1],quintile_cutoffs[2])]
		incomes_q4 = [idist_sorted[i] for i in range(quintile_cutoffs[2],quintile_cutoffs[3])]
		incomes_q5 = [idist_sorted[i] for i in range(quintile_cutoffs[3],quintile_cutoffs[4])]
		
		externalities_q1 = []
		externalities_q2 = []
		externalities_q3 = []
		externalities_q4 = []
		externalities_q5 = []
		
		for i in range(n):
			for j in range(n):
				
				if u.income[i,j] in incomes_q1:
					externalities_q1.append(u.externalities[i,j])
				elif u.income[i,j] in incomes_q2:
					externalities_q2.append(u.externalities[i,j])
				elif u.income[i,j] in incomes_q3:
					externalities_q3.append(u.externalities[i,j])
				elif u.income[i,j] in incomes_q4:
					externalities_q4.append(u.externalities[i,j])
				elif u.income[i,j] in incomes_q5:
					externalities_q5.append(u.externalities[i,j])
					
		avg_ext_q1 = sum(externalities_q1)/len(externalities_q1)
		avg_ext_q2 = sum(externalities_q2)/len(externalities_q2)
		avg_ext_q3 = sum(externalities_q3)/len(externalities_q3)
		avg_ext_q4 = sum(externalities_q4)/len(externalities_q4)
		avg_ext_q5 = sum(externalities_q5)/len(externalities_q5)
		
		externality_quintiles = np.append(externality_quintiles, [[avg_ext_q1],[avg_ext_q2],[avg_ext_q3],[avg_ext_q4],[avg_ext_q5]],axis=1)
	
	terminal_mobility_dist = np.ones_like(u.mobility) * u.mobility
	terminal_income_dist = np.ones_like(u.income) * u.income
			
	return externality_quintiles, terminal_mobility_dist, terminal_income_dist, u.agent_coords

def run_batch_experiments(batches, grid_size, rent_ceiling, create_rule, distribution, randomize=True, steps = 100):
	batches = batches
	total_externalities = np.zeros((5,steps))
	total_terminal_mobility = np.zeros((grid_size,grid_size))
	total_terminal_income = np.zeros((grid_size,grid_size))
	total_ffagent_locations = np.zeros((grid_size,grid_size))
	total_gsagent_locations = np.zeros((grid_size,grid_size))
	
	for i in range(batches):
		experiment = run_experiment(grid_size, rent_ceiling, create_rule, distribution, randomize, steps)
		total_externalities += experiment[0]
		total_terminal_mobility += experiment[1]
		total_terminal_income += experiment[2]
		agent_coords = experiment[3]
		
		ffagent_locations = np.zeros((grid_size,grid_size))
		gsagent_locations = np.zeros((grid_size,grid_size))
		
		for agent, loc in agent_coords.items():
		        string = str(agent)
		        x,y = loc
		            
		        if 'FastFoodAgent' in string:
		            ffagent_locations[x,y] = 1
		                
		        if 'GroceryStoreAgent' in string:
		            gsagent_locations[x,y] = 1
		
		total_ffagent_locations += ffagent_locations
		total_gsagent_locations += gsagent_locations
		
	avg_externalities = total_externalities/batches
	avg_terminal_mobility = total_terminal_mobility/batches
	avg_terminal_income = total_terminal_income/batches
	avg_ffagent_locations = total_ffagent_locations/batches
	avg_gsagent_locations = total_gsagent_locations/batches
	
	ax1 = pyplot.subplot(321)
	pyplot.plot(avg_externalities[0], color = 'm', label = 'low-income',linewidth=2.0)
	pyplot.plot(avg_externalities[1], color = 'r', label = 'low-middle income',linewidth=2.0)
	pyplot.plot(avg_externalities[2], color = 'y', label = 'middle income',linewidth=2.0)
	pyplot.plot(avg_externalities[3], color = 'g', label = 'middle-high income',linewidth=2.0)
	pyplot.plot(avg_externalities[4], color = 'b', label = 'high income',linewidth=2.0)
	pyplot.legend(bbox_to_anchor=(1.05, 1), loc=2, prop={'size':7}, borderaxespad=0.)

	pyplot.xlabel('time',fontsize=10,fontname='serif')
	pyplot.ylabel('total exposure',fontsize=10,fontname='serif')
	pyplot.title('Accumulation of Negative Externalities',fontsize=10,fontname='serif')
	
	ax2 = pyplot.subplot(323)
	pyplot.imshow(avg_terminal_income, interpolation='nearest')
	pyplot.title('Terminal Income Distribution',fontsize=10,fontname='serif')
	
	ax3 = pyplot.subplot(324)
	pyplot.imshow(avg_terminal_mobility, cmap = 'Purples', interpolation='nearest')
	pyplot.title('Terminal Mobility Distribution',fontsize=10,fontname='serif')
	
	ax4 = pyplot.subplot(325)
	pyplot.imshow(avg_ffagent_locations, cmap = 'Reds', interpolation='nearest')
	pyplot.title('Fast Food Agent Locations',fontsize=10,fontname='serif')
	
	ax5 = pyplot.subplot(326)
	pyplot.imshow(avg_gsagent_locations, cmap = 'Greens', interpolation='nearest')
	pyplot.title('Grocery Store Agent Locations',fontsize=10,fontname='serif')
	
	ax1.tick_params(axis='x',labelsize=9)
        ax1.tick_params(axis='y',labelsize=9)
	ax2.tick_params(axis='x',labelsize=9)
        ax2.tick_params(axis='y',labelsize=9)
        ax3.tick_params(axis='x',labelsize=9)
        ax3.tick_params(axis='y',labelsize=9)
        ax4.tick_params(axis='x',labelsize=9)
        ax4.tick_params(axis='y',labelsize=9)
        ax5.tick_params(axis='x',labelsize=9)
        ax5.tick_params(axis='y',labelsize=9)
	
	pyplot.show()
	
def plot_experiment(externality_quintiles, urbanscape):
	pyplot.subplot(221)
	pyplot.plot(externality_quintiles[0], color = 'm', label = 'low-income',linewidth=2.0)
	pyplot.plot(externality_quintiles[1], color = 'r', label = 'low-middle income',linewidth=2.0)
	pyplot.plot(externality_quintiles[2], color = 'y', label = 'middle income',linewidth=2.0)
	pyplot.plot(externality_quintiles[3], color = 'g', label = 'middle-high income',linewidth=2.0)
	pyplot.plot(externality_quintiles[4], color = 'b', label = 'high income',linewidth=2.0)
	pyplot.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

	pyplot.xlabel('time')
	pyplot.ylabel('total exposure')
	pyplot.title('Accumulation of Negative Externalities')
	
	pyplot.subplot(223)
	pyplot.imshow(urbanscape.income, interpolation='nearest')
	pyplot.title('Income Distribution')
	
	pyplot.subplot(224)
	pyplot.imshow(urbanscape.agent_locations, cmap = 'YlOrRd', interpolation='nearest')
	pyplot.title('Fast Food Locations')
	pyplot.show()
	
	
#EXPERIMENTS TO RUN ON SHELL	

#u = UrbanScape(5, 100000,no_create_rule,'vertical', randomize = False)

#u = UrbanScape(20,200000,profit_probability_create_rule,'random')
#u = UrbanScape(20,200000,profit_probability_create_rule,'BDquadrants')
#u = UrbanScape(20,200000,profit_probability_create_rule,'CBD')

#run_experiment(20,250000,profit_probability_create_rule,'random',steps=10)
#run_experiment(20,250000,profit_probability_create_rule,'BDquadrants',steps=10)
#run_experiment(20,250000,profit_probability_create_rule,'CBD',steps=100)

#run_batch_experiments(3,20,200000,random_create_rule,'random',steps=50)
#run_batch_experiments(3,20,200000,profit_probability_create_rule,'random',steps=50)
#run_batch_experiments(3,20,200000,profit_probability_create_rule,'CBD',steps=200)

#run_batch_experiments(50,20,250000,profit_probability_create_rule,'random',steps=200)
#run_batch_experiments(50,20,250000,profit_probability_create_rule,'vertical',steps=200)
#run_batch_experiments(50,20,250000,profit_probability_create_rule,'CBD',steps=200)
