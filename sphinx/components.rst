Livestock Grasshopper Components
================================

0 | Miscellaneous
-----------------

**Livestock Python Executor**

:Description: | Path to python executor.

:Inputs:
    :0.:    :Name: PythonPath
            :Description: Path to python.exe
            :Data Access: Item
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: BoundaryCondition
            :Description: | Livestock Boundary Conditions.

**Livestock SSH Connection**

:Description: | Setup SSH connection.
              | Icon based on art from Arthur Shlain from the Noun Project.
:Inputs:
    :0.:    :Name: IP
            :Description: IP Address for SSH connection.
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: Port
            :Description: Port for SSH connection.
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: Username
            :Description: Username for SSH connection.
            :Data Access: Item
            :Default Value: | None

    :3.:    :Name: Password
            :Description: Password for SSH connection.
            :Data Access: Item
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

1 | Geometry
------------

**Livestock Load Mesh**

:Description: Loads a mesh.

:Inputs:
    :0.:    :Name: Filename
            :Description: Directory and file name of mesh.
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: Load
            :Description: Activates the component.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Mesh
            :Description: | Loaded mesh.

    :2.:    :Name: MeshData
            :Description: | Additional data if any.

**Livestock Save Mesh**

:Description: Saves a mesh and additional data

:Inputs:
    :0.:    :Name: Mesh
            :Description: Mesh to save.
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: Data
            :Description: Additional data if any.
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: Directory
            :Description: File path to save mesh to.
            :Data Access: Item
            :Default Value: | None

    :3.:    :Name: Filename
            :Description: File name.
            :Data Access: Item
            :Default Value: | None

    :4.:    :Name: Save
            :Description: Activates the component.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

2 | CMF
-------

**Livestock CMF Ground**

:Description: | Generates CMF ground.
              | Icon art based created by Ben Davis from the Noun Project.

:Inputs:
    :0.:    :Name: Layers
            :Description: Soil layers to add to the mesh in m.
            :Data Access: List
            :Default Value: | 0

    :1.:    :Name: RetentionCurve
            :Description: Livestock CMF Retention Curve.
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: VegetationProperties
            :Description: Input from Livestock CMF Vegetation Properties.
            :Data Access: Item
            :Default Value: | None

    :3.:    :Name: SaturatedDepth
            :Description: Initial saturated depth in m. It is depth where the groundwater is located. Default is set
                          to 3m.
            :Data Access: Item
            :Default Value: | 3

    :4.:    :Name: SurfaceWaterVolume
            :Description: Initial surface water volume in m\ :sup:`3`. Default is set to 0 m\ :sup:`3`.
            :Data Access: Item
            :Default Value: | 0

    :5.:    :Name: FaceIndices
            :Description: List of face indices, on where the ground properties are applied.
            :Data Access: List
            :Default Value: | None

    :6.:    :Name: ETMethod
            :Description: | Set method to calculate evapotranspiration.
                          | 0: No evapotranspiration.
                          | 1: Penman-Monteith.
                          | 2: Shuttleworth-Wallace.
                          | Default is set to no evapotranspiration.
            :Data Access: Item
            :Default Value: | 0

    :7.:    :Name: Manning
            :Description: Set Manning roughness. If not set CMF calculates it from the above given values.
            :Data Access: Item
            :Default Value: | None

    :8.:    :Name: PuddleDepth
            :Description: Set puddle depth. Puddle depth is the height were run-off begins.
            :Data Access: Item
            :Default Value: | 0.01

    :9.:    :Name: SurfaceRunOffMethod
            :Description: | Set the method for computing the surface run-off.
                          | 0: Kinematic Wave.
                          | 1: Diffusive Wave.
                          | Default is set 0 - Kinematic Wave.
            :Data Access: Item
            :Default Value: | 0


:Outputs:
    :0.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :1.:    :Name: Ground
            :Description: Livestock Ground Data Class.

**Livestock CMF Weather**

