"""
====================
Constraints checking
====================

Modifies an individual to comply with all constraints

"""
from __future__ import division

import numpy as np
import pandas as pd

import cea.optimization.supportFn as sFn

__author__ =  "Thuy-An Nguyen"
__copyright__ = "Copyright 2015, Architecture and Building Systems - ETH Zurich"
__credits__ = [ "Thuy-An Nguyen", "Tim Vollrath", "Jimeno A. Fonseca"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Daren Thomas"
__email__ = "thomas@arch.ethz.ch"
__status__ = "Production"

def putToRef(individual):
    """
    This function is to be used on a population with only ONE individual
    This function puts that individual to the reference, ie
    All buildings connected to the DHN
    Heating by a centralized peak boiler

    :param individual: list with variables included in each individual.
    :type individual: list

    :return: None
    :rtype: 'NoneType'
    """
    n = len( individual )
    index = 0
    while index < 21:
        individual[index] = 0
        index +=1
    while index < n:
        individual[index] = 1
        index +=1
    individual[4] = 1
    individual[5] = 1   


def GHPCheck(individual, locator, Qnom, settings):
    """
    This function computes the geothermal availability and modifies the individual to
    comply with it

    :param individual: list with variables included in each individual.
    :param locator: path to the demand folder
    :param Qnom: Nominal installed capacity in the district heating plant
    :param gv: Global Variables
    :type individual: list
    :type locator: string
    :type Qnom: float
    :type gv: class

    :return: None
    :rtype: NoneType
    """
    areaArray = np.array( pd.read_csv(locator.get_geothermal_potential(), usecols=["Area_geo"] ) )
    buildArray = np.array( pd.read_csv(locator.get_geothermal_potential(), usecols=["Name"] ) )
    
    buildList = sFn.extract_building_names_from_csv(locator.get_total_demand())
    barcode = sFn.individual_to_barcode(individual, settings)
    
    Qallowed = 0

    for index, buildName in zip(barcode, buildList):
        if index == "1":
            areaAvail = areaArray[ np.where(buildArray == buildName)[0][0] ][0]
            Qallowed += np.ceil(areaAvail/settings.GHP_A) * settings.GHP_HmaxSize #[W_th]

    GHP_share_index = len(settings.lower_bound) - len(settings.lower_bound_solar_technologies_shares) - 1
    GHP_activation_index = len(settings.lower_bound_conversion_technologies_activation) - 1
    if Qallowed < individual[GHP_share_index] * Qnom:
        print "GHP share modified !"
        
        if Qallowed < 1E-3:
            oldValue = individual[GHP_share_index]
            shareLoss = individual[GHP_share_index]
            individual[GHP_activation_index] =0
            individual[GHP_share_index] =0
        
        else:
            oldValue = individual[GHP_share_index]
            shareLoss = oldValue - Qallowed / Qnom
            individual[GHP_share_index] = Qallowed / Qnom
        
        # Adapt the other shares
        nPlant = 0
        for i in range(settings.nHeat - 1):
            if individual[i] > 0:
                nPlant += 1
                individual[settings.discrete_variables + i] += individual[settings.discrete_variables + i] * shareLoss / (1-oldValue)
        
    return individual