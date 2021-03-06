# -*- coding: utf-8 -*-
"""
Sewage source heat exchanger
"""
from __future__ import division
import pandas as pd
import numpy as np
import scipy

__author__ = "Jimeno A. Fonseca"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"



def calc_sewage_heat_exchanger(locator, Length_HEX_available, gv):
    """
    Calaculate the heat extracted from the sewage HEX.

    :param locator: an InputLocator instance set to the scenario to work on
    :param Length_HEX_available: HEX length available
    :type Length_HEX_available: float
    :param gv: globalvar.py

    Save the results to `SWP.csv`
    """

    # local variables
    mcpwaste = []
    twaste = []
    mXt = []
    counter = 0
    names = pd.read_csv(locator.get_total_demand()).Name.count()

    for x in names:
        building = pd.read_csv(locator.get_demand_results_file(x))
        m, t = np.vectorize(calc_Sewagetemperature)( building.Qwwf_kWh, building.Qww_kWh, building.Tsww_C,
                                                     building.Trww_C, building.totwater, building.mcpww_kWC, gv.Cpw,
                                                     gv.Pwater, gv.SW_ratio)
        mcpwaste.append(m)
        twaste.append(t)
        mXt.append(m*t)
        counter = counter +1
    mcpwaste_zone = np.sum( mcpwaste, axis =0)
    twaste_zone = np.sum( mXt, axis =0) / mcpwaste_zone
    twaste_zone = twaste_zone.copy() - twaste_zone.copy() * 0.20 # lossess in the grid

    Q_source, t_source, t_out, tin_e, tout_e  = np.vectorize(calc_sewageheat)( mcpwaste_zone, twaste_zone, gv.width_HEX,
                                                                               gv.Vel_flow, gv.Cpw, gv.h0, gv.min_flow,
                                                                               Length_HEX_available, gv.tmin, gv.ATmin)
    SW_gen = locator.get_sewage_heat_potential()
    pd.DataFrame( { "Qsw_kW" : Q_source, "ts_C" : t_source, "tout_sw_C" : t_out, "tin_sw_C" : twaste_zone,
                    "tout_HP_C" : tout_e, "tin_HP_C" : tin_e}).to_csv( SW_gen, index=False, float_format='%.3f')



# Calc Sewage heat

def calc_Sewagetemperature( Qwwf, Qww, tsww, trww, totwater, mcpww, cp, density, SW_ratio):
    """
    Calculate sewage temperature and flow rate released from DHW usages and Fresh Water (FW) in buildings.

    :param Qwwf: final DHW heat requirement
    :type Qwwf: float
    :param Qww: DHW heat requirement
    :type Qww: float
    :param tsww: DHW supply temperature
    :type tsww: float
    :param trww: DHW return temperature
    :type trww: float
    :param totwater: fresh water flow rate
    :type totwater: float
    :param mcpww: DHW heat capacity
    :type mcpww: float
    :param cp: water specific heat capacity
    :type cp: float
    :param density: water density
    :type densigy: float
    :param SW_ratio: ratio of waste water to fresh water production.
    :type SW_ratio: float

    :returns mcp_combi: sewage water heat capacity [kWh/K]
    :rtype mcp_combi: float
    :returns t_to_sewage: sewage water temperature
    :rtype t_to_sewage: float
    """

    if Qwwf > 0:
        Qloss_to_spur = Qwwf - Qww
        t_spur = tsww - Qloss_to_spur / mcpww
        m_DHW = mcpww * SW_ratio # in [kWh/K]
        m_FW = totwater * SW_ratio * 0.5 * cp * density / 3600  # in [kWh/K]
        mcp_combi = m_DHW + m_FW
        t_combi = ( m_DHW * t_spur + m_FW * trww ) / mcp_combi
        t_to_sewage = 0.90 * t_combi                  # assuming 10% thermal loss throuhg piping
    else:
        t_to_sewage = trww
        mcp_combi = totwater * SW_ratio * 0.5 * cp * density / 3600 # in [kWh/K]
    return mcp_combi, t_to_sewage # in lh or kgh and in C

def calc_sewageheat( mcp, tin, w_HEX, Vf, cp, h0, min_m, L_HEX, tmin, ATmin):
    """
    Calculates the operation of sewage heat exchanger.

    :param mcp: heat capacity of total sewage in a zone
    :type mcp: float
    :param tin: sewage inlet temperature of a zone
    :type tin: float
    :param w_HEX: width of the sewage HEX
    :type w_HEX: float
    :param Vf: sewage flow rate [m/s]
    :type Vf: float
    :param cp: water specific heat capacity
    :type cp: float
    :param h0: sewage heat transfer coefficient
    :type h0: float
    :param min_m: sewage minimum flow rate in [lps]
    :type min_m: float
    :param L_HEX: HEX length available
    :type L_HEX: float
    :param tmin: minimum temperature of extraction
    :type tmin: float
    :param ATmin: minimum area of heat exchange
    :type ATmin: float

    :returns Q_source: heat supplied by sewage
    :rtype: float
    :returns t_source: sewage heat supply temperature
    :rtype t_source: float
    :returns tb2: sewage return temperature
    :rtype tbs: float
    :returns ta1: temperature inlet of the cold stream (from the HP)
    :rtype ta1: float
    :returns ta2: temperature outlet of the cold stream (to the HP)
    :rtype ta2: float

    ..[J.A. Fonseca et al., 2016] J.A. Fonseca, Thuy-An Nguyen, Arno Schlueter, Francois Marechal (2016). City Enegy
    Analyst (CEA): Integrated framework for analysis and optimization of building energy systems in neighborhoods and
    city districts. Energy and Buildings.
    """

    mcp_min = min_m * cp # minimum sewage heat capacity in [kW/K]
    mcp_max = Vf * w_HEX * 0.20 * 1000 * cp   # 20 cm is the depth of the active water in contact with the HEX
    A_HEX = w_HEX * L_HEX   # area of heat exchange
    if mcp > mcp_max:
        mcp = mcp_max
    if mcp_min < mcp <= mcp_max:
        # B is the sewage, A is the heat pump
        mcpa = mcp * 1.1 # the flow in the heat pumps slightly above the flow on the sewage side
        tb1 = tin
        ta1 = tin - ( ( tin - tmin ) + ATmin / 2 )
        alpha = h0 * A_HEX * ( 1 / mcpa - 1 / mcp )
        n = ( 1 - scipy.exp( -alpha ) ) / ( 1 - mcpa / mcp * scipy.exp( -alpha ) )
        tb2 = tb1 + mcpa / mcp * n * ( ta1 - tb1 )
        Q_source = mcp * ( tb1 - tb2 )
        ta2 = ta1 + Q_source / mcpa
        t_source = ( tb2 + tb1 )
    else:
        tb1 = tin
        tb2 = tin
        ta1 = tin
        ta2 = tin
        Q_source = 0
        t_source = tin

    return Q_source, t_source, tb2, ta1, ta2


def test_ss_heatpump():
    import cea.inputlocator
    import cea.globalvar
    locator = cea.inputlocator.InputLocator(r'C:\reference-case\baseline')
    gv = cea.globalvar.GlobalVariables()

    Length_HEX_available = 120  # 120:CAMP, 210:HEB  #measured from arcpmap

    calc_sewage_heat_exchanger(locator=locator, Length_HEX_available=Length_HEX_available, gv=gv)


if __name__ == '__main__':
    test_ss_heatpump()