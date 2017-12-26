Livestock Grasshopper Components
================================

0 | Miscellaneous
-----------------

**Livestock Python Executor**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock SSH Connection**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.


1 | Geometry
------------

**Livestock Load Mesh**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock Save Mesh**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

3 | CMF
-------

**Livestock CMF Ground**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Weather**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Vegetation Properties**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Synthetic Tree**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Retention Curve**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Solve**

:Description: | Solves CMF Case.
              | Icon art based on Vectors Market from the Noun Project.
|
:Inputs:
    :1.:    :Name: Mesh
            :Description: Topography as a mesh.
            :Data Access: Item
            :Default Value: None

    :2.:    :Name: Ground
            :Description: Input from Livestock CMF Ground.
            :Data Access: List
            :Default Value: None

    :3.:    :Name: Weather
            :Description: Input from Livestock CMF Weather.
            :Data Access: Item
            :Default Value: None

    :4.:    :Name: Trees
            :Description: Input from Livestock CMF Tree.
            :Data Access: List
            :Default Value: None

    :5.:    :Name: Stream
            :Description: Input from Livestock CMF Stream. **Currently not working.**
            :Data Access: Item
            :Default Value: None

    :6.:    :Name: BoundaryConditions
            :Description: Input from Livestock CMF Boundary Condition.
            :Data Access: List
            :Default Value: None

    :7.:    :Name: SolverSettings
            :Description: Input from Livestock CMF Solver Settings.
            :Data Access: Item
            :Default Value: None

    :8.:    :Name: Folder
            :Description: Path to folder. Default is Desktop.
            :Data Access: Item
            :Default Value: os.path.join(os.environ["HOMEPATH"], "Desktop")}

    :9.:    :Name: CaseName
            :Description: Case name as string. Default is CMF
            :Data Access: Item
            :Default Value: CMF

    :10.:   :Name: Outputs
            :Description: Connect Livestock Outputs.
            :Data Access: Item
            :Default Value: None

    :11.:   :Name: Write
            :Description: Boolean to write files.
            :Data Access: Item
            :Default Value: False

    :12.:   :Name: Overwrite
            :Description: If True excising case will be overwritten. Default is set to True.
            :Data Access: Item
            :Default Value: True

    :13.:   :Name: Run
            :Description: | Boolean to run analysis.
                          | Analysis will be ran through SSH. Configure the connection with Livestock SSH.
            :Data Access: Item
            :Default Value: False
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: ResultPath
            :Description: Path to result files.

**Livestock CMF Results**

:Description: CMF Results
|
:Inputs:
    :1.:    :Name: ResultFilePath
            :Description: Path to result file. Accepts output from Livestock Solve
            :Data Access: Item
            :Default Value: None

    :2.:    :Name: FetchResult
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
            :Default Value: 0

    :3.:    :Name: SaveCSV
            :Description: Save the values as a csv file - Default is set to False.
            :Data Access: Item
            :Default Value: False

    :4.:    :Name: Run
            :Description: Run component.
            :Data Access: Item
            :Default Value: False
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: Units
            :Description: Shows the units of the results.

    :3.:    :Name: Values
            :Description: List with chosen result values.

    :4.:    :Name: CSVPath
            :Description: Path to csv file.

**Livestock CMF Outputs**

