
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

        self.initialInd = 10  # number of initial individuals
        self.NGEN = 50  # number of total generations
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
        self.lower_bound = [0] * ((self.nHeat + self.nSolar) * 2 + self.nHR + self.nBuildings + 1)
        self.upper_bound = [4, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]