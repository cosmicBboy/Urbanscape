'''
Module defining update state for the UrbanScape class
'''

import numpy as np

#=============================
#  					  	 	 |
#  UrbanScape Agent Methods  |
#  						  	 |
#=============================

# Base class for all Food Agents
# agent has a location and wealth

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