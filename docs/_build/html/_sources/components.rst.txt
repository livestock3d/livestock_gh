Livestock Grasshopper Components
================================

0 | Miscellaneous
-----------------

Livestock Python Executor

Livestock SSH Connection


1 | Geometry
------------

Livestock Load Mesh

Livestock Save Mesh

3 | CMF
-------

Livestock CMF Ground

Livestock CMF Weather

Livestock CMF Vegetation Properties

Livestock CMF Synthetic Tree

Livestock CMF Retention Curve

Livestock CMF Solve

Livestock CMF Results

Livestock CMFOutputs

Livestock CMF Boundary Condition

Livestock CMF Solver Settings

Livestock CMF Surface Flux Result

4 | Comfort
-----------

**Livestock New Air Conditions**

:Description:

:Inputs:
    :1.:    :Name: Mesh
            :Description: Ground Mesh
            :Data Access: Item
            :Default Value: None

    :2.:    :Name: Evapotranspiration
            :Description: Evapotranspiration in m^3/day.
                          Each tree branch should represent one time unit, with all the cell values to that time.
            :Data Access: Tree
            :Default Value: None

    :3.:    :Name: HeatFlux
            :Description: HeatFlux in MJ/m^2day.
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

:Outputs:
    :1.:    :Name: readMe!
            :Description: In case of any errors, it will be shown here.

    :2.:    :Name: ClothingValue
            :Description: Calculated clothing value in clo.