:Description: CMF Outputs
|
:Inputs:
    :1.:    :Name: Evapotranspiration
            :Description: Cell evaporation - default is set to True.
            :Data Access: Item
            :Default Value: True

    :2.:    :Name: SurfaceWaterVolume
            :Description: Cell surface water - default is set to False.
            :Data Access: Item
            :Default Value: False

    :3.:    :Name: SurfaceWaterFlux
            :Description: Cell surface water flux - default is set to False.
            :Data Access: Item
            :Default Value: False

    :4.:    :Name: HeatFlux
            :Description: Cell surface heat flux - default is set to False.
            :Data Access: Item
            :Default Value: False

    :5.:    :Name: AerodynamicResistance
            :Description: Cell surface water - default is set to False.
            :Data Access: Item
            :Default Value: False

    :6.:    :Name: SurfaceWaterFlux
            :Description: Soil layer volumetric flux vectors - default is set to False.
            :Data Access: Item
            :Default Value: False

    :7.:    :Name: VolumetricFlux
            :Description: Soil layer volumetric flux vectors - default is set to False.
            :Data Access: Item
            :Default Value: False

    :8.:    :Name: Potential
            :Description: Soil layer total potential (Psi\ :sub:`tot`\ = Psi\ :sub:`M`\ + Psi\ :sub:`G`\
                          - default is set to False.
            :Data Access: Item
            :Default Value: False

    :9.:    :Name: Theta
            :Description: Soil layer volumetric water content of the layer - default is set to False.
            :Data Access: Item
            :Default Value: False

    :10.:    :Name: Volume
            :Description: Soil layer volume of water in the layer - default is set to True.
            :Data Access: Item
            :Default Value: True

    :10.:    :Name: Wetness
            :Description: Soil layer wetness of the soil (V\ :sub:`volume`\/V\ :sub:`pores`\) - default is set to False.
            :Data Access: Item
            :Default Value: False
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: ChosenOutputs
            :Description: Shows the chosen outputs.

    :3.:    :Name: Outputs
            :Description: Livestock Output Data.

**Livestock CMF Boundary Condition**

:Description: CMF Boundary connection
|
:Inputs:
    :1.:    :Name: InletOrOutlet
            :Description: 0 is inlet. 1 is outlet - default is set to 0
            :Data Access: Item
            :Default Value: 0

    :2.:    :Name: ConnectedCell
            :Description: Cell to connect to. Default is set to first cell.
            :Data Access: Item
            :Default Value: 0

    :3.:    :Name: ConnectedLayer
            :Description: Layer of cell to connect to. 0 is surface water. 1 is first layer of cell and so on.
                          Default is set to 0 - surface water.
            :Data Access: Item
            :Default Value: 0

    :4.:    :Name: InletFlux
            :Description: If inlet, then set flux in m3/day.
            :Data Access: List
            :Default Value: False

    :5.:    :Name: FlowWidth
            :Description: Width of the connection from cell to outlet in meters.
            :Data Access: Item
            :Default Value: None

    :6.:    :Name: OutletLocation
            :Description: Location of the outlet in x, y and z coordinates.
            :Data Access: List
            :Default Value: None
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: BoundaryCondition
            :Description: Livestock Boundary Conditions.

**Livestock CMF Solver Settings**

:Description: Sets the solver settings for CMF Solve
|
:Inputs:
    :1.:    :Name: AnalysisLength
            :Description: Number of time steps to be taken - Default is 24
            :Data Access: Item
            :Default Value: 24

    :2.:    :Name: TimeStep
            :Description: Size of each time step in hours - e.g. 1/60 equals time steps of 1 min and 24 is a time step
                          of one day. Default is 1 hour.
            :Data Access: Item
            :Default Value: 1

    :3.:    :Name: SolverTolerance
            :Description: Solver tolerance - Default is 1e-8
            :Data Access: Item
            :Default Value: 10**-8

    :4.:    :Name: Verbosity
            :Description: | Sets the verbosity of the print statement during runtime - Default is 1.
                          | 0 - Prints only at start and end of simulation.
                          | 1 - Prints at every time step.
            :Data Access: Item
            :Default Value: 10**-8
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :1.:    :Name: SolverSettings
            :Description: Livestock Solver Settings.


**Livestock CMF Surface Flux Result**

:Description:
|
:Inputs:
    :1.:    :Name: ResultFilePath
            :Description: Path to result file. Accepts output from Livestock Solve
            :Data Access: Item
            :Default Value: None

    :2.:    :Name: Mesh
            :Description: Mesh of the case
            :Data Access: Item
            :Default Value: None

    :3.:    :Name: IncludeRunOff
            :Description: Include surface run-off into the surface flux vector? Default is set to True.
            :Data Access: Item
            :Default Value: True

    :4.:    :Name: IncludeRain
            :Description: Include rain into the surface flux vector? Default is False.
            :Data Access: Item
            :Default Value: False

    :5.:    :Name: IncludeEvapotranspiration
            :Description: Include evapotranspiration into the surface flux vector? Default is set to False.
            :Data Access: Item
            :Default Value: False

    :6.:    :Name: IncludeInfiltration
            :Description: Include infiltration into the surface flux vector? Default is False.
            :Data Access: Item
            :Default Value: False

    :7.:    :Name: SaveResult
            :Description: Save the values as a text file - Default is set to False.
            :Data Access: Item
            :Default Value: False

    :8.:    :Name: Run
            :Description: Run component. Default is False.
            :Data Access: Item
            :Default Value: False
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: Unit
            :Description: Shows the units of the results.

    :3.:    :Name: SurfaceFluxVectors
            :Description: Tree with the surface flux vectors.

    :4.:    :Name: CSVPath
            :Description: Path to csv file.

4 | Comfort
-----------

**Livestock New Air Conditions**

:Description:

|
:Inputs:
    :1.:    :Name: Mesh
            :Description: Ground Mesh
            :Data Access: Item
            :Default Value: None

    :2.:    :Name: Evapotranspiration
            :Description: Evapotranspiration in m\ :sup:`3`\/day.
                          Each tree branch should represent one time unit, with all the cell values to that time.
            :Data Access: Tree
            :Default Value: None

    :3.:    :Name: HeatFlux
            :Description: HeatFlux in MJ/m\ :sup:`2`\day.
                          Each tree branch should represent one time unit, with all the cell values to that time.
            :Data Access: Tree
            :Default Value: None

    :4.:    :Name: AirTemperature
            :Description: Air temperature in C
            :Data Access: List
            :Default Value: None

    :5.:    :Name: AirRelativeHumidity
            :Description: Relative Humidity in -
            :Data Access: List
            :Default Value: None

    :6.:    :Name: AirBoundaryHeight
            :Description: Top of the air column in m. Default is set to 10m.
            :Data Access: Item
            :Default Value: 10

    :7.:    :Name: InvestigationHeight
            :Description: Height at which the new air temperature and relative humidity should be calculated.
                          Default is set to 1.1m.
            :Data Access: Item
            :Default Value: 1.1

    :8.:    :Name: CPUs
            :Description: Number of CPUs to perform the computations on. Default is set to 2
            :Data Access: Item
            :Default Value: 2

    :9.:    :Name: ThroughSSH
            :Description: If the computation should be run through SSH. Default is set to False
            :Data Access: Item
            :Default Value: False

    :10.:
            :Name: Run
            :Description: Run the component
            :Data Access: Item
            :Default Value: False
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: NewTemperature
            :Description: New temperature in C.

    :3.:    :Name: NewRelativeHumidity
            :Description: New relative humidity in -.

**Livestock Adaptive Clothing**

:Description:
    | Computes the clothing isolation in clo for a given outdoor temperature.
    | Source: Havenith et al. - 2012 - "The UTCI-clothing model"

:Inputs:
    :1.:    :Name: Temperature
            :Description: Temperature in C
            :Data Access: List
            :Default Value: None
|
:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: ClothingValue
            :Description: Calculated clothing value in clo.

