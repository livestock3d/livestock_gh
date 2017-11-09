__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports


# Livestock imports


# Grasshopper imports


# -------------------------------------------------------------------------------------------------------------------- #
# Plant Classes

def stomatal_resistance(rs_min, qr_sw, temperature, relative_humidity):
    """
    Calculates the stomatal resistance of a plant.
    From Manickathan, Lento et.al 2018 - Parametric study of the influence of environmental factors and tree properties
                                         on the transpirative cooling effect of trees.
    :param rs_min: Minimum of stomatal resistance in s/m
    :param qr_sw: short wave radiation in W/m2
    :param temperature: temperature in C
    :param relative_humidity: relative humidity is unitless
    :return: stomatal resistance in s/m
    """

    # constants
    a1 = 169  # W/m2
    a2 = 18  # W/m2
    a3 = 5*10**-9  # 1/Pa2 = 0.005 1/kPa2
    d0 = 1200  # Pa

    def d(temperature_, relative_humidity_):
        saturated_pressure = pv_sat(temperature_)
        actual_pressure = saturated_pressure*relative_humidity_

        return saturated_pressure - actual_pressure

    def f1(qr_sw_):
        return (a1 + qr_sw_)/(a2 + qr_sw_)

    def f2(d_):
        return 1 + a3*(d_ - d0)**2

    rs = rs_min*f1(qr_sw)*f2(d(temperature, relative_humidity))

    return rs


def pv_sat(temperature):
    """Calculated the saturated water vapour pressure of air at a given temperature
    :param temperature in C
    :return pv_sat in Pa
    """

    return 288.68*(1.098 + temperature/100)**8.02


def leaf_temperature(air_temperature, q_rad_leaf, q_lat_leaf, air_resistance):
    """
    Calculates the leaf temperature.
    :param air_temperature: temperature of the air in C
    :param q_rad_leaf: radiative heat flux of leaf W/m2
    :param q_lat_leaf: latent heat flux of leaf W/m2
    :param air_resistance: air resistance of leaf s/m
    :return: leaf temperature in C
    """

    rho = 1.225  # kg/m3
    cp = 1003.5  # J/kgK
    h_ch = 2*rho*cp/air_resistance
    t_leaf = air_temperature + (q_rad_leaf + q_lat_leaf)/h_ch

    return t_leaf
