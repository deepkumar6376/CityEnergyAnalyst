from __future__ import division
from pyomo.environ import *
from cea.utilities import physics
import math


## Set-up model
model = ConcreteModel()

# Saturation pressures
def calc_P_vapor(T_C):
    A_antoine = 8.07131
    B_antoine = 1730.63
    C_antoine = 233.426
    P_vapor = 10**(A_antoine - B_antoine/(C_antoine + T_C))*0.001315
    return P_vapor  # atm

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
    T_lm = (T1 - T2)/(log(T1+273.15)- log(T2+273.15))
    return T_lm # K

def calc_T_sat(x, P_atm, math_flag):
    A_antoine = 8.07131
    B_antoine = 1730.63
    C_antoine = 233.426
    p_H2O_mmHg = x*P_atm*760
    if math_flag == True:
        T_sat_C = B_antoine/(A_antoine - math.log(p_H2O_mmHg,10)) - C_antoine
    else:
        T_sat_C = B_antoine / (A_antoine - log10(p_H2O_mmHg)) - C_antoine
    return T_sat_C


## PARAMETERS
# Outdoor air conditions
T_outdoor_C = 35
RH_outdoor = 75
w_outdoor = physics.calc_w(T_outdoor_C, RH_outdoor) # kg/kg dry air
P_sat_outdoor = calc_P_vapor(T_outdoor_C)
h_outdoor = physics.calc_h(T_outdoor_C, w_outdoor) # kJ/kg moist air
# T_outdoor_sat = physics.calc_t(w_outdoor, 100) # C #fixme: the function is wrong
T_outdoor_sat = calc_T_sat(w_outdoor/(1+w_outdoor), 1, True) #fixme: check equation, the result is too low
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
H2O_occupant = 100*4/3600 # g/s

eff_carnot = 0.55




# Variables
model.m_dot_vent_dry = Var(within=NonNegativeReals)
model.m_dot_exhaust_dry = Var(within=NonNegativeReals)
model.w_vent_supply = Var(within=NonNegativeReals, initialize = 0.002)
model.T_vent_supply = Var(within=NonNegativeReals, initialize = 16)
model.m_H2O_cond = Var(within=NonNegativeReals)
model.w_indoor = Var(within=NonNegativeReals)

model.H_vent_supply = Var(within=NonNegativeReals)
model.H_exfil = Var(within=NonNegativeReals)
model.H_exhaust = Var(within=NonNegativeReals)
model.Q_sen_vent = Var(within=NonNegativeReals)
model.Q_lat_vent = Var(within=NonNegativeReals)
model.T_lm_sen = Var(within=NonNegativeReals)
model.T_lm_lat = Var(within=NonNegativeReals)
model.E_carnot = Var(within=NonNegativeReals)



## Constraints
# required amount of fresh air
model.con1 = Constraint(expr = m_dot_infil_dry + model.m_dot_vent_dry - m_dot_requirement_dry >= 0)
# water balance in ventilation air
model.con2 = Constraint(expr = model.m_dot_vent_dry * ( -model.w_vent_supply + w_outdoor ) == model.m_H2O_cond )
# indoor humidity requirement
model.con3 = Constraint(expr = model.w_indoor - w_indoor_set <= 0)
# water balance of room
model.con4 = Constraint(expr = H2O_occupant + m_dot_infil_dry*w_outdoor + model.m_dot_vent_dry*model.w_vent_supply -\
                        model.w_indoor*(m_dot_exfil_dry+model.m_dot_exhaust_dry) == 0)
# enthalpy
model.con5 = Constraint(expr = model.H_vent_supply - (1 + model.w_vent_supply)* model.m_dot_vent_dry * physics.calc_h(model.T_vent_supply, model.w_vent_supply) == 0)
model.con6 = Constraint(expr = model.H_exfil - m_dot_exfil_dry * (1 + model.w_indoor) * physics.calc_h(T_indoor_set_C, model.w_indoor) == 0)
model.con7 = Constraint(expr = model.H_exhaust - model.m_dot_exhaust_dry * (1 + model.w_indoor) * physics.calc_h(T_indoor_set_C, model.w_indoor) == 0)
# cooling energy
model.con8 = Constraint(expr = model.T_vent_supply - calc_T_sat(model.w_vent_supply/(1+model.w_vent_supply), 1, False) == 0) #fixme:change
model.con9 = Constraint(expr = model.Q_sen_vent - (model.m_dot_vent_dry*(1+w_outdoor)*h_outdoor - model.m_dot_vent_dry*(1+w_outdoor)*h_outdoor_sat) == 0)
model.con10 = Constraint(expr = model.Q_lat_vent - (model.m_dot_vent_dry*(1+w_outdoor)*h_outdoor_sat
                                                    - model.H_vent_supply - model.m_H2O_cond * calc_h_h2o(model.T_vent_supply)) == 0)

# energy balance of the room
model.con11 = Constraint(expr = q_gain_sen + model.H_vent_supply + H_infil - model.H_exfil - model.H_exhaust == 0)

# exergy requirement
model.con12 = Constraint(expr = model.T_lm_sen - calc_T_lm(T_outdoor_C, T_outdoor_sat) == 0)
model.con13 = Constraint(expr = model.T_lm_lat - calc_T_lm(T_outdoor_sat, model.T_vent_supply) == 0)
model.con14 = Constraint(expr = model.E_carnot - (model.Q_sen_vent*((T_lm_outdoor-model.T_lm_sen)/model.T_lm_sen) + model.Q_lat_vent*(T_lm_outdoor - model.T_lm_lat)/model.T_lm_lat) == 0)

# dry air balance
model.con15 = Constraint(expr = model.m_dot_vent_dry + m_dot_infil_dry - model.m_dot_exhaust_dry - m_dot_exfil_dry == 0)


# OBJECTIVE FUNCTION
model.OBJ = Objective(expr = model.E_carnot/eff_carnot)