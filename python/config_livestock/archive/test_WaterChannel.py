import cmf
from datetime import datetime,timedelta
from matplotlib.pylab import plot, show
p=cmf.project()
# Create a triangular reach crosssection for 10 m long reaches with a bankslope of 2
shape = cmf.TriangularReach(10.,2.)
# Create a 1km river with 100 reaches along the x axis and a constant slope of 1%
reaches = [p.NewReach(i,0,i*.01,shape,False) for i in range(0,1000,10)]

for r_lower, r_upper in zip(reaches[:-1],reaches[1:]):
    r_upper.set_downstream(r_lower)

# Create a solver
solver = cmf.CVodeIntegrator(p,1e-9)
# Initial condition: 10 cmf of water in the most upper reach
reaches[-1].depth=0.1

# We store the results in this list
depth = [[r.depth for r in reaches]]
# Run the model for 3 h with dt=1 min
for t in solver.run(datetime(2012,1,1),datetime(2012,1,1,3), timedelta(minutes=1)):
    depth.append([r.depth for r in reaches])
    print(t)

# Plot the result (matplotlib needs to be installed)
plot(depth)
show()