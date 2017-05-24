__author__ = "Christian Kongsgaard"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Christian Kongsgaard"
__email__ = "ocni@dtu.dk"
__status__ = "Work in Progress"


#-------------------------------------------------------------------------#
#DELPHIN FILES CLASSES

class Delphin:
    """
    Creates the Delphin .dpj file
    Takes Arguments: File, Info, Init, Materials, Wall, Climate, Boundary, Initial, Contact, Discretisation, OutputGeneral, Grids, OutputFormats, OutputFiles
    All arguments have to be the class object corresponding to their name.
    Materials: List of objects
    Climate: List of objects
    Boundary: List of objects
    Contact: List of objects or a false
    Initial: Object or a false
    Grids: List of objects
    OutputFormats: List of objects
    OutputFiles: List of objects
    """

    def __init__(self,File, Info, Init, Materials, Wall, Weather, Boundary, Initial, Contact, Discretisation, OutputGeneral, Grids, OutputFormats, OutputFiles ):
        self.File = File
        self.Info = Info
        self.Init = Init
        self.Materials = Materials
        self.Wall = Wall
        self.Climate = Weather
        self.Boundary = Boundary
        self.Initial = Initial
        self.Contact = Contact
        self.Discretisation = Discretisation
        self.OutGen = OutputGeneral
        self.Grids = Grids
        self.OutputFormats = OutputFormats
        self.OutputFiles = OutputFiles

    def create(self):
        file_obj = open(self.File.F, 'w')

        #Write Project Information
        file_obj.write('[PROJECT_INFO]' + '\n\n')
        file_obj.write(self.Info.write())
        file_obj.write('; ******************************************************************************' +'\n\n')

        #Write Initialization parameters
        file_obj.write('[INIT]' + '\n\n')
        file_obj.write(self.Init.write())
        file_obj.write('\n'+'; ******************************************************************************' + '\n\n')

        #Write Materials
        file_obj.write('[MATERIALS]' + '\n\n')
        for m in self.Materials:
            file_obj.write(m.writeMaterial())
            file_obj.write('\n')
        file_obj.write('\n' + '; ******************************************************************************' + '\n\n')

        # Write Wall
        file_obj.write('[CONDITIONS]' + '\n\n')
        file_obj.write('  [WALLS]' + '\n\n')
        file_obj.write(self.Wall.write())
        file_obj.write('\n')

        # Write Climate Conditions
        file_obj.write('  [CLIMATE_CONDITIONS]' + '\n\n')
        for w in self.Climate:
            file_obj.write(w.write())
            file_obj.write('\n')
        file_obj.write('\n\n')

        # Write Boundary Conditions
        file_obj.write('  [BOUNDARY_CONDITIONS]' + '\n\n')
        for b in self.Boundary:
            file_obj.write(b.writeBoundary())
            file_obj.write('\n')
        file_obj.write('\n\n')

        # Write Initial Conditions
        if self.Initial != False:
            file_obj.write('  [INITIAL_CONDITIONS]' + '\n\n')
            #file_obj.write(self.Initial.writeInitial() + '\n')

        # Write Contact Conditions
        if self.Contact != False:
            file_obj.write('  [CONTACT_CONDITIONS]' + '\n\n')
            for c in self.Contact:
                file_obj.write(c.writeContact() + '\n')

        #Write Default Conditions
        file_obj.write('  [DEFAULT_CONDITIONS]' + '\n\n')
        file_obj.write('    DEFAULT_TEMPERATURE      = 20 C' + '\n')
        file_obj.write('    DEFAULT_RELHUM           = 80 %' + '\n')
        file_obj.write('\n' + '; ******************************************************************************' + '\n\n')

        #Write Discretisation
        file_obj.write('[DISCRETISATION]' + '\n\n')
        file_obj.write(self.Discretisation.write() + '\n')
        file_obj.write('\n' + '; ******************************************************************************' + '\n\n')

        # Write Outputs
        file_obj.write('[OUTPUTS]' + '\n\n')
        file_obj.write(self.OutGen.write() + '\n')
        file_obj.write('\n')

        # Write Grids
        file_obj.write('  [GRIDS]' + '\n\n')
        for g in self.Grids:
            file_obj.write(g.write())
            file_obj.write('\n')

        # Write Output Formats
        file_obj.write('  [FORMATS]' + '\n\n')
        for of in self.OutputFormats:
            file_obj.write(of.write())
            file_obj.write('\n')

        # Write Output Files
        file_obj.write('  [FILES]' + '\n\n')
        for of in self.OutputFiles:
            file_obj.write(of.writeOutputFile())
            file_obj.write('\n')
        file_obj.write('\n' + '; ******************************************************************************' + '\n\n')

        #Write Assignments
        file_obj.write('[ASSIGNMENTS]' + '\n\n')

        # Write Assign Materials
        for m in self.Materials:
            file_obj.write(m.writeAssign())
            file_obj.write('\n')

        # Write Assign Boundary Conditions
        for b in self.Boundary:
            file_obj.write(b.writeAssign())
            file_obj.write('\n')

        # Write Assign Contact Conditions
        if self.Contact != False:
            for c in self.Contact:
                file_obj.write(c.writeAssign())
                file_obj.write('\n')

        # Write Assign Initial Conditions
        #if self.Initial != False:
        #    i = self.Initial
        #    file_obj.write(i.writeAssign())
        #    file_obj.write('\n')

        # Write Assign Output Files
        for of in self.OutputFiles:
            file_obj.write(of.writeAssign())
            file_obj.write('\n')
        file_obj.write('\n' + '; ******************************************************************************' + '\n\n')

        #Close and end process
        file_obj.close()

#-------------------------------------------------------------------------#
#File

class File:
    """
    Constructs the filename and path for the Delphin .dpj file
    Takes Arguments: Name, Path
    Name: String - Containing the filename
    Path: String - Folder path
    """

    def __init__(self,Name,Path):
        self.N = Name
        self.P = Path
        self.F = self.P + '\\' + self.N + '.dpj'

#-------------------------------------------------------------------------#
#Project Info

class ProjectInfo:
    """
    Takes no arguments
    However ProjectInfo is mandatory object in the Delphin file
    If no parameters is changed the object will be filled with defaults
    """

    def __init__(self):
        import datetime
        from getpass import getuser
        today = datetime.datetime.today()
        time = today.strftime('%a %b %m %H:%M:%S %Y')
        user = str(getuser())

        self.Version = '5.9.0'
        self.Created = time
        self.Edit = time
        self.Materials = '$(INSTALL_DIR)/DB_material_data'
        self.User_Materials = 'C:/Users/' + user + '/AppData/Roaming/IBK/material_data'
        self.Climate = '$(INSTALL_DIR)/DB_climate_data'
        self.Salt = '$(INSTALL_DIR)/DB_salt_data'
        self.VOC = '$(INSTALL_DIR)/DB_VOC_data'
        self.User_Climate = 'C:/Users/' + user + '/AppData/Roaming/IBK/climate_data'

    def write(self):
        return '  FILE_VERSION             = ' + self.Version + '\n' +\
               '  CREATED                  = ' + self.Created + '\n' +\
               '  LAST_EDIT                = ' + self.Edit + '\n\n' +\
               '; ******************************************************************************' + '\n\n' +\
               '[DIRECTORIES]' + '\n\n' +\
               '  MATERIALS                = ' + self.Materials + '\n' +\
               '  USER_MATERIALS           = ' + self.User_Materials + '\n' +\
               '  CLIMATE                  = ' + self.Climate + '\n' +\
               '  SALT                     = ' + self.Salt + '\n' +\
               '  VOC                      = ' + self.VOC + '\n' +\
               '  USER_CLIMATE             = ' + self.User_Climate + '\n\n'

#-------------------------------------------------------------------------#
#Init