:Description: | Generates CMF weather.
              | Icon art based created by Adrien Coquet from the Noun Project.

:Inputs:
    :0.:    :Name: Temperature
            :Description: Temperature in C. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :1.:    :Name: WindSpeed
            :Description: Wind speed in m/s. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :2.:    :Name: RelativeHumidity
            :Description: Relative humidity in %. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :3.:    :Name: CloudCover
            :Description: Cloud cover, unitless between 0 and 1. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :4.:    :Name: GlobalRadiation
            :Description: Global Radiation in W/m\:sup:`2`\. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :5.:    :Name: Rain
            :Description: Horizontal precipitation in mm/h. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :6.:    :Name: GroundTemperature
            :Description: Ground temperature in C. Either a list or a tree where the number of branches is equal to the number
                          of mesh faces.
            :Data Access: Tree
            :Default Value: | None

    :7.:    :Name: Location
            :Description: A Ladybug Tools Locations.
            :Data Access: Item
            :Default Value: | None

    :8.:    :Name: MeshFaceCount
            :Description: Number of faces in the ground mesh.
            :Data Access: Item
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Weather
            :Description: | Livestock Weather Data Class.


**Livestock CMF Vegetation Properties**

:Description: | Generates CMF Vegetation Properties
              | Icon art based created by Ben Davis from the Noun Project.

:Inputs:
    :0.:    :Name: Property
            :Description: 0-1 grasses. 2-6 soils. Default is set to 0
            :Data Access: Item
            :Default Value: | 0

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Units
            :Description: | Shows the units of the surface values.

    :2.:    :Name: VegetationValues
            :Description: | Chosen vegetation property values.

    :3.:    :Name: VegetationProperties
            :Description: | Livestock Vegetation Property Data.

**Livestock CMF Synthetic Tree**

:Description: | Generates a synthetic tree

:Inputs:
    :0.:    :Name: FaceIndex
            :Description: Mesh face index where tree is placed
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: TreeType
            :Description: Tree types: 0 - Deciduous. Default is deciduous.
            :Data Access: Item
            :Default Value: | 0

    :2.:    :Name: Height
            :Description: Height of tree in meters. Default is set to 10m
            :Data Access: Item
            :Default Value: | 10

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Units
            :Description: | Shows the units of the tree values.

    :2.:    :Name: TreeValues
            :Description: | Chosen tree properties values.

    :3.:    :Name: TreeProperties
            :Description: | Livestock tree properties data.

**Livestock CMF Retention Curve**

:Description: Generates a CMF retention curve.

:Inputs:
    :0.:    :Name: SoilIndex
            :Description: Index for choosing soil type. Index from 0-5. Default is set to 0, which is the default CMF
                          retention curve.
            :Data Access: Item
            :Default Value: | 0

    :1.:    :Name: K_sat
            :Description: Saturated conductivity in m/day.
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: Phi
            :Description: Porosity in m3/m3.
            :Data Access: Item
            :Default Value: | None

    :3.:    :Name: Alpha
            :Description: Inverse of water entry potential in 1/cm.
            :Data Access: Item
            :Default Value: | 0

    :4.:    :Name: N
            :Description: Pore size distribution parameter is unitless.
            :Data Access: Item
            :Default Value: | None

    :5.:    :Name: M
            :Description: VanGenuchten m (if negative, 1-1/n is used) is unitless.
            :Data Access: Item
            :Default Value: | None

    :6.:    :Name: L
            :Description: Mualem tortoisivity is unitless.
            :Data Access: Item
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Units
            :Description: | Shows the units of the curve values.

    :2.:    :Name: CurveValues
            :Description: | Chosen curve properties values.

    :3.:    :Name: RetentionCurve
            :Description: | Livestock Retention Curve.

**Livestock CMF Solve**

:Description: | Solves CMF Case.
              | Icon art based on Vectors Market from the Noun Project.
