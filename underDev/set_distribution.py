'''
Module defining setter methods for the UrbanScape class
'''

import numpy as np

#=========================
#  					  	 |
#  Distribution Setters  |
#  					  	 |
#=========================

def random_distribution(UrbanScape):
	u = UrbanScape
	u.rent = np.random.randint(u.rent_floor, u.rent_ceiling,(u.size,u.size))

def vertical_distribution(UrbanScape):
	u = UrbanScape
	gradient = float(u.rent_ceiling - u.rent_floor) / (u.size - 1)
	g_multiplier = gradient / u.rent_ceiling
	fr_ratio = float(u.rent_floor) / u.rent_ceiling

	#loops through each row and modifies the rent by factor of gg
	for i in range(u.size):
		gg = fr_ratio + g_multiplier * i
		u.rent[i] = u.rent[i] * gg
			
def diagonal_distribution(UrbanScape):
	u = UrbanScape
	gradient = float(u.rent_ceiling - u.rent_floor) / (u.size - 1)
	g_multiplier = gradient / u.rent_ceiling
	fr_ratio = float(u.rent_floor) / u.rent_ceiling
	
	for i in range(u.size):
		gg = float(fr_ratio + g_multiplier*i)
		u.rent[i] = u.rent[i] * gg
	for j in range(u.size):
		gg = float(fr_ratio + g_multiplier*j)
		u.rent[:,j] = u.rent[:,j] * gg

#Functions for calculating rent based on distance from a business district block
def distance_rent_function(quadrant_coords, bd_coords):
    x_dist = float(quadrant_coords[0] - bd_coords[0])
    y_dist = float(quadrant_coords[1] - bd_coords[1])
    dist = np.sqrt(x_dist ** 2 + y_dist ** 2)
    return dist      

#block rent decays exponentially the further away it is from a business district
def exponential_rent_function(UrbanScape, distance, coord, dmax):
    u = UrbanScape
    i,j = coord
    Lambda = np.log(float(u.rent_floor)/float(u.rent_ceiling)) * (-1/dmax)
    rent_value = u.rent_ceiling * np.e**(-Lambda*distance)
    u.rent[i][j] = rent_value

#block rent decreases linearly the further away it is from a business district        
def linear_rent_function(UrbanScape, distance, coord, dmax):
	u = UrbanScape
	i,j = coord
	Alpha = (float(u.rent_floor) - float(u.rent_ceiling)) / dmax
	rent_value = u.rent_ceiling + (Alpha * distance)
	u.rent[i][j] = rent_value

#Functions for setting an income distribution based on 'business districts'
#---- The approximate center of each quadrant of the urbanscape is a 'business district'
#---- The assumption is that rent and income decreases the further away a block is.

def businessdistricts_quadrant_distribution(UrbanScape, gradient_function=exponential_rent_function):
	u = UrbanScape
	bisector = int(np.ceil(u.size * 0.5)) #finds the bisecting block value for UrbanScape
	lower_range = range(bisector) #lower range of block indices in UrbanScape
	upper_range = range(bisector, u.size) #upper range of block indices in UrbanScape

	district1 = [(i,j) for i in lower_range for j in lower_range]
	district2 = [(i,j) for i in upper_range for j in lower_range]
	district3 = [(i,j) for i in lower_range for j in upper_range]
	district4 = [(i,j) for i in upper_range for j in upper_range]

	d1_coords = (np.ceil(u.size * 0.25), np.ceil(u.size * 0.25))
	d2_coords = (np.ceil(u.size * 0.75), np.ceil(u.size * 0.25))
	d3_coords = (np.ceil(u.size * 0.25), np.ceil(u.size * 0.75))
	d4_coords = (np.ceil(u.size * 0.75), np.ceil(u.size * 0.75))

	d1_distances = [distance_rent_function(q, d1_coords) for q in district1]
	d2_distances = [distance_rent_function(q, d2_coords) for q in district2]
	d3_distances = [distance_rent_function(q, d3_coords) for q in district3]
	d4_distances = [distance_rent_function(q, d4_coords) for q in district4]

	dmax = max(d1_distances)

	#for i in range(len(district1)):
	for i in range( len(district1) ):
	    gradient_function(u, d1_distances[i], district1[i], dmax)
	    gradient_function(u, d2_distances[i], district2[i], dmax)
	    gradient_function(u, d3_distances[i], district3[i], dmax)
	    gradient_function(u, d4_distances[i], district4[i], dmax)

def centralbusinessdistrict_distribution(UrbanScape, gradient_function=exponential_rent_function):
	u = UrbanScape
	block_coords = [ (i,j) for i in range(u.size) for j in range(u.size) ]
	district_coords = (np.ceil(u.size * 0.5), np.ceil(u.size * 0.5))
	block_distances = [distance_rent_function(q, district_coords) for q in block_coords]
	dmax = max(block_distances)

	for i in range(len(block_coords)):
	    #u.linear_rent_function(block_distances[i], block_coords[i])
	    gradient_function(u, block_distances[i], block_coords[i], dmax)


#applies random variation to the rent values
def apply_variation(UrbanScape, var=0.25):
	u = UrbanScape
	rand_var = np.random.uniform( (1 - var), (1 + var), (u.size, u.size) )
	u.rent = u.rent * rand_var

if __name__ == '__main__':
	import urbanscape as us
	u = us.UrbanScape(4, 5000, 200000, setDist=random_distribution)
	print u.rent
	print u.income

