import urbanscape as us
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation

ppcr = us.profit_probability_create_rule
rcr = us.random_create_rule


def animate_urbanscape(urbanscape):

    fig = pyplot.figure()
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    ax1.set_title('Income Distribution',fontname='serif',fontsize=10)
    ax2.set_title('Fast Food Exposure',fontsize=10)
    ax3.set_title('Externalities',fontsize=10)
    ax4.set_title('Food Agent Locations',fontsize=10)

    ax1.tick_params(axis='x',labelsize=9)
    ax1.tick_params(axis='y',labelsize=9)

    global u
    u = urbanscape

    im1 = ax1.imshow(u.income, interpolation = 'nearest')
    im2 = ax2.imshow(u.ffcapture_number, cmap = 'YlOrRd',interpolation = 'nearest')
    im3 = ax3.imshow(u.externalities, cmap = 'Purples',interpolation = 'nearest')
    im4 = ax4.imshow(u.agent_locations, cmap = 'RdYlGn',interpolation = 'nearest',vmin=-1,vmax=1)

    def updatefig(*args):
        u.step()
        im1.set_array(u.income)
        im2.set_array(u.ffcapture_number)
        im3.set_array(u.externalities)
        im4.set_array(u.agent_locations)

        im1.autoscale()
        im2.autoscale()
        im3.autoscale()
        
        return im1,im2,im3,im4
        
    ani = animation.FuncAnimation(fig,updatefig,frames=100,interval=1)

    pyplot.show()

#animator.animate_urbanscape(20, 100000, urbanscape.random_create_rule, "CBD", randomize=True)
#animator.animate_urbanscape(20, 100000, urbanscape.profit_probability_create_rule, "CBD", randomize=True)