class Initialization:
    """
    Takes no arguments
    However Initialization is mandatory object in the Delphin file
    If no parameters is changed the object will be filled with defaults
    """

    def __init__(self):
        self.Balance_Equations = 'ENERGY MOISTURE'
        self.Kirchhoff = 'yes'
        self.Gravity = 'no'
        self.Buoyancy = 'no'
        self.Hydrostatic = 'no'
        self.Pressure_interval = 10
        self.Year = 2016 #Start year
        self.Time = 31532400 # 31st of december, 23.00 Hours
        self.Duration = 8760 #Hours = 1 year
        self.Isothermal_Ref = 20

        self.Salt_output = 'no'
        self.Oversaturation = 'no'
        self.Density = 'yes'
        self.Flow_resistance_factor = 0

        self.Initial_dt = 0.01
        self.Max_dt = 30
        self.Min_dt = 10**(-9)
        self.Rel_tol = 10**(-5)
        self.Abs_tol_energy = 1
        self.Abs_tol_moisture = 10**(-6)
        self.Abs_tol_air = 10**(-6)
        self.Abs_tol_salt = 10**(-10)
        self.Abs_tol_pollutant = 10**(-12)
        self.Auto_Recover = 'yes'
        self.Max_Order = 5
        self.Max_Steps = 10**6
        self.Monitors_file = 'no'
        self.One_step_monitors = 'no'
        self.Prevent_Overfilling = 'yes'
        self.Strict_Range_Checking = 'no'

    def write(self):
        return '  [GENERAL]' + '\n' +\
               '    BALANCE_EQUATIONS        = ' + self.Balance_Equations + '\n' +\
               '    USE_KIRCHHOFF            = ' + self.Kirchhoff + '\n' +\
               '    USE_GRAVITY              = ' + self.Gravity + '\n' +\
               '    USE_BUOYANCY             = ' + self.Buoyancy + '\n' +\
               '    USE_HYDROSTATIC          = ' + self.Hydrostatic  + '\n' +\
               '    PRESSURE_UPDATE_INTERVAL = ' + str(self.Pressure_interval) + ' min'   + '\n' +\
               '    START_YEAR               = ' + str(self.Year) + '\n' +\
               '    START_TIME               = ' + str(self.Time) + '\n' +\
               '    DURATION                 = ' + str(self.Duration) + ' h' + '\n' +\
               '    ISOTHERMAL_T_REF         = ' + str(self.Isothermal_Ref) + ' C' + '\n\n' +\
               '  [SALT_SETTINGS]' + '\n' +\
               '    USE_EXTRA_SALT_OUTPUT    = ' + self.Salt_output + '\n' +\
               '    USE_OVERSATURATION       = ' + self.Oversaturation + '\n' +\
               '    USE_DENSITY              = ' + self.Density + '\n' +\
               '    FLOW_RESISTANCE_FACTOR   = ' + str(self.Flow_resistance_factor) + '\n\n\n' +\
               '  [SOLVER_SETTINGS]' + '\n' +\
               '    [CVODE_SOLVER_SETTINGS]' + '\n' +\
               '      INITIAL_DT               = ' + str(self.Initial_dt) + ' s' + '\n' +\
               '      MAX_DT                   = ' + str(self.Max_dt) + ' min' + '\n' +\
               '      MIN_DT                   = ' + str(self.Min_dt) + ' s' + '\n' +\
               '      REL_TOL                  = ' + str(self.Rel_tol) + '\n' +\
               '      ABS_TOL_ENERGY           = ' + str(self.Abs_tol_energy) + '\n' +\
               '      ABS_TOL_MOISTURE         = ' + str(self.Abs_tol_moisture) + '\n' +\
               '      ABS_TOL_AIR              = ' + str(self.Abs_tol_air) + '\n' +\
               '      ABS_TOL_SALT             = ' + str(self.Abs_tol_salt) + '\n' +\
               '      ABS_TOL_POLLUTANT        = ' + str(self.Abs_tol_pollutant) + '\n' +\
               '      USE_AUTO_RECOVER         = ' + str(self.Auto_Recover) + '\n' +\
               '      MAX_ORDER                = ' + str(self.Max_Order) + '\n' +\
               '      MAX_STEPS                = ' + str(self.Max_Steps) + '\n' +\
               '      USE_MONITORS_FILE        = ' + self.Monitors_file + '\n' +\
               '      USE_ONE_STEP_MONITORS    = ' + self.One_step_monitors  + '\n' +\
               '      PREVENT_OVERFILLING      = ' + self.Prevent_Overfilling  + '\n' +\
               '      USE_STRICT_RANGE_CHECKING = ' + self.Strict_Range_Checking  + '\n'

#-------------------------------------------------------------------------#
#Materials

class Material:
    """
    Takes Arguments: Name, ID, Range, Path
    Name: String - Name of the material as stated in the material database
    ID: Integer - ID number of the material as stated in the material database
    Range: List with 4 integers - Range, which the material covers
    Path: Path - Path where the material file are stored.
    """

    def __init__(self, Name, ID, Range, Path = '$(MATERIALS_DIR)/', color = '#ff404060'):
        self.Path = Path
        self.Name = Name
        self.ID = str(ID)
        self.RX = Range[0],Range[1]
        self.RY = Range[2],Range[3]
        self.R = [self.RX[0],self.RY[0],self.RX[1],self.RY[1]]
        self.Range = ' '.join(str(e) for e in self.R)
        self.Color = color


    def UpdateRange(self):
        self.R = [self.RX[0],self.RY[0],self.RX[1],self.RY[1]]
        self.Range = ' '.join(str(e) for e in self.R)

    def writeMaterial(self):
        #By default the material are assigned with a grey color, but it can be changed.
        return '  [MATERIAL]' + '\n' +\
               '    EXTERNAL                 = ' + self.Path + self.Name + '_' + self.ID + '.m6' + '\n' + \
               ' ' + '\n' +\
               '    [IDENTIFICATION]' + '\n' +\
               '      NAME                     = ' + self.Name + '\n' +\
               '      COLOUR                   = ' + self.Color + '\n' +\
               '      UNIQUE_ID                = ' + self.ID + '\n'

    def writeAssign(self):
        return '  [SELECTION]' + '\n' +\
               '    TYPE                     = ' + 'MATERIAL' + '\n' +\
               '    RANGE                    = ' + self.Range + '\n' +\
               '    NAME                     = ' + self.Name + '\n' +\
               '    LOCATION                 = ' + 'ELEMENT' + '\n'

#-------------------------------------------------------------------------#
#Wall

class Wall:
    """
    Takes Arguments: Orientation, Inclination, Latitude
    Orientation: Integer - Orientation of the wall in degrees. North = 0 Deg, East = 90 Deg
    Inclination: Integer - Inclination of the wall in degrees. Default is set at 90 Deg, which coresponds to a vertical wall
    Latitude: Integer - Latitude for the location where the wall is placed. The information is used for Delphins solar radiation calculation
    """

    def __init__(self, Orientation, Inclination = 90, Latitude = 55):
        self.Or = str(Orientation)
        self.In = str(Inclination)
        self.La = str(Latitude) #A latitude of 55 corespons to the location of Denmark

    def write(self):
        return '  [WALL_DATA]'+'\n' +\
               '      NAME                     = Wall\n' +\
               '      ORIENTATION              = ' + self.Or +' Deg'+'\n' +\
               '      INCLINATION              = ' + self.In +' Deg'+'\n' +\
               '      LATITUDE                 = ' + self.La +' Deg' + '\n' +\
               '      WALLAREA                 = 1 m2' + '\n'

#-------------------------------------------------------------------------#
#Discretisation

class Discretisation:
    """
    Takes Arguments: X, Y
    X: List of floats - List of element widths (in meters) in the X direction
    Y: List of floats - List of element widths (in meters) in the Y direction
    """

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.x = ' '.join(str(e) for e in self.X)
        self.y = ' '.join(str(e) for e in self.Y)

    def write(self):
        return '  GEOMETRY                 = PLANE2D' + '\n' +\
               '  X_STEPS                  = ' + self.x + ' m' + '\n' +\
               '  Y_STEPS                  = ' + self.y + ' m' + '\n' +\
               '  Z_STEPS                  = 1 m' + '\n' +\
               '  THETA_Z                  = 0' + '\n' +\
               '  PIE_SLICE_ANGLE          = 360' + '\n'

#-------------------------------------------------------------------------#
#Weather

class Weather:
    """
    Takes Arguments: IN_OUT, WeatherType, Filename
    IN_OUT: String - Either "IN" or "OUT". Indicates whether the weather is located on the inside or outside of the construction
    WeatherType: String - Delphin Weather Type
    Filename: String - Filename and path to the weather file
    """

    def __init__(self, IN_OUT, WeatherType, Filename):
        self.WT = WeatherType
        self.FN = Filename

        #Generate Name for the weather
        self.N = self.WT + '_' + IN_OUT

        #Generate unit for the weather
        if self.WT == 'TEMPER':
            self.U = 'K'
        elif self.WT == 'RELHUM':
            self.U = '%'
        elif self.WT == 'HORRAIN' or self.WT == 'NORRAIN':
            self.U = 'l/m2s'
        elif self.WT == 'WINDDIR':
            self.U = 'Deg'
        elif self.WT == 'WINDVEL':
            self.U = 'm/s'
        elif self.WT == 'DIRRAD' or self.WT == 'DIFRAD' or self.WT == 'SKYEMISS' or self.WT == 'SHWRAD':
            self.U = 'W/m2'
        else:
            print('Wrong Weather Type or Weather Type has not been implemented')
            exit()

    def write(self):
        return '    [CLIMATE_COND]'+'\n' +\
               '      TYPE                     = '+ self.WT +'\n' +\
               '      NAME                     = '+ self.N +'\n' +\
               '      KIND                     = DATLINEAR'+'\n' +\
               '      FILENAME                 = ' + self.FN + '\n' +\
               '      USE_INTERPOLATION        = yes' + '\n' +\
               '      EXTEND_DATA              = yes' + '\n' +\
               '      CYCLIC_DATA              = yes' + '\n' +\
               '      SHIFTVALUE               = 0 ' + self.U  + '\n'

