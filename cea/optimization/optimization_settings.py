
from __future__ import absolute_import

__author__ = "Sreepathi Bhargava Krishna"
__copyright__ = "Copyright 2017, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Sreepathi Bhargava Krishna"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"


class optimization_settings(object):
    def __init__(self):

        self.initialInd = 2  # number of initial individuals
        self.NGEN = 5  # number of total generations
        self.TLS = self.initialInd  # Tabu List size
        self.TR = 0.01  # Tabu Radius
        self.fCheckPoint = 1  # frequency for the saving of checkpoints
        self.maxTime = 7 * 24 * 3600  # maximum computational time [seconds]



        # Set Flags for different system setup preferences

        # self.NetworkLengthZernez = 864.0 #meters network length of maximum network, \
        # then scaled by number of costumers (Zernez Specific), from J.Fonseca's Pipes Data

        self.ZernezFlag = 0
        self.FlagBioGasFromAgriculture = 0  # 1 = Biogas from Agriculture, 0 = Biogas normal
        self.HPSew_allowed = 1
        self.HPLake_allowed = 1
        self.GHP_allowed = 1
        self.CC_allowed = 1
        self.Furnace_allowed = 0
        self.DiscGHPFlag = 1  # Is geothermal allowed in disconnected buildings? 0 = NO ; 1 = YES
        self.DiscBioGasFlag = 0  # 1 = use Biogas only in Disconnected Buildings, no Natural Gas; 0so = both possible

        # Losses and margins
        self.DCNetworkLoss = 0.05  # Cooling ntw losses (10% --> 0.1)
        self.DHNetworkLoss = 0.12  # Heating ntw losses
        self.Qmargin_ntw = 0.01  # Reliability margin for the system nominal capacity in the hub
        self.Qloss_Disc = 0.05  # Heat losses within a disconnected building
        self.Qmargin_Disc = 0.20  # Reliability margin for the system nominal capacity for decentralized systems
        self.QminShare = 0.10  # Minimum percentage for the installed capacity
        self.K_DH = 0.25  # linear heat loss coefficient district heting network twin pipes groundfoss
        self.roughness = 0.02/1000 # roughness coefficient for heating network pipe in m (for a steel pipe, from Li &
                           # Svendsen (2012) "Energy and exergy analysis of low temperature district heating network")

        # Financial Data
        self.EURO_TO_CHF = 1.2
        self.CHF_TO_EURO = 1.0 / self.EURO_TO_CHF
        self.USD_TO_CHF = 0.96
        self.MWST = 0.08  # 8% MWST assumed, used in A+W data

        # Pressure losses
        # self.DeltaP_DCN = 1.0 #Pa - change
        # self.DeltaP_DHN = 84.8E3 / 10.0 #Pa  - change

        self.PumpEnergyShare = 0.01  # assume 1% of energy required for pumping, after 4DH
        self.PumpReliabilityMargin = 0.05  # assume 5% reliability margin

        # Circulating Pump
        self.etaPump = 0.8

        # Heat Exchangers
        self.U_cool = 2500  # W/m2K
        self.U_heat = 2500  # W/m2K
        self.dT_heat = 5  # K - pinch delta at design conditions
        self.dT_cool = 1  # K - pinch delta at design conditions

        # Heat pump
        self.HP_maxSize = 20.0E6  # max thermal design size [Wth]
        self.HP_minSize = 1.0E6  # min thermal design size [Wth]

        self.HP_etaex = 0.6  # exergetic efficiency of WSHP [L. Girardin et al., 2010]_
        self.HP_deltaT_cond = 2.0  # pinch for condenser [K]
        self.HP_deltaT_evap = 2.0  # pinch for evaporator [K]
        self.HP_maxT_cond = 140 + 273.0  # max temperature at condenser [K]

        self.HP_Auxratio = 0.83  # Wdot_comp / Wdot_total (circulating pumps)

        # Sewage resource

        self.Sew_minT = 10 + 273.0  # minimum temperature at the sewage exit [K]

        # Lake resources
        self.DeltaU = 12500.0E6  # [Wh], maximum change in the lake energy content at the end of the year (positive or negative)
        self.TLake = 5 + 273.0  # K

        # Geothermal heat pump

        self.TGround = 6.5 + 273.0

        self.COPScalingFactorGroundWater = 3.4 / 3.9  # Scaling factor according to EcoBau, take GroundWater Heat pump into account

        self.GHP_CmaxSize = 2E3  # max cooling design size [Wc] FOR ONE PROBE
        self.GHP_Cmax_Size_th = 2E3  # Wh/m per probe
        self.GHP_Cmax_Length = 40  # depth of exploration taken into account

        self.GHP_HmaxSize = 2E3  # max heating design size [Wth] FOR ONE PROBE
        self.GHP_WmaxSize = 1E3  # max electrical design size [Wel] FOR ONE PROBE

        self.GHP_nBH = 50.0  # [years] for a borehole

        self.GHP_etaex = 0.677  # exergetic efficiency [O. Ozgener et al., 2005]_
        self.GHP_Auxratio = 0.83  # Wdot_comp / Wdot_total (circulating pumps)

        self.GHP_i = 0.06  # interest rate
        self.GHP_A = 25  # [m^2] area occupancy of one borehole Gultekin et al. 5 m separation at a penalty of 10% less efficeincy

        # Combined cycle

        self.CC_i = 0.06

        self.GT_maxSize = 50.00000001E6  # max electrical design size in W = 50MW (NOT THERMAL capacity)
        self.GT_minSize = 0.2E6  # min electrical design size in W = 0.2 MW (NOT THERMAL capacity)
        self.GT_minload = 0.1 * 0.999  # min load (part load regime)

        self.CC_exitT_NG = 986.0  # exit temperature of the gas turbine if NG
        self.CC_exitT_BG = 1053.0  # exit temperature of the gas turbine if BG
        self.CC_airratio = 2.0  # air to fuel mass ratio

        self.ST_deltaT = 4.0  # pinch for HRSG
        self.ST_deltaP = 5.0E5  # pressure loss between steam turbine and DHN
        self.CC_deltaT_DH = 5.0  # pinch for condenser


        # Activation Order of Power Plants
        # solar sources are treated first
        self.act_first = 'HP'  # accounts for all kind of HP's as only one will be in the system.
        self.act_second = 'CHP'  # accounts for ORC and NG-RC (produce electricity!)
        self.act_third = 'BoilerBase'  # all conventional boilers are considered to be backups.
        self.act_fourth = 'BoilerPeak'  # additional Peak Boiler

        # Data for Evolutionary algorithm
        self.nHeat = 6  # number of heating
        self.nHR = 2 # number of heat recovery options
        self.nSolar = 3 # number of solar technologies

        self.PROBA = 0.5
        self.SIGMAP = 0.2
        self.epsMargin = 0.001

        #  BOunds for optimization
        self.nBuildings = 24
        self.lower_bound_conversion_technologies_activation = [0] * (self.nHeat)  # discrete variables
        #  the order of technologies is CHP/Furnace, Base Boiler, Peak Boiler, HP Lake, HP Sewage, GHP
        self.upper_bound_conversion_technologies_activation = [4, 2, 2, 1, 1, 1]  # discrete variables
        self.lower_bound_heat_recovery = [0] * (self.nHR)  # only ON or OFF, discrete variables
        self.upper_bound_heat_recovery = [1] * (self.nHR)  # discrete variables
        self.lower_bound_solar_technologies_activation = [0] * (self.nSolar)  # discrete variables
        #  the order of technologies is PV, PVT, SC
        self.upper_bound_solar_technologies_activation = [1] * (self.nSolar)  # discrete variables
        self.lower_bound_buildings = [0] * (self.nBuildings)  # discrete variables
        self.upper_bound_buildings = [1] * (self.nBuildings)  # discrete variables
        self.discrete_variables = self.nHeat + self.nHR + self.nSolar + self.nBuildings

        self.lower_bound_conversion_technologies_shares = [0] * (self.nHeat)  # continuous variables
        self.upper_bound_conversion_technologies_shares = [1] * (self.nHeat)  # continuous variables
        self.lower_bound_solar_technologies_shares = [0] * (self.nSolar + 1)  # continuous variables
        self.upper_bound_solar_technologies_shares = [1] * (self.nSolar + 1)  # continuous variables

        self.lower_bound = self.lower_bound_conversion_technologies_activation + self.lower_bound_heat_recovery + \
                           self.lower_bound_solar_technologies_activation + self.lower_bound_buildings +\
                           self.lower_bound_conversion_technologies_shares + self.lower_bound_solar_technologies_shares

        self.upper_bound = self.upper_bound_conversion_technologies_activation + self.upper_bound_heat_recovery + \
                           self.upper_bound_solar_technologies_activation + self.upper_bound_buildings +\
                           self.upper_bound_conversion_technologies_shares + self.upper_bound_solar_technologies_shares

