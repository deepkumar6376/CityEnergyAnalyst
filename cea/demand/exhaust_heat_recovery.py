from __future__ import division
import numpy as np
from scipy.optimize import *
from min_exergy_cooling import calc_P_vapor
from cea.utilities import physics

## Evaporative cooling (adiabatic humidification)

def calc_w_sat(P_sat):
    w = P_sat/(1-P_sat)
    return w

def calc_h_vapor(T):
    Cp_vapor = 1.84  # kJ/kgC
    h_we = 2501  # kJ/kg
    h_vapor = Cp_vapor*T + h_we
    return h_vapor

def calc_h_moist_air(T, w):
    Cp_air = 1.006  # kJ/kgC
    Cp_vapor = 1.84  # kJ/kgC
    h_we = 2501  # kJ/kg
    h_vapor = Cp_vapor*T + h_we
    h_moist_air = Cp_air*T + w*h_vapor
    return h_moist_air


def function(z):
    x = z
    P_sat = calc_P_vapor(x)
    w_sat = calc_w_sat(P_sat)
    h_sat = calc_h_moist_air(x,w_sat)
    #F = np.empty((0))
    F = h_sat - h_1_sat
    return F



Cp_air = 1.006  # kJ/kgC
Cp_vapor = 1.84  # kJ/kgC
h_we = 2501  # kJ/kg



# P_1_sat = calc_P_vapor(T_1)
# w_1_sat = calc_w_sat(P_1_sat)
# h_1_sat = calc_h_moist_air(T_1, w_1_sat)


# zGuess = 1
# z = fsolve(function, zGuess)
# print z


# iteration to calculate T_wetbulb

def calc_T_wetbulb(rh, T_1):

    T_wetbulb = T_1-10
    E_d = 1

    es = 6.112 * np.exp((17.67*T_1)/(T_1+243.5))
    e = es*rh
    while abs(E_d) >= 0.05:
        E_wg = 6.112 * np.exp(17.67 * T_wetbulb / ( T_wetbulb + 243.5 ))
        eg = E_wg - 1013.25*(T_1-T_wetbulb)*0.00066*(1+(0.00115*T_wetbulb))
        E_d = e - eg
        T_wetbulb = T_wetbulb + 0.1

    w_wetbulb = physics.calc_w(T_wetbulb, 100)
    return T_wetbulb, w_wetbulb



def calc_T_hex_cold_out(T_hot_in, T_cold_in):
    dT = 2
    T_cold_out = T_cold_in + (T_hot_in-T_cold_in)/2 - dT/2
    T_hot_out = T_hot_in - (T_hot_in-T_cold_in)/2 + dT/2
    return T_cold_out, T_hot_out


# calculate temperature of adiabatic humidification
def calc_adiabatic_humidification(m_h2o_add, w_1, m_exhaust):
    #m_h2o_add = 0.002*100#kg/s
    Cp_air = 1.006  # kJ/kgC
    Cp_vapor = 1.84  # kJ/kgC
    h_we = 2501  # kJ/kg
    w_2 = w_1 + m_h2o_add/m_exhaust
    T_2 = (h_1 - w_2*h_we)/ (Cp_air+Cp_vapor*w_2)
    return w_2, T_2


# exchange sensible heat with ventilation air
T_outdoor = 30
w_outdoor = 0.021
h_outdoor = physics.calc_h(T_outdoor, w_outdoor)

m_exhaust = 100 #kg/s  # todo: get from cea
T_1 = 24 # todo: get from cea
w_1 = 0.011 # kg/kg dry air # todo: get from cea
h_1 = physics.calc_h(T_1, w_1)

T_wb_1, w_wb_1 = calc_T_wetbulb(0.6, T_1)
T_hex_1, T_hex_vent_1 = calc_T_hex_cold_out(T_outdoor, T_wb_1)
m_h2o_evaporate_1 = m_exhaust*(w_wb_1 - w_1)


# P_sat_hex_1 = calc_P_vapor(T_hex_1)
# w_sat_hex_1 = calc_w_sat(P_sat_hex_1)
# rh_2 = w_wb_1/w_sat_hex_1
# T_wb_2, w_wb_2 = calc_T_wetbulb(rh_2, T_hex_1)
# T_hex_2, T_hex_vent_2 = calc_T_hex_cold_out(T_hex_vent_1, T_wb_2)
# m_h2o_evaporate_2 = m_exhaust*(w_wb_2 - w_wb_1)

h_vent_recovered = physics.calc_h(T_hex_vent_1, w_outdoor)
Q_sen_recovery = m_exhaust*(h_outdoor - h_vent_recovered)

# print ("T_exhaust: ", T_1, "T_wb_1: ", T_wb_1, "T_hex_1: ", T_hex_1, "T_wb_2: ", T_wb_2, "T_hex_2:", T_hex_2)
# print ("w_exhaust: ", w_1, "w_wb_1: ", w_wb_1, "w_wb_2: ", w_wb_2)
# print ("m_h2o_evaporate:", m_h2o_evaporate_1+m_h2o_evaporate_2)
# print ("Q_sen_recovery")

print ("T_exhaust: ", T_1, "T_wb_1: ", T_wb_1, "T_hex_1: ", T_hex_1)
print ("w_exhaust: ", w_1, "w_wb_1: ", w_wb_1)
print ("T_outdoor: ", T_outdoor, "T_supply:", T_hex_vent_1)
print ("m_h2o_evaporate:", m_h2o_evaporate_1)
print ("Q_sen_recovery", Q_sen_recovery)