# -------------------------------------------------------------------------#
#BoundaryCondition

class BoundaryCondition:
    """
    Takes Arguments: ConditionType, Kind, In_Out, Coefficient_Arguments, Weather
    ConditionType: String - Delphin Boundary Condition Type
    Kind: String - Delphin Boundary Condition Kind
    IN_OUT: List - First elements has to be OUT or IN, indicating if the Boundary Condition is on the inside or outside. Second element indicates what element the boundary condition should be assigned to
    Coefficient_Arguments: Float of list of floats - Coefficients for the Boundary Condition
    Weather: Class - Weather which should be included in the Boundary Condition
    """

    def __init__(self,ConditionType,Kind,In_Out,Coefficient_Arguments,Weather):
        self.CT = ConditionType
        self.K = Kind
        self.IO = In_Out
        self.CA = []
        for i in Coefficient_Arguments:
            self.CA.append(str(i))
        self.W = Weather

        # Generate Name for the Weather
        self.N = self.CT + '_' + self.IO[0]

        # Generate Range and Location of the weather
        if self.IO[0] == 'OUT':
            self.R = str(self.IO[1][0]) + ' ' + str(self.IO[1][1]) + ' ' + str(self.IO[1][0]) + ' ' + str(self.IO[1][1])
            self.L = 'RIGHT'

        if self.IO[0] == 'IN':
            self.R = str(self.IO[1][0]) + ' ' + str(self.IO[1][1]) + ' ' + str(self.IO[1][0]) + ' ' + str(self.IO[1][1])
            self.L = 'LEFT'

    def writeBoundary(self):

        #Handle Heat Condution
        if self.CT == 'HEATCOND':
            if self.W[0].WT != 'TEMPER':
                print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                exit()

            else:
                return '  [BOUND_COND]' + '\n' +\
                       '      TYPE                     = ' + self.CT + '\n' +\
                       '      NAME                     = ' + self.N + '\n' +\
                       '      KIND                     = ' + self.K + '\n' +\
                       '      EXCOEFF                  = ' + self.CA[0] + ' W/m2K' + '\n' +\
                       '      TEMPER                   = ' + self.W[0].N + '\n'

        #Handle Vapour Diffusion
        elif self.CT == 'VAPDIFF':
            if self.W[0].WT != 'TEMPER' or self.W[1].WT != 'RELHUM':
                print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                exit()

            else:
                return '  [BOUND_COND]' + '\n' +\
                       '      TYPE                     = ' + self.CT + '\n' +\
                       '      NAME                     = ' + self.N + '\n' +\
                       '      KIND                     = ' + self.K + '\n' +\
                       '      EXCOEFF                  = ' + self.CA[0] + ' s/m' + '\n' +\
                       '      TEMPER                   = ' + self.W[0].N + '\n' +\
                       '      RELHUM                   = ' + self.W[1].N + '\n'

        #Handle Wind Driven Rain
        elif self.CT == 'RAIN':
            #Delphin's Standard Rain Model
            if self.K == 'STDRAIN':
                if self.W[0].WT != 'TEMPER' or self.W[1].WT != 'RELHUM' or self.W[2].WT != 'HORRAIN' or self.W[3].WT != 'WINDDIR' or self.W[4].WT != 'WINDVEL' :
                    print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                    exit()

                else:
                    return '  [BOUND_COND]' + '\n' +\
                           '      TYPE                     = ' + self.CT + '\n' +\
                           '      NAME                     = ' + self.N + '\n' +\
                           '      KIND                     = ' + self.K + '\n' +\
                           '      EXPCOEFF                  = ' + self.CA[0] + ' -' + '\n' +\
                           '      MINRTEMP                  = -2 C' + '\n' +\
                           '      MINRFLUX                  = 0 l/m2s' + '\n' +\
                           '      WALLDATA                 = Wall' + '\n' +\
                           '      TEMPER                   = ' + self.W[0].N + '\n' +\
                           '      RELHUM                   = ' + self.W[1].N + '\n' +\
                           '      HORRAIN                  = ' + self.W[2].N + '\n' +\
                           '      WINDDIR                  = ' + self.W[3].N + '\n' +\
                           '      WINDVEL                  = ' + self.W[4].N + '\n'

            #Imposed Flux
            elif self.K == 'IMPFLUX':
                if self.W[0].WT != 'TEMPER' or self.W[1].WT != 'RELHUM' or self.W[2].WT != 'NORAIN':
                    print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                    exit()

                else:
                    return '  [BOUND_COND]' + '\n' +\
                           '      TYPE                     = ' + self.CT + '\n' +\
                           '      NAME                     = ' + self.N + '\n' +\
                           '      KIND                     = ' + self.K + '\n' +\
                           '      EXPCOEFF                  = ' + self.CA[0] + '-' + '\n' +\
                           '      MINRTEMP                  = ' + '-2 C' + '\n' +\
                           '      MINRFLUX                  = ' + '0 l/m2s' + '\n' +\
                           '      WALLDATA                  = Wall' + '\n' +\
                           '      TEMPER                   = ' + self.W[0].N + '\n' +\
                           '      RELHUM                   = ' + self.W[1].N + '\n' +\
                           '      NORRAIN                   = ' + self.W[2].N + '\n'

            else:
                print('Unknown weather kind for rain. Can not assign boundary condition. Weather kind used was:', str(self.K))
                exit()

        #Handle Shortwave Radiation
        elif self.CT == 'SHWRAD':
            #Delphin's Shortwave Radiation Model
            if self.K == 'SUNRADM':
                if self.W[0].WT != 'DIRRAD' or self.W[1].WT != 'DIFRAD':
                    print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                    exit()

                else:
                    return '  [BOUND_COND]' + '\n' +\
                           '      TYPE                     = ' + self.CT + '\n' +\
                           '      NAME                     = ' + self.N + '\n' +\
                           '      KIND                     = ' + self.K + '\n' +\
                           '      SURABSOR                 = ' + str(self.CA[0]) + ' -' + '\n' +\
                           '      GRDREFLE                 = ' + str(self.CA[1]) + ' -' + '\n' +\
                           '      WALLDATA                 = Wall' + '\n' +\
                           '      DIRRAD                   = ' + self.W[0].N + '\n' +\
                           '      DIFRAD                   = ' + self.W[1].N + '\n'

            #Imposed Flux
            elif self.K == 'IMPFLUX':
                if self.W[0].WT != 'SHWRAD':
                    print('Wrong weather type. Can not assign boundary condition', str(self.CT))
                    exit()

                else:
                    return '  [BOUND_COND]' + '\n' +\
                           '      TYPE                     = ' + self.CT + '\n' +\
                           '      NAME                     = ' + self.N + '\n' +\
                           '      KIND                     = ' + self.K + '\n' +\
                           '      SURABSOR                 = ' + self.CA[0] + ' -' + '\n' +\
                           '      WALLDATA                 = Wall' + '\n' +\
                           '      SHWRAD                   = ' + self.W[0].N + '\n'
            else:
                print('Unknown weather kind for short wave radiation. Can not assign boundary condition. Weather kind used was:', str(self.K))
                exit()

        #Handle Longwave Radiation
        elif self.CT == 'LOWRAD':
            if self.W[0].WT != 'SKYEMISS':
                print('Wrong weather types. Can not assign boundary condition', str(self.CT))
                exit()

            else:
                return '  [BOUND_COND]' + '\n' +\
                       '      TYPE                     = ' + self.CT + '\n' +\
                       '      NAME                     = ' + self.N + '\n' +\
                       '      KIND                     = ' + self.K + '\n' +\
                       '      SUREMISS                 = ' + self.CA[0] + ' -' + '\n' +\
                       '      WALLDATA                 = Wall' + '\n' +\
                       '      SKYEMISS                 = ' + self.W[0].N + '\n'
        else:
            print('Can not recognize weather types. Can not assign boundary condition')
            exit()

    def writeAssign(self):
        return '  [SELECTION]' + '\n' +\
               '    TYPE                     = ' + 'BOUNDARYCOND' + '\n' +\
               '    RANGE                    = ' + self.R + '\n' +\
               '    NAME                     = ' + self.N + '\n' +\
               '    LOCATION                 = ' + self.L + '\n' +\
               '    CONDITION_TYPE           = ' + self.CT + '\n'

# -------------------------------------------------------------------------#
#Initial Conditions

