Livestock Grasshopper Components
================================

0 | Miscellaneous
-----------------

**Livestock Python Executor**

**Livestock SSH Connection**


1 | Geometry
------------

**Livestock Load Mesh**

**Livestock Save Mesh**

3 | CMF
-------

**Livestock CMF Ground**

**Livestock CMF Weather**

**Livestock CMF Vegetation Properties**

**Livestock CMF Synthetic Tree**

**Livestock CMF Retention Curve**

**Livestock CMF Solve**

**Livestock CMF Results**

**Livestock CMFOutputs**

**Livestock CMF Boundary Condition**
:Description:
Sets the solver settings for CMF Solve
|
:Inputs:
    :1.:    :Name: AnalysisLength
            :Description: Number of time steps to be taken - Default is 24
            :Data Access: Item
            :Default Value: 24

**Livestock CMF Solver Settings**

:Description:
Sets the solver settings for CMF Solve
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

