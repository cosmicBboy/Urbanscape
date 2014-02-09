import sys
sys.path.insert(0, '/Users/Niels/Desktop')
import urbanscape
from urbanscape import profit_probability_create_rule
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

fig = pyplot.figure()

def urban():
    u = urbanscape.UrbanScape(20,200000,profit_probability_create_rule,'random')
    return u

u = urban()

im = pyplot.imshow(u.capture_number,cmap = 'YlOrRd',interpolation = 'nearest')

def updatefig(*args):
    global u
    u.step()
    im.set_array(u.capture_number)
    im.autoscale()
    return im,
    
ani = animation.FuncAnimation(fig,updatefig,frames=500,interval=1)

#ani.save('urbanscape_movie.mp4')

pyplot.show()