class InitialCondition:
    """
    Takes arguments: Type, Value, Range
    Type: String - Type of initial condition e.g. TEMPER or RELHUM
    Value: Float - Value of the argument
    Range: List - Where the initial condition should be assigned
    If false is inputed instead, no InitialCondition will be applied
    """

    def __init__(self, Type, Value, Range):
        self.T = Type
        if self.T == 'TEMPER':
            self.VU = ' C'
        elif self.T == 'RELHUM':
            self.VU = ' %'
        self.V = str(Value)
        self.N = 'Initial_' + self.T
        self.RX = Range[0], Range[1]
        self.RY = Range[2], Range[3]
        self.R = [self.RX[0], self.RY[0], self.RX[1], self.RY[1]]
        self.Range = ' '.join(str(e) for e in self.R)

    def writeInitial(self):
        return '    [INIT_COND]' + '\n' +\
               '      NAME                     = ' + self.N + '\n' +\
               '      TYPE                     = ' + self.T + '\n' +\
               '      VALUE                    = ' + self.V + self.VU + '\n'

    def writeAssign(self):
        return '  [SELECTION]' + '\n' +\
               '    TYPE                     = INITIALCOND' + '\n' +\
               '    RANGE                    = ' + self.Range + '\n' +\
               '    NAME                     = ' + self.N + '\n' +\
               '    LOCATION                 = ELEMENT' + '\n' +\
               '    CONDITION_TYPE           = ' + self.T

# -------------------------------------------------------------------------#
# Contact Conditions

class ContactCondition:
    """
    Takes arguments: Value, Range, Type
    Value: Float - Value of the argument
    Range: List - Where the initial condition should be assigned
    Type: String - Type of initial condition e.g. TEMPER or RELHUM
    If false is inputed instead, no InitialCondition will be applied
    """

    def __init__(self, OUT_IN, Value, Type='ADDITIONAL_RESISTANCE'):
        self.T = Type
        self.V = str(Value)
        self.IO = OUT_IN
        self.N = 'Contact_Vapdiff_' + self.IO[0]

        # Generate Range and Location of the contact condition
        if self.IO[0] == 'OUT':
            self.R = str(self.IO[1][0]) + ' ' + str(self.IO[1][1]) + ' ' + str(self.IO[1][0]) + ' ' + str(self.IO[1][1])
            self.L = 'LEFT'

        if self.IO[0] == 'IN':
            self.R = str(self.IO[1][0]) + ' ' + str(self.IO[1][1]) + ' ' + str(self.IO[1][0]) + ' ' + str(self.IO[1][1])
            self.L = 'RIGHT'

    def writeContact(self):
        return '    [CONTACT_COND]' + '\n' + \
               '      TYPE                     = ' + self.T + '\n' + \
               '      NAME                     = ' + self.N + '\n' + \
               '      VAPDIFFRES               = ' + self.V + ' m' + '\n'

    def writeAssign(self):
        return '  [SELECTION]' + '\n' + \
               '    TYPE                     = CONTACTCOND' + '\n' + \
               '    RANGE                    = ' + self.R + '\n' + \
               '    NAME                     = ' + self.N + '\n' + \
               '    LOCATION                 = ' + self.L + '\n'

# -------------------------------------------------------------------------#
#Output General

class OutputGeneral:
    """
    Takes argument: Folder
    Folder: String - Folder path
    """

    def __init__(self,Folder):
        self.F = Folder
        self.Max_hyg_Relhum = 95
        self.Exp_ref_temper = 0
        self.Exp_ref_relhum = 60
        self.Thaw_begin = 0
        self.Freeze_begin = 0.01

    def write(self):
        return '  [GENERAL]' + '\n' +\
               '    OUTPUT_FOLDER            = ' + self.F + '\n' +\
               '    MAX_HYG_RELHUM           = ' + str(self.Max_hyg_Relhum) + ' %' + '\n' +\
               '    EXP_REF_TEMPER           = ' + str(self.Exp_ref_temper) + ' C' + '\n' +\
               '    EXP_REF_RELHUM           = ' + str(self.Exp_ref_relhum) + ' %' + '\n' +\
               '    THAW_BEGIN               = ' + str(self.Thaw_begin) + '\n' +\
               '    FREEZE_BEGIN             = ' + str(self.Freeze_begin) + ' ---' + '\n'

# -------------------------------------------------------------------------#
#Grid

class Grid:
    """
    Takes arguments: Name, Interval
    Name: String - Name of the grid
    Interval:
    """

    def __init__(self,Name,Interval):
        self.N = Name
        self.I = Interval

    def write(self):
        return '    [OUTPUT_GRID]\n' +\
               '      NAME                     = ' + self.N + '\n' +\
               '      INTERVAL                 = ' + self.I + '\n'

# -------------------------------------------------------------------------#
#OutputFormat

class OutputFormat:
    """
    Takes arguments: Name, Type, FieldType, SpaceType, TimeType, TimeUnit, Precision, Width, Format, Binary
    Name: String - Name of the Output Format
    Type: String -
    FieldType: String -
    SpaceType: String -
    TimeType: String -
    TimeUnit: String -
    Precision: Integer -
    Width: Integer - Width of the number field
    Format: String - Number format
    Binary: String - Has to be no or yes. Default is no.
    """

    def __init__(self, Name, Type, FieldType, SpaceType, TimeType, TimeUnit, Precision, Width, Format, Binary = 'no'):
        self.N = Name

        if str(Type) not in ['FIELD','FLUX']:
            print('Type has to be FIELD or FLUX')
            exit()
        self.T = Type

        self.FT = FieldType
        if self.FT == 'RELHUM':
            self.VU = '%'
        elif self.FT == 'TEMPER':
            self.VU = 'C'
        elif self.FT == 'THETAL':
            self.VU = 'm3'

        if str(SpaceType) not in ['SINGLE','MEAN']:
            print('SpaceType has to be SINGLE or MEAN')
            exit()
        self.ST = SpaceType

        if str(TimeType) not in ['NONE',]:
            print('TimeType has to be NONE')
            exit()
        self.TT = TimeType

        if str(TimeUnit) not in ['s', 'min', 'h', 'd', 'a']:
            print('TimeUnit has to be s, min, h, d or a')
            exit()
        self.TU = TimeUnit

        if int(Precision) < int(Width):
            print('Width ( ' + str(Width) + ') has to be larger than Precision ( ' + str(Precision)+')')
            exit()
        self.Pr = str(Precision)
        self.W = str(Width)

        if str(Format) not in ['DEFAULT', 'FIXED', 'SCIENTIFIC']:
            print('Format has to be DEFAULT, FIXED or SCIENTIFIC')
            exit()
        self.F = Format

        self.B = Binary

    def write(self):
        return '    [OUTPUT_FORMAT]' + '\n' +\
               '      NAME                     = ' + self.N + '\n' +\
               '      TYPE                     = ' + self.T + '\n' +\
               '      FIELD_TYPE               = ' + self.FT + '\n' +\
               '      SPACE_TYPE               = ' + self.ST + '\n' +\
               '      TIME_TYPE                = ' + self.TT + '\n' +\
               '      TIME_UNIT                = ' + self.TU + '\n' +\
               '      VALUE_UNIT               = ' + self.VU + '\n' +\
               '      PRECISION                = ' + self.Pr + '\n' +\
               '      WIDTH                    = ' + self.W + '\n' +\
               '      FORMAT                   = ' + self.F + '\n' +\
               '      BINARY                   = ' + self.B + '\n'

# -------------------------------------------------------------------------#
#OutputFile

class OutputFile:
    """
    Takes Arguments: Name, Grid, Format, Range
    Name: String - Name of the Output File
    Grid: Object - Grid object to preform the output file from
    Format: Object - OutputFormat to preform the output file from
    Range: List - Range which the output file applies to
    """

    def __init__(self, Name, Grid, Format, Range):
        self.G = Grid
        self.F = Format
        self.N = self.F.N + Name + '.out'
        self.RX = Range[0],Range[1]
        self.RY = Range[2],Range[3]
        self.R = [self.RX[0],self.RY[0],self.RX[1],self.RY[1]]
        self.Range = ' '.join(str(e) for e in self.R)

    def UpdateRange(self):
        self.R = [self.RX[0],self.RY[0],self.RX[1],self.RY[1]]
        self.Range = ' '.join(str(e) for e in self.R)

    def writeOutputFile(self):
        return '    [OUTPUT_FILE]' + '\n' +\
               '      NAME                     = ' + self.N + '\n' +\
               '      OUTPUT_GRID              = ' + self.G.N + '\n' +\
               '      OUTPUT_FORMAT            = ' + self.F.N + '\n'

    def writeAssign(self):
        return '  [SELECTION]\n' +\
               '    TYPE                     = ' + self.F.T +'OUTPUT' + '\n' +\
               '    RANGE                    = ' + self.Range + '\n' +\
               '    NAME                     = ' + self.N +'\n' +\
               '    LOCATION                 = ELEMENT' + '\n'