:Inputs:
    :0.:    :Name: Mesh
            :Description: Topography as a mesh.
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: Ground
            :Description: Input from Livestock CMF Ground.
            :Data Access: List
            :Default Value: | None

    :2.:    :Name: Weather
            :Description: Input from Livestock CMF Weather.
            :Data Access: Item
            :Default Value: | None

    :3.:    :Name: Trees
            :Description: Input from Livestock CMF Tree.
            :Data Access: List
            :Default Value: | None

    :4.:    :Name: Stream
            :Description: Input from Livestock CMF Stream. **Currently not working.**
            :Data Access: Item
            :Default Value: | None

    :5.:    :Name: BoundaryConditions
            :Description: Input from Livestock CMF Boundary Condition.
            :Data Access: List
            :Default Value: | None

    :6.:    :Name: SolverSettings
            :Description: Input from Livestock CMF Solver Settings.
            :Data Access: Item
            :Default Value: | None

    :7.:    :Name: Folder
            :Description: Path to folder. Default is Desktop.
            :Data Access: Item
            :Default Value: | os.path.join(os.environ["HOMEPATH"], "Desktop")}

    :8.:    :Name: CaseName
            :Description: Case name as string. Default is CMF
            :Data Access: Item
            :Default Value: | CMF

    :9.:   :Name: Outputs
            :Description: Connect Livestock Outputs.
            :Data Access: Item
            :Default Value: | None

    :10.:   :Name: Write
            :Description: Boolean to write files.
            :Data Access: Item
            :Default Value: | False

    :11.:   :Name: Overwrite
            :Description: If True excising case will be overwritten. Default is set to True.
            :Data Access: Item
            :Default Value: | True

    :12.:   :Name: Run
            :Description: | Boolean to run analysis.
                          | Analysis will be ran through SSH. Configure the connection with Livestock SSH.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: ResultPath
            :Description: | Path to result files.

**Livestock CMF Results**

:Description: | CMF Results

:Inputs:
    :0.:    :Name: ResultFolder
            :Description: Path to result file. Accepts output from Livestock Solve.
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: FetchResult
            :Description: | Choose which result should be loaded:
                          | 0 - Evapotranspiration
                          | 1 - Surface water volume
                          | 2 - Surface water flux
                          | 3 - Heat flux
                          | 4 - Aerodynamic resistance
                          | 5 - Soil layer water flux
                          | 6 - Soil layer potential
                          | 7 - Soil layer theta
                          | 8 - Soil layer volume
                          | 9 - Soil layer wetness
                          | Default is set to 0.
            :Data Access: Item
            :Default Value: | 0

    :2.:    :Name: SaveCSV
            :Description: Save the values as a csv file - Default is set to False.
            :Data Access: Item
            :Default Value: | False

    :3.:    :Name: Run
            :Description: Run component.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Units
            :Description: | Shows the units of the results.

    :2.:    :Name: Values
            :Description: | List with chosen result values.

    :3.:    :Name: CSVPath
            :Description: | Path to csv file.

**Livestock CMF Outputs**

:Description: Specify the wanted outputs from the CMF simulation.

