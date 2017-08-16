from __future__ import division
import os
import numpy as np
import pandas as pd
from cea.utilities import physics
import scipy.optimize
import math


# Outdoor air conditions
T_outdoor_C = 35
RH_outdoor = 0.75
x_outdoor = physics.calc_h(T_outdoor_C, RH_outdoor)
# Indoor air set points
T_indoor_C = 24
RH_indoor = 0.5
x_indoor = physics.calc_h(T_indoor_C, RH_indoor)


# Ventilation requirements  #TODO: get value from cea
V_zone_m3 = 550*3 # 3for2 office site
m_dot_requirement = V_zone_m3*1 # assume air change rate = 1
m_dot_infiltration = V_zone_m3*0.01 # assumption
m_dot_exfiltration = m_dot_infiltration
# variables
# m_dot_ventilation = m_dot_requirement - m_dot_infiltration
# m_dot_exhaust = m_dot_ventilation

# sensible heat gains # TODO: get value from RC model
q_sen_gain_Wh = 2000 * 550 # assumption, include sensible heat gain from radiation/convection/appliances/building thermal mass/ occupants
# water gain # TODO: get value from CEA database
H2O_occupant_gperhr = 100




def calc_T_sat(x, P_atm):
    A_antoine = 8.07131
    B_antoine = 1730.63
    C_antoine = 233.426
    p_H2O_mmHg = x*P_atm*760
    T_sat_C = B_antoine/(A_antoine - math.log(p_H2O_mmHg,10)) - C_antoine
    return T_sat_C