# -------------------------------------------------------------------------#
#PREPROCESS:

def Subdivision(Width,MinimumDivision, StretchFactor):
    """
    Creates a subdivision of the material to be used for the discretisation.
    Takes arguments: Width, NumberOfDivisions, StretchFactor
    Width: Number - Width of the material to be subdivided
    MinimumDivision: Integer - Width of the smallest division
    StretchFactor: Float - Increase in subdivisions
    Returns list containing width of subdivisions
    """

    import numpy as np

    sumx = 0
    next = MinimumDivision
    new_grid = []
    max_dx = 0.02
    x = Width/2

    while sumx < x:
        remaining = x - sumx

        if next> max_dx:
            n = np.ceil(remaining/max_dx)
            if n == 0:
                new_grid.append(remaining)

            next = remaining/n
            j = 0
            while j < n:
                new_grid.append(next)
                sumx += next
                j += 1

        remaining = x - sumx
        if next < remaining:
            new_grid.append(next)
            sumx += next
        else:
            remaining += new_grid[-1]
            new_grid[-1] = remaining/2
            new_grid.append(remaining/2)
            sumx = x

        next = next*StretchFactor

    x1 = new_grid[::-1]
    x2 = new_grid+x1

    return x2

class IndoorClimate:


    def __init__(self, Temp):
        import numpy as np
        self.Temp = Temp
        x = np.reshape(self.Temp, (365, 24))
        x = np.sum(x, 1)
        self.daylyAvg = x/24

    def EN13788(self,indoorClass):
        """
        Only the Continental class is implemented
        :param indoorClass: String - Either A or B
        :return: Two element list of lists with indoor temperature, and relative humidity
        """

        import numpy as np
        if indoorClass == 'A':
            deltaRH = 0
        elif indoorClass == 'B':
            deltaRH = 5
        else:
            print("Wrong indoor class. It has to be either A or B")
            exit()

        Tavg = self.daylyAvg
        Ti = []
        RHi = []

        #Create indoor temperature
        for t in Tavg:
            if t <= 10:
                Ti.append([20,]*24)
            elif t >= 20:
                Ti.append([25,]*24)
            else:
                ti = 0.5*t+15
                Ti.append([ti,]*24)

        #Create indoor relative humidity
        for rh in Tavg:
            if rh <= -10:
                RHi.append([35+deltaRH,]*24)
            elif rh >= 20:
                RHi.append([65+deltaRH,]*24)
            else:
                rhi = 1*rh+45
                RHi.append([rhi+deltaRH,]*24)

        return np.ravel(Ti), np.ravel(RHi)

class RainVertical:
    """
    #Reference: J. Straube - Simplified Prediction of Driving Rain on Buildings: ASHRAE 160P and WUFI 4.0 - 2010
    #https://buildingscience.com/documents/digests/bsd-148-wufi-simplified-driving-rain-prediction
    """

    def __init__(self, WindSpeed10, WindDirection, WindExposureCoefficient, Orientation, RainHorizontal, Height,
                 Width, House):
        import math as ma
        self.WS10 = WindSpeed10
        self.O = Orientation
        self.WD = WindDirection
        self.WEC = WindExposureCoefficient
        self.RH = RainHorizontal
        self.W = Width
        self.H = Height
        self.HW = House[0]
        self.HH = House[1]
        self.HT = House[2]

        # Run Check:
        er_mes = []
        if len(self.WS10) != len(self.WD) != len(self.RH):
            er_mes.append('Data length of wind speed, wind direction and rain horizontal are not the same!')

        if self.W > self.HW:
            er_mes.append('Width are greater than width of building!')

        if self.H > self.HH:
            er_mes.append('Height are greater then height of building!')

        if self.WEC != 0.14 and self.WEC != 0.25 and self.WEC != 0.36:
            er_mes.append('Wind exposure coefficient has to be either 0.14, 0.25 or 0.36!')

        if self.O < 0 or self.O > 360:
            er_mes.append('Orientation should be between 0 and 360 degrees!')

        if er_mes:
            for m in er_mes:
                print(m, '\n')
            exit()

        # Calculate Driving Rain Factor
        drf = []
        for r in self.RH:
            o = 1.104184263 * r ** (29 / 125)
            Vt = -0.166033 + 4.91844 * o - 0.888016 * o ** 2 + 0.054888 * o ** 3
            if Vt > 9.2:
                Vt = 9.2
            d = 1 / Vt
            if d < 0:
                d = 0
            drf.append(d)
        self.DRF = drf

        # Calculate Rain Admittance Factor
        # Type 1 functions:
        # Curve 0:
        def f0(x):
            return -3.53190031251 + 37.7141597621 * x - 120.744700406 * x ** 2 + 166.125695641 * x ** 3 - 83.1136682834 * x ** 4

        # Curve 1:
        def f1(x):
            return -0.931605494049 + 21.256922549 * x - 78.1848506706 * x ** 2 + 113.896391585 * x ** 3 - 56.9739535784 * x ** 4

        # Type 2 functions:
        # Curve 2:
        def f2(x):
            return 0.259119652159 + 2.03160916861 * x - 2.03205751441 * x ** 2

        # Curve 3:
        def f3(x):
            return 0.595275177771 + 1.28195941435 * x - 1.28224232364 * x ** 2

        # Type 3 functions:
        # Curve 4:
        def f4(x):
            return 0.825311363922 + 0.345717415246 * x - 0.3456903087 * x ** 2

        # Curve 5:
        def f5(x):
            return 0.562922788737 + 0.787906951295 * x - 0.787845174146 * x ** 2

        # Curve 6:
        def f6(x):
            return 0.18540434379 + 1.12533273028 * x - 1.12524449671 * x ** 2

        h = self.H / self.HH
        w = self.W / self.HW

        if self.HT == 1:
            if f0(w) >= h:
                self.RAF = 0.5
            elif f1(w) >= h:
                self.RAF = 0.7
            else:
                self.RAF = 0.95

        if self.HT == 2:
            if f2(w) >= h:
                self.RAF = 0.5
            elif f3(w) >= h:
                self.RAF = 0.65
            else:
                self.RAF = 0.9

        if self.HT == 3:
            if f4(w) >= h:
                self.RAF = 0.35
            elif f5(w) >= h:
                self.RAF = 0.425
            elif f6(w) >= h:
                self.RAF = 0.275
            else:
                self.RAF = 0.2

        # Wind speed correction for height
        vz = []
        for v in self.WS10:
            vz.append(v * self.H / 10 ** self.WEC)

        self.Vz = vz

        # Calculate angle between wall and wind direction:
        # Set upper bound for wind direction
        u = self.O + 90
        if u >= 360:
            u = u - 360

        # Set lower bound for wind direction
        l = self.O - 90
        if l <= 360:
            l = l + 360

        # Angle calculation
        ang = []
        for w in self.WD:
            dir = w - self.O
            if dir > u and dir < l:
                ang.append(0)
            else:
                dir = ma.cos(dir * ma.pi / 180)
                ang.append(abs(dir))
        self.A = ang

        # Calculate Wind Driven Rain (Vertical Rain)
        rv = []
        i = 0
        # print('Lenght of Vz: ', len(self.Vz))
        while i < len(self.Vz):
            # print('i: ',i)
            # raf = self.RAF
            # drf = self.DRF[i]
            # a =self.A[i]
            # vz = self.Vz[i]
            # rh = self.RH[i]

            # print('RAF ',raf)
            # print('DRF ', drf)
            # print('A ',a)
            # print('Vz ', vz)
            # print('RH ', rh)

            r = self.RAF * self.DRF[i] * self.A[i] * self.Vz[i] * self.RH[i]
            # print('R: ',r)
            rv.append(r)
            i += 1

        self.WDR = rv

#-------------------------------------------------------------------------#
#POSTPROCESS:

def read_avg(lst):
    """Reads the text file and returns data values"""

    file_obj = open(lst, 'r')
    data = []
    data_obj = file_obj.readlines()
    if str(data_obj[5][-5:-1]) != 'MEAN':
        print('Function only processes average space values!' + '\n' + str(data_obj[5][-5:]))
        exit()
    data_obj = data_obj[13:]
    #print(data_obj)
    for line in data_obj:
        line = line[:-1]
        data.append(float(line.split('\t')[1]))
    return data

