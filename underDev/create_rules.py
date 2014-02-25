'''
Module defining create rules for Agents within the UrbanScape
'''
import numpy.random as random
import agent

def no_create_rule(urbanscape):
	pass

#creates FastFoodAgents randomly on the grid
def random_create_rule(urbanscape):
	x = random.randint(0,urbanscape.size)
	y = random.randint(0,urbanscape.size)
	urbanscape.add_agent(agent.FastFoodAgent((x,y),urbanscape))

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
		ff_cn = urbanscape.ffexposure
		gs_cn = urbanscape.gsexposure
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