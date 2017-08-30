from __future__ import division
import os
import numpy as np
import pandas as pd
from cea.utilities import physics
import scipy.optimize
import math
from pulp import *

# Saturation pressures
def calc_P_vapor(T_C):
    A_antoine = 8.07131
    B_antoine = 1730.63
    C_antoine = 233.426
    P_vapor = 10**(A_antoine - B_antoine/(C_antoine + T_C))*0.001315
    return P_vapor  # mmHg

def calc_x_sat(P_sat, P_ambient):
    x_sat = P_sat / P_ambient
    return x_sat

def calc_m_moist(m_dry, w):
    m_moist = m_dry*(1+w)
    return m_moist

def calc_h_h2o(T): #TODO: check unit
    cp_h2o_vapor = 34.4 # kJ/kmol/C
    h_h2o = -18*327.6*(374-T)**0.3435 + cp_h2o_vapor*T
    return h_h2o


def calc_T_lm(T1, T2): #TODO: check reference
    T_lm = (T1 - T2)/(math.log(T1+273.15)- math.log(T2+273.15))
    return T_lm # K

def calc_T_sat(x, P_atm):
    A_antoine = 8.07131
    B_antoine = 1730.63
    C_antoine = 233.426
    p_H2O_mmHg = x*P_atm*760
    T_sat_C = B_antoine/(A_antoine - math.log(p_H2O_mmHg,10)) - C_antoine
    return T_sat_C

## PARAMETERS
# Outdoor air conditions
T_outdoor_C = 35
RH_outdoor = 75
w_outdoor = physics.calc_w(T_outdoor_C, RH_outdoor) # kg/kg dry air
P_sat_outdoor = calc_P_vapor(T_outdoor_C)
h_outdoor = physics.calc_h(T_outdoor_C, w_outdoor) # kJ/kg moist air
# T_outdoor_sat = physics.calc_t(w_outdoor, 100) # C #fixme: the function is wrong
T_outdoor_sat = calc_T_sat(w_outdoor/(1+w_outdoor), 1) #fixme: check equation, the result is too low
h_outdoor_sat = physics.calc_h(T_outdoor_sat, w_outdoor)
density_air_outdoor = physics.calc_rho_air(T_outdoor_C)  #kg/m3
T_lm_outdoor = calc_T_lm(T_outdoor_C+10, T_outdoor_C)  #K

# Indoor air set points
T_indoor_set_C = 24
RH_indoor = 50
w_indoor_set = physics.calc_w(T_indoor_set_C, RH_indoor)  # kg/kg dry air
#P_sat_indoor = calc_P_vapor(T_indoor_C)
#x_indoor_sat = calc_x_sat(P_sat_indoor, 1) # todo: change to kg/kg dry air

# Ventilation requirements  #TODO: get value from cea
V_zone_m3 = 550*3 # fixme: cea
air_change_rate = 1 # fixme: cea
infiltration_rate = 0.01 # fixme: cea
m_dot_requirement_dry = V_zone_m3* density_air_outdoor * air_change_rate/3600 # assume air change rate = 1 # kg/s #fixme: dry air
m_dot_infil_dry = V_zone_m3 * density_air_outdoor * infiltration_rate / 3600 #kg/s
m_dot_exfil_dry = m_dot_infil_dry #kg/s fixme: assumption

H_infil = m_dot_infil_dry * (1 + w_outdoor) * h_outdoor   # kJ/hr

# Sensible heat gains # TODO: get value from RC model
q_gain_sen = 2000 * 550 / 3600 # J/s # assumption, include sensible heat gain from radiation/convection/appliances/building thermal mass/ occupants
# Humidity gain # TODO: get value from CEA database
H2O_occupant = 100/3600 # g/s

eff_carnot = 0.55


## OPTIMIZATION PROBLEM
prob = LpProblem("problem", LpMinimize)