class ProcessFile:
    """
    Takes Arguments: url, file_id
    url: String - url for MongoDatabase
    file_id: String - id for the simulated delphin file
    """


    #def __init__(self):

    def MouldIndex(self, RH, T, DrawBack, SensitivityClass, SurfaceQuality):
        """
        Computes a time series of the mould index
        Takes Arguments: SensitivityClass, DrawBack, SurfaceQuality
        SensitivityClass: Integer - Integer from 1 to 4, that defines the Sensitivity Class of the material. See source for elaboration.
        DrawBack: Integer - Integer from 1 to 4, that defines the mould drawback of the material. See source for elaboration.
        SurfaceQuality: Integer - Integer from 0 to 1, that defines the surface quality of the material. See source for elaboration.
        Source: T. Ojanen, H. Viitanen - Mold growth modeling of building structures using sensitivity classes of materials - 2010
        """
        import math

        #Initial setup:
        if SensitivityClass==1:
            SC = ((1,2),(1,7,2),80)
        elif SensitivityClass==2:
            SC = ((0.578,0.386),(0.3,6,1),80)
        elif SensitivityClass==3:
            SC = ((0.072,0.097),(0,5,1.5),85)
        elif SensitivityClass==4:
            SC = ((0.033,0.014),(0,3,1),85)

        if DrawBack == 1:
            D = 1
        elif DrawBack == 2:
            D = 0.5
        elif DrawBack == 3:
            D = 0.25
        elif DrawBack == 4:
            D = 0.1

        if SurfaceQuality < 0:
            SQ = 0
        elif SurfaceQuality > 1:
            SQ = 1
        else:
            SQ = SurfaceQuality

        k1_m1 = SC[0][0]
        k1_m3 = SC[0][1]
        A = SC[1][0]
        B = SC[1][1]
        C = SC[1][2]
        RHmin = SC[2]

        M = 0
        t = 0
        result = []

        i = 0

        #Loop through temperature and relative humidity list
        while i < len(RH):
            if T[i] > 20:
                RHcrit = RHmin
            else:
                RHcrit = -0.00267*T[i]**3 + 0.16*T[i]**2 - 3.13*T[i] + 100
                if RHcrit == 100:
                    RHcrit = 99.99

            Mmax = A + B*(RHcrit - RH[i])/(RHcrit - 100) - C*((RHcrit - RH[i])/(RHcrit - 100))**2

            if M < 1:
                k1 = k1_m1
            else:
                k1 = k1_m3

            try:
                k2 = max((1 - math.exp(2.3*(M - Mmax))), 0)
            except OverflowError:
                k2 = 1

            if RH[i] < RHcrit or T[i] <= 0:
                if t < 6:
                    dM = D * -0.00133
                    t += 1
                elif t >= 6 and t <= 24:
                    dM = 0
                    t += 1
                else:
                    dM = D * -0.000667
                    t += 1

            else:
                dM = 1/(7*math.exp(-0.68*math.log(T[i]) - 13.9*math.log(RH[i]) - 0.33*SQ + 66.02))*k1*k2
                t = 0

            M += dM
            if M < 0:
                M = 0
            result.append(M)

            i += 1

        return result

    def Frost(self, RH, T):
        """
        Evaluates frost risk
        Returns: List - Containing 0's and 1's. Where a 0 indicates no frost risk and an 1 indicate frost risk
        Source: John Gruenewalds Frost Model
        """
        import math

        # Water density:
        pl = 1000 #kg/m3
        #Specific Heat Capacity of Water:
        cl = 4187 #J/(kgK)
        #Specific Heat Capacity of Water-ice:
        ci = 2100 #J/(kgK)
        #Absolute Temperature
        T0 = -273.15 #C
        #Thaw Enthalpy for Water-ice
        hi = -333500 #J/kg
        #Gas constant for vapour
        Rv = 461.5 #J/(kgK)

        i = 0
        result = []

        while i <len(T):
            if T[i] >=   0:
                result.append(0)
            else:
                f_pu = pl * (-(hi / T0 * (T[i] + T0)) + (cl - ci) * (T[i] * math.log(T[i] / T0) - (T[i] + T0)))
                f_phi = math.exp(f_pu / (pl * Rv * T[i]))*100
                if RH[i]<=f_phi:
                    result.append(0)
                elif RH[i]>f_phi:
                    result.append(1)
            i += 1

        return result

    def FrostCurves(self, T):
        """
        Outputs Frost curve
        """

        import numpy as np

        # Water density:
        pl = 1000 #kg/m3
        #Specific Heat Capacity of Water:
        cl = 4187 #J/(kgK)
        #Specific Heat Capacity of Water-ice:
        ci = 2100 #J/(kgK)
        #Absolute Temperature
        T0 = 273.15 #K
        #Thaw Enthalpy for Water-ice
        hi = -333500 #J/kg
        #Gas constant for vapour
        Rv = 461.5 #J/(kgK)

        result = []
        maxT = max(T)
        minT = min(T)
        T = np.linspace(minT,maxT,200)

        for t in T:
            f_pu = pl * (-(hi / T0 * (t - T0)) + (cl - ci) * (t * np.log(t/T0) - (t - T0)))
            f_phi = np.exp(f_pu/(pl*Rv*t)) * 100
            result.append(f_phi)

        return result

    def WaterContent(self, U):
        """
        Evaluates development of water content in construction
        Returns: True if water content is converged. False if water content is not converged.
        """
        import numpy as np

        u = self.obj['U_Total_0']['values']
        listLenght = len(u)
        years = listLenght//8760

        if years <= 1:
            return False

        else:
            u = np.array(u)
            U = np.split(u,years)
            u0 = U[-2]
            u1 = U[-1]

#-------------------------------------------------------------------------#
#DATABASE:

def writeMaterialFile(url,uniqueID,path):
    """
    Function writes a Delphin material file from Mongo Database.
    :param url: String - url to database
    :param uniqueID: Integer - Unique ID for the material
    :param path: Path - Path to where to material file should be written to.
    :return:
    """

    ### Imports, etc.
    import pymongo
    import codecs

    client = pymongo.MongoClient(url)
    db = client['local']
    collection = db['materials']

    def writeContent(group,dictDB,model=False):
        unitDict = {"RHO":"kg/m3", "CE":"J/kgK", "THETA_POR":"m3/m3", "THETA_EFF":"m3/m3", "THETA_CAP":"m3/m3", "THETA_80":"m3/m3", "LAMBDA":"W/mK", "AW":"kg/m2s05", "MEW":"-", "KLEFF":"s", "DLEFF":"m2/s", "KG": "s"}

        if model:
            modelExist = False
            for key, value in dictDB.items():
                #print(key)
                try:
                    if key[3] == "[":
                        file.write("\n\n  " + "[MODEL]")
                except IndexError:
                    pass
        else:
            file.write("\n\n" + "[" + group + "]")

        for key, value in dictDB.items():
            if key.split("-")[0] == group:
                name = key.split("-")[1]

                if name == "FUNCTION" and key.split("-")[-1] == "X" and model != True: #Parameters under "FUNCTION"

                    funcValX = "      "
                    for v in value:
                        funcValX += str(v).ljust(20)

                    value = dictDB[key.strip("-X") + "-Y"]
                    funcValY = "      "
                    for v in value:
                        funcValY += str(v).ljust(20)
                    value = key.split("-")[2] + "\n" + funcValX + "\n" + funcValY

                    file.write("\n" + "  " + name.ljust(28) + "= " + str(value))

                elif name == "MODEL" and model: #parameters under "MODEL"
                    name = key.split("-")[-1]
                    file.write("\n" + "    " + name.ljust(28) + "= " + str(value))

                elif name in unitDict: #parameters with units
                    value = str(value) + " " + unitDict[name]
                    file.write("\n" + "  " + name.ljust(28) + "= " + str(value))

                elif len(key.split("-")) <= 2:
                    file.write("\n" + "  " + name.ljust(28) + "= " + str(value))



    ### DB Query
    query = {"INFO-UNIQUE_ID" : uniqueID}
    cursor = collection.find(query)


    for doc in cursor:
        #print(doc)
        dictDB = doc

    ### Create file
    file = codecs.open(path + '\\' + dictDB["INFO-FILE"], "w", "utf-8")

    ### Write lines
    file.write(dictDB["INFO-MAGIC_HEADER"])
    writeContent("IDENTIFICATION",dictDB)
    writeContent("STORAGE_BASE_PARAMETERS",dictDB)
    writeContent("TRANSPORT_BASE_PARAMETERS",dictDB)
    writeContent("MOISTURE_STORAGE",dictDB)
    writeContent("MOISTURE_STORAGE",dictDB,True)
    writeContent("MOISTURE_TRANSPORT",dictDB)
    writeContent("MOISTURE_TRANSPORT",dictDB,True)
    file.write("\n")

    file.close()

    return dictDB['INFO-MATERIAL_NAME']

