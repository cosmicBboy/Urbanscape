'''
Module defining create rules for plotting 
'''
import matplotlib.pyplot as pyplot

def plot_urbanscape(urbanscape):
	fig = pyplot.figure()
	
	pyplot.clf()
	pyplot.subplot(221)
	ii = urbanscape.income
	pyplot.imshow(ii, interpolation='nearest')
	pyplot.title("Income Distribution")
	
	pyplot.subplot(222)
	ff = urbanscape.ffexposure
	pyplot.imshow(ff, cmap = 'YlOrRd', interpolation='nearest')
	pyplot.title("FFR Effect Radii")
	
	pyplot.subplot(223)
	mm = urbanscape.externalities
	pyplot.imshow(mm, cmap = 'Purples', interpolation='nearest')
	pyplot.title("Externalities")
	
	pyplot.subplot(224)
	ll = urbanscape.agent_locations
	pyplot.imshow(ll, cmap = 'RdYlGn', interpolation='nearest',vmin=-1,vmax=1)
	pyplot.title("Food Agent Locations")
	
	return fig
