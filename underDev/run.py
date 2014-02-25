'''
Script for running experiments
'''

import urbanscape as us

def run_experiment(grid_size, rent_ceiling, create_rule, distribution, steps = 100):
	
	n = grid_size
	ceiling = rent_ceiling
	create_rule = create_rule
	steps = steps
	
	#defining the urbanscape
	#u = UrbanScape(20,10000,profit_probability_create_rule,'random')
	u = us.UrbanScape(n,ceiling,create_rule,distribution)
	
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

def run_batch_experiments(batches, grid_size, rent_ceiling, create_rule, distribution, steps = 100):
	batches = batches
	total_externalities = np.zeros((5,steps))
	total_terminal_mobility = np.zeros((grid_size,grid_size))
	total_terminal_income = np.zeros((grid_size,grid_size))
	total_ffagent_locations = np.zeros((grid_size,grid_size))
	total_gsagent_locations = np.zeros((grid_size,grid_size))
	
	for i in range(batches):
		experiment = run_experiment(grid_size, rent_ceiling, create_rule, distribution, steps)
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