def writeWeatherFile(aList, Type, unit, name, path, start = [0,0]):
    file = open(path + '\\' + name + '.ccd', 'w')
    file.write('# ' + name + '\n\n')
    file.write(Type + '   ' + unit+ '\n')

    i = 0
    d = start[0]
    h = start[1]
    while i < len(aList):
        file.write(str(d) + '\t' + '{:02d}'.format(h) + ':00:00\t' + str(aList[i]) + '\n')

        if h == 23:
            h = 0
            d += 1
        else:
            h += 1
        i += 1

    file.close()

def createSimulatedFiles(url,path):
    """
    Creates Delphin files from a MongoDatabase.
    :param url: url to the MongoDatabase.
    """

    # Imports
    import pymongo as pm
    import os
    from getpass import getuser

    client = pm.MongoClient(url)
    db = client['local']
    simQueue = db['simQueue']

    user = str(getuser())
    outFolder = 'C:\\Users\\' + user + '\\Desktop\\Delphin_Simulations'
    print('Files saved to: ' + outFolder + '\n')

    # run as long as we have filenames in the Queue
    for d in simQueue.find({'1D': True, 'Simulating': False}):
        delphin = {}

        #Object ID
        id = d['_id']

        # Create folders for input and outputs
        name = str(id)
        inputFolder = path + '\\' + name
        if not os.path.exists(inputFolder):
            os.makedirs(inputFolder)

        # Path and Name
        delphin['OutputGeneral'] = OutputGeneral(outFolder + '\\' + name)
        delphin['File'] = File(name, inputFolder)


        # Initilazations
        if d['Info'] == 'Standard':
            delphin['Info'] = ProjectInfo()
        else:
            print('Could not read database entry: Info')
            exit()

        if d['Init'] == 'Standard':
            delphin['Init'] = Initialization()
        else:
            print('Could not read database entry: Init')
            exit()

        # Wall
        # print('Wall')
        delphin['Wall'] = Wall(d['Wall'])

        # Grids
        # print('Grids')
        delphin['Grids'] = [Grid(d["Grids"][0], d["Grids"][1])]

        # Output Formats
        # print('Output Formats')
        OF = []
        for of in d['OutputFormats']:
            OF.append(OutputFormat(of[0], of[1], of[2], of[3], of[4], of[5], of[6], of[7], of[8], ))
        delphin['OutputFormats'] = OF

        # Widths
        # print('Widths')
        X = []
        Y = [1]
        Range = []
        j = 0
        while j < len(d['MaterialWidths']):
            range_before = len(X)
            materialWidth = d['MaterialWidths'][j]
            numberOfDivisions = d['Discretisation'][j][0]
            minimumDivision = d['Discretisation'][j][1]
            width = Subdivision(materialWidth, numberOfDivisions, minimumDivision)
            X += width
            Range += [[range_before, len(X) - 1]]
            j += 1
        delphin['Discretisation'] = Discretisation(X, Y)

        # Weather
        # print('Weather')
        weather0 = []
        for w in d['Weather']:
            weather0.append(Weather(w[0], w[1], w[2]))
        delphin['Weather'] = weather0

        # Boundary Conditions
        boundaryCondition = []
        for bc in d['Boundary']:
            weather1 = []
            for w in bc[4]:
                weather1.append(weather0[w])

            if bc[2] == 'OUT':
                boundaryCondition.append(BoundaryCondition(bc[0], bc[1], [bc[2], [0, 0]], bc[3], weather1))
            elif bc[2] == 'IN':
                boundaryCondition.append(
                    BoundaryCondition(bc[0], bc[1], [bc[2], [Range[-1][1], 0]], bc[3], weather1))
        delphin['Boundary'] = boundaryCondition

        # Materials
        # print('Materials')
        materials = []
        i = 0
        for m in d['Materials']:
            mf = ddt.writeMaterialFile(url, m, inputFolder)
            materials.append(Material(mf, m, [Range[i][0], Range[i][1], 0, 0, inputFolder]))
            i += 1
        delphin['Materials'] = materials

        # Contact Conditions
        contact = []
        for c in d['SurfaceTreatment']:
            if c[1] == 'OUT':
                contact.append(ContactCondition([c[1], [0, 0]], c[0]))
            elif c[1] == 'IN':
                contact.append(ContactCondition([c[1], [Range[-1][1], 0]], c[0]))
        delphin['Contact'] = contact

        # Output Files
        i = 0
        outputFiles = []
        for of in d['OutputFiles']:
            j = 0
            if of == 'Interface':
                outputFiles.append(OutputFile('_' + str(j), delphin['Grids'][0], OF[i], [0, 2, 0, 0]))
                while j < len(Range) - 1:
                    outputFiles.append(OutputFile('_' + str(j + 1), delphin['Grids'][0], OF[i],
                                                  [Range[j][1] - 1, Range[j + 1][0] + 1, 0, 0]))
                    j += 1
                outputFiles.append(
                    OutputFile('_' + str(j + 1), delphin['Grids'][0], OF[i],
                               [Range[-1][1] - 2, Range[-1][1], 0, 0]))
            elif of == 'All':
                outputFiles.append(
                    OutputFile('_' + str(j), delphin['Grids'][0], OF[i], [0, Range[-1][1], 0, 0]))
            i += 1
        delphin['OutputFiles'] = outputFiles

        # Initial Conditions
        delphin['Initial'] = InitialCondition

        # Create file
        #print('Create')
        Delphin(delphin['File'], delphin['Info'], delphin['Init'], delphin['Materials'], delphin['Wall'],
                delphin['Weather'],
                delphin['Boundary'], delphin['Initial'], delphin['Contact'], delphin['Discretisation'],
                delphin['OutputGeneral'], delphin['Grids'],
                delphin['OutputFormats'], delphin['OutputFiles']).create()
        print('Created: ' + name)

# -------------------------------------------------------------------------#
#SOLVERS:

def RunDelphin(DelphinDict,N_Threads):
    """
    Function to automate Delphin simulations.
    DelphinDict: A list of dictionaries on the form shown in line 789
    N_Threads: Number of threads/CPU's to preform the simulations on
    """

    # import the module for calling external programs (creating subprocesses )
    import subprocess
    import threading
    import queue

    #Specify the path to the DELPHIN solver executable
    delphin_executable = r'C:\Program Files (x86)\IBK\Delphin 5.8.3\delphin_solver.exe'
    print('Using: ' + delphin_executable)

    # create array to contain the filenames of the created projects
    #filenames = []

    # here we define our solver runner function
    def solver_runner():
        """ This function runs a DELPHIN solver . """

        # run as long as we have filenames in the Queue
        while 1:
            # get a new task from the Queue
            job = q.get()
            index = job[0]
            filename = job[1]
            print('Running : ' + filename)
            retcode = subprocess.call([delphin_executable, "-x", "-v0", filename])

            # if run was successful , remember project file for analysis
            if retcode == 0:
                print(job)
            #    run_results.append(job)
            # tell the Queue that the task was successfully done
            q.task_done()
    q = queue.Queue()

    # add threads
    for i in range(N_Threads):
        t = threading.Thread(target=solver_runner)
        t.setDaemon(True)
        t.start()

    # add the filenames ,alphas and betas to the queue
    for i in range(len(DelphinDict)):
        DD = DelphinDict[i]
        file = Delphin(DD['File'], DD['Info'], DD['Init'], DD['Materials'], DD['Wall'], DD['Weather'], DD['Boundary'], DD['Initial'], DD['Contact'], DD['Discretisation'], DD['OutputGeneral'], DD['Grids'], DD['OutputFormats'], DD['OutputFiles']).create()
        filename = DD['File'].F
        q.put([i, filename])

    q.join()