# VARIABLES
m_dot_vent_dry = LpVariable("m_dot_ventilation", 0, None)
w_vent_supply = LpVariable("w_vent_supply", 0, 1)
T_vent_supply = LpVariable("T_vent_supply", 5, 20)
w_indoor = LpVariable("w_indoor", 0, 1)


m_dot_exhaust_dry = LpVariable("m_dot_exhaust", 0, None)  # f(m_dot_vent_dry)
H_vent_supply = LpVariable("H_vent_supply", 0, None)   # f(m_dot_vent_dry)
m_H20_cond = LpVariable("m_H20_cond", 0, None)  # f(m_dot_vent_dry, w_outdoor, w_vent_supply)
H_exfil = LpVariable("m_H_exfil", 0, None) # f(m
H_exhaust = LpVariable("m_H_exhaust", 0, None)
Q_sen_vent = LpVariable("Q_sen_vent", 0, None)
Q_lat_vent = LpVariable("Q_lat_vent", 0, None)
T_lm_sen = LpVariable("T_lm_sen", 0, None)
T_lm_lat = LpVariable("T_lm_lat", 0, None)
E_carnot = LpVariable("E_carnot", 0, None)


# CONSTRAINTS
# inequality constraints
prob += m_dot_infil_dry + m_dot_vent_dry - m_dot_requirement_dry >= 0 # required amount of fresh air

# mass balance
#prob += calc_m_moist(m_dot_infil_dry, w_outdoor) + calc_m_moist(m_dot_vent_dry, w_vent_supply) -\
#        calc_m_moist(m_dot_exhaust_dry, w_indoor) - calc_m_moist(m_dot_exfil_dry, w_indoor) == 0 # mass balance of air #todo: check if it's necessary
# prob += m_dot_vent_dry*(w_outdoor - w_vent_supply) - m_H20_cond == 0 # water balance in ventilation air    #fixme:non-linear
prob += w_indoor - w_indoor_set <= 0 # indoor humidity requirement
prob += H2O_occupant + m_dot_infil_dry*w_outdoor + m_dot_vent_dry*w_vent_supply -\
        w_indoor*(m_dot_exfil_dry+m_dot_exhaust_dry) == 0 # water balance of room


# calculate enthalpy
prob += H_vent_supply - m_dot_vent_dry * (1 + w_vent_supply) * physics.calc_h(T_vent_supply, w_vent_supply) == 0 # calculate  H_vent_supply
prob += H_exfil - m_dot_exfil_dry * (1 + w_indoor) * physics.calc_h(T_indoor_set_C, w_indoor) == 0 # calculate H_exfil
prob += H_exhaust - m_dot_exhaust_dry * (1 + w_indoor) * physics.calc_h(T_indoor_set_C, w_indoor) == 0 # calculate H_exhaust
prob += T_vent_supply - physics.calc_t(w_vent_supply,100) == 0
prob += Q_sen_vent - (m_dot_vent_dry*(1+w_outdoor)*h_outdoor - m_dot_vent_dry*(1+w_outdoor)*h_outdoor_sat) == 0 # sensible heat removal from the ventilation air stream
prob += Q_lat_vent - (m_dot_vent_dry*(1+w_outdoor)*h_outdoor_sat - H_vent_supply - m_H20_cond * calc_h_h2o(T_vent_supply)) == 0 # condensation heat removal from the vent air stream


# energy balance
prob += q_gain_sen + H_vent_supply + H_infil - H_exfil - H_exhaust == 0  # energy balance of the room


# exergy requirement
prob += T_lm_sen - calc_T_lm(T_outdoor_C, T_outdoor_sat) == 0
prob += T_lm_lat - calc_T_lm(T_outdoor_sat, T_vent_supply) == 0
prob += E_carnot - (Q_sen_vent*((T_lm_outdoor-T_lm_sen)/T_lm_sen) + Q_lat_vent*(T_lm_outdoor - T_lm_lat)/T_lm_lat) == 0


# OBJECTIVE FUNCTION
prob += E_carnot/eff_carnot


# solve the problem
status = prob.solve(GLPK(msg=0))
LpStatus[status]





