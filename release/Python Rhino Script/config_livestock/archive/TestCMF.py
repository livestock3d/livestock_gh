def first_simple_model():
    import cmf
    import datetime

    p = cmf.project()
    # Create W1 in project p
    W1 = p.NewStorage(name="W1",x=0,y=0,z=0)
    # Create W2 in project p without any volume as an initial state
    W2 = p.NewStorage(name="W2",x=10,y=0,z=0)
    # Create a linear storage equation from W1 to W2 with a residence time tr of one day
    q = cmf.kinematic_wave(source=W1,target=W2,residencetime=1.0)
    # Set the initial state of w1 to 1m³ of water.
    W1.volume = 1.0

    # Create Outlet
    Out = p.NewOutlet(name="Outlet",x=20,y=0,z=0)
    qout = cmf.kinematic_wave(source=W2,target=Out,residencetime=2.0)

    # Create a Neumann Boundary condition connected to W1
    In = cmf.NeumannBoundary.create(W1)
    # Create a timeseries with daily alternating values.
    In.flux = cmf.timeseries(begin = datetime.datetime(2012,1,1),
                             step = datetime.timedelta(days=1),
                             interpolationmethod = 0)
    for i in range(10):
        # Add 0.0 m3/day for even days, and 1.0 m3/day for odd days
        In.flux.add(i % 2)

    # Create an integrator for the ODE represented by project p, with an error tolerance of 1e-9
    solver = cmf.RKFIntegrator(p,1e-9)

    # Set the intitial time of the solver
    solver.t = datetime.datetime(2012,1,1)

    # Iterate the solver hourly through the time range and return for each time step the volume in W1 and W2
    result = [[W1.volume,W2.volume] for t in solver.run(datetime.datetime(2012,1,1),datetime.datetime(2012,1,7),datetime.timedelta(hours=1))]
    import pylab as plt
    plt.plot(result)
    plt.xlabel('hours')
    plt.ylabel('Volume in $m^3$')
    plt.legend(('W1','W2'))
    plt.show()

#first_simple_model()

#----------------------------------------------------------------------------------------------------------------------#

def simple1D():
    from matplotlib import pyplot as plt
    import cmf
    from datetime import datetime, timedelta

    project = cmf.project()

    # Add one cell at position (0,0,0), Area=1000m2
    cell = project.NewCell(0, 0, 0, 1000, with_surfacewater=True)

    # Create a retention curve
    r_curve = cmf.VanGenuchtenMualem(Ksat=1, phi=0.5, alpha=0.01, n=2.0)

    # Add ten layers of 10cm thickness
    for i in range(10):
        depth = (i + 1) * 0.1
        cell.add_layer(depth, r_curve)

    # Connect layers with Richards perc.
    # this can be shorten as
    cell.install_connection(cmf.Richards)

    # Create solver
    solver = cmf.CVodeIntegrator(project, 1e-6)
    solver.t = cmf.Time(1, 1, 2011)

    # Create groundwater boundary (uncomment to use it)
    # Create the boundary condition
    gw = project.NewOutlet('groundwater', x=0, y=0, z=-1.1)

    # Set the potential
    gw.potential = -2

    # Connect the lowest layer to the groundwater using Richards percolation
    gw_flux=cmf.Richards(cell.layers[-1],gw)


    # Set inital conditions
    # Set all layers to a potential of -2 m
    cell.saturated_depth = 2.

    # 100 mm water in the surface water storage
    cell.surfacewater.depth = 0.1

    # The run time loop, run for 72 hours
    # Save potential and soil moisture for each layer
    potential = [cell.layers.potential]
    moisture = [cell.layers.theta]

    for t in solver.run(solver.t, solver.t + timedelta(days=7), timedelta(hours=1)):
        potential.append(cell.layers.potential)
        moisture.append(cell.layers.theta)
    """
    # Plot results
    plt.subplot(211)
    plt.plot(moisture)
    plt.ylabel(r'Soil moisture $\theta [m^3/m^3]$')
    plt.xlabel(r'$time [h]$')
    plt.grid()
    plt.subplot(212)
    plt.plot(potential)
    plt.ylabel(r'Water head $\Psi_{tot} [m]$')
    plt.xlabel(r'$time [h]$')
    plt.grid()
    plt.show()
    """

    print(cell.vegetation)

#simple1D()

#----------------------------------------------------------------------------------------------------------------------#

def canopyStorage():
    import cmf
    import pylab as plt

    p = cmf.project()
    c = p.NewCell(0, 0, 0, 1000, True)
    # Add a single layer of 1 m depth
    l = c.add_layer(1.0, cmf.VanGenuchtenMualem())
    # Use GreenAmpt infiltration from surface water
    c.install_connection(cmf.GreenAmptInfiltration)
    # Add a groundwater boundary condition
    gw = p.NewOutlet('gw', 0, 0, -2)
    # Use a free drainage connection to the groundwater
    cmf.FreeDrainagePercolation(l, gw)

    # Add some rainfall
    c.set_rainfall(5.0)

    # Make c.canopy a water storage
    c.add_storage('Canopy', 'C')
    # Split the rainfall from the rain source (RS) between
    # intercepted rainfall (RS->canopy) and throughfall (RS-surface)
    cmf.Rainfall(c.canopy, c, False, True)  # RS->canopy, only intercepted rain
    cmf.Rainfall(c.surfacewater, c, True, False)  # RS->surface, only throughfall
    # Use an overflow mechanism, eg. the famous Rutter-Interception Model
    cmf.RutterInterception(c.canopy, c.surfacewater, c)
    # And now the evaporation from the wet canopy (using a classical Penman equation)
    cmf.CanopyStorageEvaporation(c.canopy, c.evaporation, c)

    solver = cmf.CVodeIntegrator(p, 1e-9)
    res = [l.volume for t in solver.run(solver.t, solver.t + cmf.day, cmf.min * 15)]

    plt.figure()
    plt.plot(res)
    plt.show()

#canopyStorage()


#----------------------------------------------------------------------------------------------------------------------#
import cmf
import numpy as np
from datetime import datetime,timedelta

# Create a project
project = cmf.project()
print('rain stations', project.rainfall_stations)

# Create a timeseries, starting Jan 1st, 2010 with 1h step, with random data
raindata = cmf.timeseries.from_array(datetime(2010,1,1), timedelta(hours=1), np.random.uniform(0,30,24*365))
# Add a rainfall station to the project
rainstation = project.rainfall_stations.add(Name='Random station',
                                            Data=raindata,
                                            Position=(0,0,0))

print('rain stations', project.rainfall_stations)