def DatabaseRun(url, N_Threads):
    """
    Runs Delphin files from a MongoDatabase.
    :param url: url to the MongoDatabase.
    :param N_Threads: Number of threads to run Delphin on.
    """

    # Imports
    import pymongo as pm
    import subprocess
    import threading
    import time
    import os
    from getpass import getuser

    client = pm.MongoClient(url)
    db = client['local']
    simQueue = db['simQueue']
    simResults = db['simResults']

    # Specify the path to the DELPHIN solver executable
    delphin_executable = r'C:\Program Files (x86)\IBK\Delphin 5.8.3\delphin_solver.exe'
    print('Using: ' + delphin_executable)

    # Create folders for output
    user = str(getuser())
    outFolder = 'C:\\Users\\' + user + '\\Desktop\\Delphin_Simulations'
    inFolder = 'C:\\Users\\' + user + '\\Desktop\\Delphin_Files'

    # Check if outFolder is created and if not create it
    if not os.path.exists(outFolder):
        os.makedirs(outFolder)

    # Check if outFolder is created and if not create it
    if not os.path.exists(inFolder):
        os.makedirs(inFolder)

    #Solver runner function
    def database_solver():
        """ This function runs a DELPHIN solver . """

        # run as long as we have filenames in the Queue
        while simQueue.find({'1D': False, 'Simulating': False}).sort('QueuePriority', pm.DESCENDING).count()>0:
            delphin = {}

            # Database
            data = simQueue.find({'1D': False, 'Simulating': False}).sort('QueuePriority', pm.DESCENDING).limit(1)
            d = data[0]
            id = d['_id']
            simQueue.update_one({'_id': id}, {'$set': {'Simulating': True}})

            #Create folders for input
            name = str(id)
            inputFolder = inFolder + '\\' + name + '_inputs'
            if not os.path.exists(inputFolder):
                os.makedirs(inputFolder)

            # Path and Name
            delphin['OutputGeneral'] = OutputGeneral(outFolder + '\\' + name)
            delphin['File'] = File(name, inFolder)
            #print('Running: ' + name)

            # Initilazations
            if d['Info'] == 'Standard':
                delphin['Info'] = ProjectInfo()
            else:
                print('Could not read database entry: Info')
                exit()

            if d['Init'] == 'Standard':
                delphin['Init'] = Initialization()
            else:
                print('Could not read database entry: Init')
                exit()

            # Wall
            #print('Wall')
            delphin['Wall'] = Wall(d['Wall'])

            # Grids
            #print('Grids')
            delphin['Grids'] = [Grid(d["Grids"][0], d["Grids"][1])]

            # Output Formats
            #print('Output Formats')
            OF = []
            for of in d['OutputFormats']:
                OF.append(OutputFormat(of[0], of[1], of[2], of[3], of[4], of[5], of[6], of[7], of[8], ))
            delphin['OutputFormats'] = OF

            # Widths
            #print('Widths')
            X = []
            Y = [1]
            Range = []
            j = 0
            while j < len(d['MaterialWidths']):
                range_before = len(X)
                materialWidth = d['MaterialWidths'][j]
                numberOfDivisions = d['Discretisation'][j][0]
                minimumDivision = d['Discretisation'][j][1]
                width = Subdivision(materialWidth, numberOfDivisions, minimumDivision)
                X += width
                Range += [[range_before, len(X) - 1]]
                j += 1
            delphin['Discretisation'] = Discretisation(X, Y)

            # Weather
            #print('Weather')
            weather0 = []
            for w in d['Weather']:
                weather0.append(Weather(w[0], w[1], w[2]))
            delphin['Weather'] = weather0

            # Boundary Conditions
            boundaryCondition = []
            for bc in d['Boundary']:
                weather1 = []
                for w in bc[4]:
                    weather1.append(weather0[w])

                if bc[2] == 'OUT':
                    boundaryCondition.append(BoundaryCondition(bc[0], bc[1], [bc[2], [0, 0]], bc[3], weather1))
                elif bc[2] == 'IN':
                    boundaryCondition.append(
                        BoundaryCondition(bc[0], bc[1], [bc[2], [Range[-1][1], 0]], bc[3], weather1))
            delphin['Boundary'] = boundaryCondition

            #Materials
            #print('Materials')
            materials = []
            i = 0
            for m in d['Materials']:
                mf = writeMaterialFile(url,m,inputFolder)
                materials.append(Material(mf, m, [Range[i][0], Range[i][1], 0, 0, inputFolder]))
                i += 1
            delphin['Materials'] = materials

            #Contact Conditions
            contact = []
            for c in d['SurfaceTreatment']:
                if c[1] == 'OUT':
                    contact.append(ContactCondition([c[1], [0, 0]], c[0]))
                elif c[1] == 'IN':
                    contact.append(ContactCondition([c[1], [Range[-1][1], 0]], c[0]))
            delphin['Contact'] = contact

            # Output Files
            i = 0
            outputFiles = []
            for of in d['OutputFiles']:
                j = 0
                if of == 'Interface':
                    outputFiles.append(OutputFile('_' + str(j), delphin['Grids'][0], OF[i], [0, 2, 0, 0]))
                    while j < len(Range) - 1:
                        outputFiles.append(OutputFile('_' + str(j + 1), delphin['Grids'][0], OF[i],
                                                      [Range[j][1] - 1, Range[j + 1][0] + 1, 0, 0]))
                        j += 1
                    outputFiles.append(
                        OutputFile('_' + str(j + 1), delphin['Grids'][0], OF[i],
                                   [Range[-1][1] - 2, Range[-1][1], 0, 0]))
                elif of == 'All':
                    outputFiles.append(OutputFile('_' + str(j), delphin['Grids'][0], OF[i], [0, Range[-1][1], 0, 0]))
                i += 1
            delphin['OutputFiles'] = outputFiles

            # Initial Conditions
            delphin['Initial'] = InitialCondition

            #Create file
            #print('Create')
            Delphin(delphin['File'], delphin['Info'], delphin['Init'], delphin['Materials'], delphin['Wall'], delphin['Weather'],
                           delphin['Boundary'], delphin['Initial'], delphin['Contact'], delphin['Discretisation'], delphin['OutputGeneral'], delphin['Grids'],
                           delphin['OutputFormats'], delphin['OutputFiles']).create()
            filename = delphin['File'].F
            folder = delphin['OutputGeneral'].F

            #Solve Delphin file
            print('Running : ' + filename)
            retcode = subprocess.Popen([delphin_executable, "-x", "-v1", filename],creationflags=subprocess.CREATE_NEW_CONSOLE).wait()

            # if run was successful
            if retcode == 0:
                #Update database
                print(filename, 'was simulated succesfully')
                simQueue.update_one({'_id': id}, {'$set': {'Simulating': False}})
                simQueue.update_one({'_id': id}, {'$set': {'1D': True}})

                #Delete Delphin file
                os.remove(filename)
                os.remove(filename + '.output')
                for entry in os.scandir(inputFolder):
                    if entry.is_file():
                        os.remove(inputFolder + '\\' + entry.name)
                os.rmdir(inputFolder)

                #Save results to database
                combFolder = folder
                id = 0
                for file in os.listdir(combFolder):
                    if file.endswith(".out"):
                        #print('Processing: ', file)
                        obj = open(combFolder + '\\' + file, 'r')
                        lines = obj.readlines()
                        del obj

                        if id == 0:
                            file_id = lines[2].split(' = ')[-1][:-1].split('/')[-1][:-4]
                            created = lines[3].split(' = ')[-1][:-1]

                            if simResults.find_one({'file_id': str(file_id)}):
                                id = simResults.find_one({'file_id': str(file_id)})['_id']
                                simResults.update_one({'_id': id}, {'$set': {'created': str(created)}})
                            else:
                                id = simResults.insert_one({'file_id': str(file_id), 'created': str(created)}).inserted_id
                            # print(id)
                            # print(type(id))

                        types = lines[1].split(' = ')[-1][:-1]
                        quantity = lines[4].split(' = ')[-1][:-1]
                        space_type = lines[5].split(' = ')[-1][:-1]
                        time_type = lines[6].split(' = ')[-1][:-1]
                        value_unit = lines[7].split(' = ')[-1][:-1]
                        time_unit = lines[8].split(' = ')[-1][:-1]
                        name = file[:-4]
                        values = []
                        for value in lines[13:-1]:
                            values.append(float(value.split(' ')[-1][:-1]))
                        simResults.update_one({'_id': id}, {'$set': {
                            str(name): {'Type': str(types), 'quantity': str(quantity), 'spaceType': str(space_type),
                                        'timeType': str(time_type),
                                        'valueUnit': str(value_unit), 'timeUnit': str(time_unit), 'values': values}}})

                        #Delete files after saving to database
                        os.remove(combFolder + '\\' + file)
                        #print('Deleted: ', file)
                    else:

                        # Delete non-result files
                        os.remove(combFolder + '\\' + file)

                #Delete folder
                os.rmdir(combFolder)

            else:
                print('Retcode: ', retcode)
                print(filename, 'was simulated unsuccesfully')
                simQueue.update_one({'_id': id}, {'$set': {'Simulating': False}})
                simQueue.update_one({'_id': id}, {'$set': {'1D': False}})

                file = open(folder + '\\' + filename + '.txt', 'w')
                file.write('Retcode: ' + retcode + '\n')
                file.write(filename + 'was simulated unsuccesfully')
                file.close()


    #print('Initial threads: ', threading.active_count())
    # add threads
    for i in range(N_Threads):
        #print('Threads after '+str(i)+' loops: ', threading.active_count())
        time.sleep(0.2)
        thread = threading.Thread(target=database_solver)
        thread.setDaemon(True)
        thread.start()

    i = 1
    while i:
        time.sleep(1)
        if simQueue.find({'1D': True, 'Simulating': False}).count() == simQueue.find().count():
            print('Simulations done!')
            os.rmdir(outFolder)
            os.rmdir(inFolder)
            exit()
        else:
            time.sleep(10)