:Inputs:
    :0.:    :Name: Evapotranspiration
            :Description: Cell evaporation - default is set to True.
            :Data Access: Item
            :Default Value: | True

    :1.:    :Name: SurfaceWaterVolume
            :Description: Cell surface water - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :2.:    :Name: SurfaceWaterFlux
            :Description: Cell surface water flux - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :3.:    :Name: HeatFlux
            :Description: Cell surface heat flux - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :4.:    :Name: AerodynamicResistance
            :Description: Cell surface water - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :5.:    :Name: VolumetricFlux
            :Description: Soil layer volumetric flux vectors - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :6.:    :Name: Potential
            :Description: Soil layer total potential (Psi\ :sub:`tot`\ = Psi\ :sub:`M`\ + Psi\ :sub:`G`\
                          - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :7.:    :Name: Theta
            :Description: Soil layer volumetric water content of the layer - default is set to False.
            :Data Access: Item
            :Default Value: | False

    :8.:    :Name: Volume
            :Description: Soil layer volume of water in the layer - default is set to True.
            :Data Access: Item
            :Default Value: | True

    :9.:    :Name: Wetness
            :Description: Soil layer wetness of the soil (V\ :sub:`volume`\/V\ :sub:`pores`\) - default is set to False.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: ChosenOutputs
            :Description: | Shows the chosen outputs.

    :2.:    :Name: Outputs
            :Description: | Livestock Output Data.

**Livestock CMF Boundary Condition**

:Description: CMF Boundary connection

:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: | 0

    :2.:    :Name: ConnectedCell
            :Description: Cell to connect to. Default is set to first cell.
            :Data Access: Item
            :Default Value: | 0

    :3.:    :Name: ConnectedLayer
            :Description: Layer of cell to connect to. 0 is surface water. 1 is first layer of cell and so on.
                          Default is set to 0 - surface water.
            :Data Access: Item
            :Default Value: | 0

    :4.:    :Name: InletFlux
            :Description: If inlet, then set flux in m3/day.
            :Data Access: List
            :Default Value: | False

    :5.:    :Name: FlowWidth
            :Description: Width of the connection from cell to outlet in meters.
            :Data Access: Item
            :Default Value: | None

    :6.:    :Name: OutletLocation
            :Description: Location of the outlet in x, y and z coordinates.
            :Data Access: List
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: BoundaryCondition
            :Description: | Livestock Boundary Conditions.

**Livestock CMF Solver Settings**

:Description: Sets the solver settings for CMF Solve

:Inputs:
    :0.:    :Name: AnalysisLength
            :Description: Total length of the simulation in hours - default is set to 24 hours.
            :Data Access: Item
            :Default Value: | 24

    :1.:    :Name: TimeStep
            :Description: | Size of each time step in hours - e.g. 1/60 equals time steps of 1 min and 24 is a time step of one day.
                          | Default is 1 hour.
            :Data Access: Item
            :Default Value: | 1

    :2.:    :Name: SolverTolerance
            :Description: Solver tolerance - Default is 1e-8
            :Data Access: Item
            :Default Value: | 10**-8

    :3.:    :Name: Verbosity
            :Description: | Sets the verbosity of the print statement during runtime - Default is 1.
                          | 0 - Prints only at start and end of simulation.
                          | 1 - Prints at every time step.
            :Data Access: Item
            :Default Value: | 1

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: SolverSettings
            :Description: | Livestock Solver Settings.


**Livestock CMF Surface Flux Result**

:Description: Extract the surface flux for a mesh.

:Inputs:
    :0.:    :Name: ResultFolder
            :Description: Path to result file. Accepts output from Livestock Solve
            :Data Access: Item
            :Default Value: | None

    :1.:    :Name: Mesh
            :Description: Mesh of the case
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: IncludeRunOff
            :Description: Include surface run-off into the surface flux vector? Default is set to True.
            :Data Access: Item
            :Default Value: | True

    :3.:    :Name: IncludeRain
            :Description: Include rain into the surface flux vector? Default is False.
            :Data Access: Item
            :Default Value: | False

    :4.:    :Name: IncludeEvapotranspiration
            :Description: Include evapotranspiration into the surface flux vector? Default is set to False.
            :Data Access: Item
            :Default Value: | False

    :5.:    :Name: IncludeInfiltration
            :Description: Include infiltration into the surface flux vector? Default is False.
            :Data Access: Item
            :Default Value: | False

    :6.:    :Name: SaveResult
            :Description: Save the values as a text file - Default is set to False.
            :Data Access: Item
            :Default Value: | False

    :7.:    :Name: Run
            :Description: Run component. Default is False.
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: Unit
            :Description: | Shows the units of the results.

    :2.:    :Name: SurfaceFluxVectors
            :Description: | Tree with the surface flux vectors.

    :3.:    :Name: CSVPath
            :Description: | Path to csv file.

**Livestock CMF Outlet**

:Description: Create a CMF Outlet.

:Inputs:
    :0.:    :Name: Location
            :Description: Location of the outlet in x, y and z coordinates. Default is 0,0,0.
            :Data Access: Item
            :Default Value: | [0, 0, 0]

    :1.:    :Name: ConnectedCell
            :Description: Cell to connect to. Default is set to first cell.
            :Data Access: Item
            :Default Value: | 0

    :2.:    :Name: ConnectedLayer
            :Description: | Layer of cell to connect to.
                          | 0 is surface water.
                          | 1 is first layer of cell and so on.
                          | Default is set to 0 - surface water
            :Data Access: Item
            :Default Value: | 0

    :3.:    :Name: OutletType
            :Description: | Set type of outlet connection.
                          | 1: Richards.
                          | 2: Kinematic wave.
                          | 3: Technical Flux.
            :Data Access: Item
            :Default Value: | None

    :4.:    :Name: ConnectionParameter
            :Description: | If Richards:
                          |    Potential - Sets the potential of the outlet. The difference in potential is what drives the flux.
                          | If Kinematic wave:
                          |    Residence Time - Linear flow parameter of travel time in days.
                          | If Technical Flux:
                          |    Maximum Flux - The maximum flux is in m\ :sup:`3`\/day.
            :Data Access: Item
            :Default Value: | None

:Outputs:
    :0.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :1.:    :Name: BoundaryCondition
            :Description: | Livestock Boundary Condition.

3 | Comfort
-----------

**Livestock New Air Conditions**

:Description: Computes new air temperature and relative humidity

:Inputs:
    :1.:    :Name: Mesh
            :Description: Ground Mesh
            :Data Access: Item
            :Default Value: | None

    :2.:    :Name: Evapotranspiration
            :Description: Evapotranspiration in m\ :sup:`3`\/day.
                          Each tree branch should represent one time unit, with all the cell values to that time.
            :Data Access: Tree
            :Default Value: | None

    :3.:    :Name: HeatFlux
            :Description: HeatFlux in MJ/m\ :sup:`2`\day.
                          Each tree branch should represent one time unit, with all the cell values to that time.
            :Data Access: Tree
            :Default Value: | None

    :4.:    :Name: AirTemperature
            :Description: Air temperature in C
            :Data Access: List
            :Default Value: | None

    :5.:    :Name: AirRelativeHumidity
            :Description: Relative Humidity in -
            :Data Access: List
            :Default Value: | None

    :6.:    :Name: AirBoundaryHeight
            :Description: Top of the air column in m. Default is set to 10m.
            :Data Access: Item
            :Default Value: | 10

    :7.:    :Name: InvestigationHeight
            :Description: Height at which the new air temperature and relative humidity should be calculated.
                          Default is set to 1.1m.
            :Data Access: Item
            :Default Value: | 1.1

    :8.:    :Name: CPUs
            :Description: Number of CPUs to perform the computations on. Default is set to 2
            :Data Access: Item
            :Default Value: | 2

    :9.:    :Name: ThroughSSH
            :Description: If the computation should be run through SSH. Default is set to False
            :Data Access: Item
            :Default Value: | False

    :10.:
            :Name: Run
            :Description: Run the component
            :Data Access: Item
            :Default Value: | False

:Outputs:
    :1.:    :Name: readMe!
            :Description: | In case of any errors, it will be shown here.

    :2.:    :Name: NewTemperature
            :Description: | New temperature in C.

    :3.:    :Name: NewRelativeHumidity
            :Description: | New relative humidity in -.


**Go Back to:**

`Livestock Frontpage`__

`Livestock PyPi`__

`Livestock Grasshopper`__

__ https://ocni-dtu.github.io/

__ https://ocni-dtu.github.io/livestock/index.html

__ https://ocni-dtu.github.io/livestock_gh/index.html